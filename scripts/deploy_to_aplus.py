#!/usr/bin/env python3
"""Deploy the static CellNucleus site to an Aplus-hosted FTP target."""

from __future__ import annotations

import argparse
import os
import posixpath
import re
import socket
import xml.etree.ElementTree as ET
from contextlib import suppress
from ftplib import FTP, FTP_TLS, all_errors
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse

from aplus_secrets import load_aplus_secrets

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".github",
    ".secrets",
    "backup",
    "docs",
    "inbox",
    "jobs",
    "output",
    "reports",
    "scripts",
    "skills",
    "taskforce_submissions",
    "__pycache__",
}
PUBLIC_EXTENSIONS = {
    ".css",
    ".docx",
    ".eot",
    ".gif",
    ".htaccess",
    ".htm",
    ".html",
    ".ico",
    ".jpeg",
    ".jpg",
    ".js",
    ".mov",
    ".mp4",
    ".pdf",
    ".php",
    ".phtml",
    ".png",
    ".svg",
    ".ttf",
    ".txt",
    ".webm",
    ".webp",
    ".woff",
    ".woff2",
    ".xml",
}
PUBLIC_BASENAMES = {"robots.txt"}
VIDEO_EXTENSIONS = {".mov", ".mp4", ".webm"}
SAFE_REMOTE_DIR = "public"
DANGEROUS_REMOTE_DIRS = {
    "",
    ".",
    "/",
    "public_html",
    "secure",
    "wwww",
    "www",
    "cgi-bin",
    "databases",
    "db",
    "private",
}
START_FILES = {"index.html", "sitemap.xml", "robots.txt"}
LINK_ATTRS = {"href", "src", "action", "poster"}
CSS_URL_RE = re.compile(r"url\((['\"]?)(.*?)\1\)", re.IGNORECASE)
TEXT_LOCAL_REF_RE = re.compile(
    r"['\"]([^'\"]+\.(?:css|gif|html?|ico|jpe?g|js|mov|mp4|pdf|php|png|svg|txt|webm|webp|xml))['\"]",
    re.IGNORECASE,
)


class PublishLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key and key.lower() in LINK_ATTRS and value:
                self.refs.append(value)


def normalize_remote_dir(remote_dir: str) -> str:
    return remote_dir.replace("\\", "/").strip("/")


def validate_remote_dir(remote_dir: str) -> str:
    normalized = normalize_remote_dir(remote_dir)
    if normalized in {"cellnucleus.com", "cellnucleus.com/public"}:
        normalized = SAFE_REMOTE_DIR
    if normalized.lower() in DANGEROUS_REMOTE_DIRS:
        raise SystemExit(
            f"Refusing to deploy to FTP root/server folder {remote_dir!r}; "
            f"expected {SAFE_REMOTE_DIR!r}."
        )
    if normalized != SAFE_REMOTE_DIR:
        raise SystemExit(
            f"Refusing to deploy to {remote_dir!r}; this script is scoped to "
            f"{SAFE_REMOTE_DIR!r} so sibling domains and databases are not touched."
        )
    return normalized


def iter_publishable_files() -> Iterable[Path]:
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if any(part.startswith(".") for part in rel.parts[:-1]):
            continue
        if path.name.startswith(".") and path.name != ".htaccess":
            continue
        if path.name in PUBLIC_BASENAMES or path.suffix.lower() in PUBLIC_EXTENSIONS:
            yield rel


def is_publishable_rel(rel: Path) -> bool:
    if any(part in SKIP_DIRS for part in rel.parts):
        return False
    if any(part.startswith(".") for part in rel.parts[:-1]):
        return False
    if rel.name.startswith(".") and rel.name != ".htaccess":
        return False
    return rel.name in PUBLIC_BASENAMES or rel.suffix.lower() in PUBLIC_EXTENSIONS


def resolve_local_reference(base_rel: Path, ref: str) -> Path | None:
    if not ref or ref.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlparse(ref)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    candidate = (ROOT / path.lstrip("/")) if path.startswith("/") else (ROOT / base_rel.parent / path)
    try:
        rel = candidate.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return None
    if rel == Path(".") or not (ROOT / rel).is_file():
        return None
    if not is_publishable_rel(rel):
        return None
    return rel


def refs_from_html(path: Path) -> list[str]:
    parser = PublishLinkParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return parser.refs


def refs_from_css(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [match.group(2).strip() for match in CSS_URL_RE.finditer(text)]


def refs_from_text(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [match.group(1) for match in TEXT_LOCAL_REF_RE.finditer(text)]


def start_files_from_sitemap() -> set[Path]:
    sitemap = ROOT / "sitemap.xml"
    starts = {Path(name) for name in START_FILES if (ROOT / name).is_file()}
    if not sitemap.is_file():
        return starts
    try:
        document = ET.parse(sitemap)
    except ET.ParseError:
        return starts
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for loc in document.findall(".//sm:loc", namespace):
        if not loc.text:
            continue
        parsed = urlparse(loc.text.strip())
        if parsed.netloc and parsed.netloc not in {"cellnucleus.com", "www.cellnucleus.com"}:
            continue
        path = parsed.path.strip("/") or "index.html"
        if path.endswith("/"):
            path += "index.html"
        rel = Path(path)
        if (ROOT / rel).is_file() and is_publishable_rel(rel):
            starts.add(rel)
    return starts


def iter_linked_publishable_files() -> Iterable[Path]:
    queue = sorted(start_files_from_sitemap(), key=lambda p: p.as_posix())
    seen: set[Path] = set()
    included: set[Path] = set()

    while queue:
        rel = queue.pop(0)
        if rel in seen:
            continue
        seen.add(rel)
        path = ROOT / rel
        if not path.is_file() or not is_publishable_rel(rel):
            continue
        included.add(rel)

        suffix = rel.suffix.lower()
        refs: list[str] = []
        if suffix in {".html", ".htm", ".php", ".phtml"}:
            refs.extend(refs_from_html(path))
        if suffix == ".css":
            refs.extend(refs_from_css(path))
        if suffix == ".js":
            refs.extend(refs_from_text(path))

        for ref in refs:
            target = resolve_local_reference(rel, ref)
            if target and target not in seen:
                queue.append(target)

    for rel in sorted(included):
        yield rel


def select_publishable_files(linked_only: bool, include_videos: bool = False) -> list[Path]:
    if linked_only:
        files = list(iter_linked_publishable_files())
    else:
        files = list(iter_publishable_files())
    if not include_videos:
        files = [rel for rel in files if rel.suffix.lower() not in VIDEO_EXTENSIONS]
    return files


def iter_publishable_dirs(files: Iterable[Path]) -> list[str]:
    dirs = {rel.parent.as_posix() for rel in files if rel.parent.as_posix() != "."}
    return sorted(dirs)


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def connect_ftp(host: str, port: int, username: str, password: str, secure_mode: str) -> FTP:
    modes: list[bool]
    secure_mode = secure_mode.strip().lower()
    if secure_mode == "auto":
        modes = [True, False]
    elif truthy(secure_mode):
        modes = [True]
    else:
        modes = [False]

    last_error: Exception | None = None
    for secure in modes:
        try:
            ftp: FTP
            if secure:
                ftp = FTP_TLS(timeout=30)
            else:
                ftp = FTP(timeout=30)
            ftp.connect(host, port, timeout=30)
            ftp.login(username, password)
            if secure and isinstance(ftp, FTP_TLS):
                ftp.prot_p()
            ftp.set_pasv(True)
            return ftp
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(f"Unable to connect to FTP host {host}:{port}") from last_error


def list_root_entries(ftp: FTP) -> list[str]:
    entries: list[str] = []
    with suppress(all_errors):
        ftp.retrlines("NLST", entries.append)
    return sorted(entry.rstrip("/") for entry in entries if entry)


def cwd_or_fail(ftp: FTP, remote_dir: str) -> None:
    ftp.cwd("/")
    normalized = remote_dir.strip("/")
    if not normalized:
        return
    for part in normalized.split("/"):
        ftp.cwd(part)


def ensure_remote_dirs(ftp: FTP, relative_dir: str) -> None:
    if not relative_dir:
        return
    current = ftp.pwd()
    try:
        for part in relative_dir.split("/"):
            with suppress(all_errors):
                ftp.mkd(part)
            ftp.cwd(part)
    finally:
        ftp.cwd(current)


def ensure_remote_tree(ftp: FTP, dirs: Iterable[str]) -> int:
    created_or_verified = 0
    for remote_dir in dirs:
        ensure_remote_dirs(ftp, remote_dir)
        created_or_verified += 1
    return created_or_verified


def archive_remote_index(ftp: FTP) -> str | None:
    with suppress(all_errors):
        ftp.size("index.phtml")
        backup_name = "index.phtml.bak"
        counter = 1
        while True:
            candidate = f"{backup_name}.{counter}"
            try:
                ftp.rename("index.phtml", candidate)
                return candidate
            except all_errors:
                counter += 1
    return None


def upload_file(ftp: FTP, local_rel: Path) -> None:
    remote_dir = local_rel.parent.as_posix()
    ensure_remote_dirs(ftp, remote_dir)
    local_path = ROOT / local_rel
    remote_name = local_rel.name
    current = ftp.pwd()
    try:
        if remote_dir and remote_dir != ".":
            ftp.cwd(posixpath.join(current, remote_dir))
        with local_path.open("rb") as handle:
            ftp.storbinary(f"STOR {remote_name}", handle)
    finally:
        ftp.cwd(current)


def remote_size_matches(ftp: FTP, local_rel: Path) -> bool:
    remote_dir = local_rel.parent.as_posix()
    local_path = ROOT / local_rel
    current = ftp.pwd()
    try:
        if remote_dir and remote_dir != ".":
            ftp.cwd(posixpath.join(current, remote_dir))
        with suppress(all_errors):
            return ftp.size(local_rel.name) == local_path.stat().st_size
        return False
    finally:
        ftp.cwd(current)


def build_remote_size_index(ftp: FTP, dirs: Iterable[str]) -> dict[str, int]:
    current = ftp.pwd()
    size_index: dict[str, int] = {}
    for remote_dir in ["", *dirs]:
        try:
            ftp.cwd(current)
            if remote_dir:
                ftp.cwd(posixpath.join(current, remote_dir))
            for name, facts in ftp.mlsd():
                if facts.get("type") != "file" or "size" not in facts:
                    continue
                remote_rel = posixpath.join(remote_dir, name) if remote_dir else name
                size_index[remote_rel] = int(facts["size"])
        except all_errors:
            continue
    ftp.cwd(current)
    return size_index


def indexed_remote_size_matches(remote_sizes: dict[str, int], local_rel: Path) -> bool:
    local_path = ROOT / local_rel
    return remote_sizes.get(local_rel.as_posix()) == local_path.stat().st_size


def deploy(args: argparse.Namespace) -> None:
    secrets = load_aplus_secrets(args.env_path)
    username = args.username or secrets.get("APLUS_FTP_USERNAME") or secrets.get("APLUS_USERNAME", "")
    password = args.password or secrets.get("APLUS_PASSWORD", "")
    host = args.host or secrets.get("APLUS_FTP_HOST", "ftp.cellnucleus.com")
    port = int(args.port or secrets.get("APLUS_FTP_PORT", "21"))
    secure = args.secure or secrets.get("APLUS_FTP_SECURE", "auto")
    remote_dir = validate_remote_dir(args.remote_dir or secrets.get("APLUS_REMOTE_DIR", SAFE_REMOTE_DIR))

    if not username or not password:
        raise SystemExit("Missing Aplus username or password in .secrets/.env")

    files = select_publishable_files(not args.all_public_files, args.include_videos)
    if args.skip:
        files = files[args.skip :]
    if args.limit:
        files = files[: args.limit]

    ftp = connect_ftp(host, port, username, password, secure)
    try:
        root_entries = list_root_entries(ftp)
        print(f"Connected to {host}:{port}", flush=True)
        print(f"Remote root entries: {len(root_entries)}", flush=True)
        for entry in root_entries[:50]:
            print(f"- {entry}", flush=True)
        if args.inspect:
            return

        cwd_or_fail(ftp, remote_dir)
        print(f"Deploy target: {ftp.pwd()}", flush=True)
        print("Safety mode: no remote deletion; sibling FTP root folders are not modified.", flush=True)

        dirs = iter_publishable_dirs(files)
        if args.create_dirs_only:
            count = ensure_remote_tree(ftp, dirs)
            print(f"Created/verified {count} publishable directories under {remote_dir}.", flush=True)
            return

        archived = archive_remote_index(ftp)
        if archived:
            print(f"Archived remote index.phtml -> {archived}", flush=True)

        if args.dry_run:
            mode = "linked/reachable" if not args.all_public_files else "all public-looking"
            if not args.include_videos:
                mode += ", excluding video binaries"
            print(f"Dry run only. Would upload {len(files)} {mode} files.")
            print(f"Would create/verify {len(dirs)} directories.")
            for rel in files[:50]:
                print(f"- {rel.as_posix()}")
            return

        count = ensure_remote_tree(ftp, dirs)
        print(f"Created/verified {count} publishable directories.", flush=True)
        remote_sizes = build_remote_size_index(ftp, dirs)
        print(f"Indexed {len(remote_sizes)} existing remote files for same-size resume checks.", flush=True)

        uploaded = 0
        skipped = 0
        for rel in files:
            if not args.force and indexed_remote_size_matches(remote_sizes, rel):
                skipped += 1
                if (uploaded + skipped) % 25 == 0 or (uploaded + skipped) == len(files):
                    print(f"Checked {uploaded + skipped}/{len(files)}; uploaded {uploaded}, skipped {skipped}", flush=True)
                continue
            upload_file(ftp, rel)
            uploaded += 1
            if (uploaded + skipped) % 25 == 0 or (uploaded + skipped) == len(files):
                print(f"Checked {uploaded + skipped}/{len(files)}; uploaded {uploaded}, skipped {skipped}", flush=True)
        print(f"Deployment complete. Uploaded {uploaded} files, skipped {skipped} same-size files to {remote_dir}.", flush=True)
    finally:
        with suppress(Exception):
            ftp.quit()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-path", type=Path, default=ROOT / ".secrets" / ".env")
    parser.add_argument("--host", help="Override FTP host")
    parser.add_argument("--port", type=int, help="Override FTP port")
    parser.add_argument("--username", help="Override FTP username")
    parser.add_argument("--password", help="Override FTP password")
    parser.add_argument("--secure", help="Override FTP secure mode: true, false, or auto")
    parser.add_argument("--remote-dir", help="Remote directory for the cellnucleus.com site")
    parser.add_argument("--inspect", action="store_true", help="Only connect and list remote root entries")
    parser.add_argument("--dry-run", action="store_true", help="List the upload set without transferring files")
    parser.add_argument(
        "--create-dirs-only",
        action="store_true",
        help="Create/verify the publishable directory tree without uploading files",
    )
    parser.add_argument("--limit", type=int, help="Only upload the first N files")
    parser.add_argument("--skip", type=int, default=0, help="Skip the first N files before uploading")
    parser.add_argument("--force", action="store_true", help="Upload files even when the remote size already matches")
    parser.add_argument(
        "--all-public-files",
        action="store_true",
        help="Upload every file with a public extension instead of the linked/reachable manifest",
    )
    parser.add_argument(
        "--include-videos",
        action="store_true",
        help="Include linked video binaries. By default they are left out to avoid large unintended uploads.",
    )
    args = parser.parse_args()

    socket.setdefaulttimeout(30)
    deploy(args)


if __name__ == "__main__":
    main()
