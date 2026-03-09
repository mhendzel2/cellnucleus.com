#!/usr/bin/env python3
"""Deploy the static CellNucleus site to an Aplus-hosted FTP target."""

from __future__ import annotations

import argparse
import os
import posixpath
import socket
from contextlib import suppress
from ftplib import FTP, FTP_TLS, all_errors
from pathlib import Path
from typing import Iterable

from aplus_secrets import load_aplus_secrets

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".github",
    ".secrets",
    "backup",
    "docs",
    "reports",
    "scripts",
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


def deploy(args: argparse.Namespace) -> None:
    secrets = load_aplus_secrets(args.env_path)
    username = args.username or secrets.get("APLUS_FTP_USERNAME") or secrets.get("APLUS_USERNAME", "")
    password = args.password or secrets.get("APLUS_PASSWORD", "")
    host = args.host or secrets.get("APLUS_FTP_HOST", "ftp.cellnucleus.com")
    port = int(args.port or secrets.get("APLUS_FTP_PORT", "21"))
    secure = args.secure or secrets.get("APLUS_FTP_SECURE", "auto")
    remote_dir = args.remote_dir or secrets.get("APLUS_REMOTE_DIR", "cellnucleus.com")

    if not username or not password:
        raise SystemExit("Missing Aplus username or password in .secrets/.env")

    files = list(iter_publishable_files())
    if args.limit:
        files = files[: args.limit]

    ftp = connect_ftp(host, port, username, password, secure)
    try:
        root_entries = list_root_entries(ftp)
        print(f"Connected to {host}:{port}")
        print(f"Remote root entries: {len(root_entries)}")
        for entry in root_entries[:50]:
            print(f"- {entry}")
        if args.inspect:
            return

        cwd_or_fail(ftp, remote_dir)
        print(f"Deploy target: {ftp.pwd()}")

        archived = archive_remote_index(ftp)
        if archived:
            print(f"Archived remote index.phtml -> {archived}")

        if args.dry_run:
            print(f"Dry run only. Would upload {len(files)} files.")
            for rel in files[:50]:
                print(f"- {rel.as_posix()}")
            return

        uploaded = 0
        for rel in files:
            upload_file(ftp, rel)
            uploaded += 1
            if uploaded % 25 == 0 or uploaded == len(files):
                print(f"Uploaded {uploaded}/{len(files)}")
        print(f"Deployment complete. Uploaded {uploaded} files to {remote_dir}.")
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
    parser.add_argument("--limit", type=int, help="Only upload the first N files")
    args = parser.parse_args()

    socket.setdefaulttimeout(30)
    deploy(args)


if __name__ == "__main__":
    main()
