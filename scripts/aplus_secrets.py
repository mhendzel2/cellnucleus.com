#!/usr/bin/env python3
"""Load Aplus credentials from an untracked local secrets file."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_PATH = ROOT / ".secrets" / ".env"

LABEL_MAP = {
    "username/account": "APLUS_USERNAME",
    "username": "APLUS_USERNAME",
    "account": "APLUS_USERNAME",
    "password": "APLUS_PASSWORD",
    "ftp username": "APLUS_FTP_USERNAME",
    "ftp user": "APLUS_FTP_USERNAME",
    "panel url": "APLUS_PANEL_URL",
    "ftp host": "APLUS_FTP_HOST",
    "ftp port": "APLUS_FTP_PORT",
    "ftp secure": "APLUS_FTP_SECURE",
    "remote dir": "APLUS_REMOTE_DIR",
    "admin user": "CELLNUCLEUS_ADMIN_USER",
    "admin username": "CELLNUCLEUS_ADMIN_USER",
    "admin password": "CELLNUCLEUS_ADMIN_PASSWORD",
    "taskforce admin user": "TASKFORCE_ADMIN_USER",
    "taskforce admin password": "TASKFORCE_ADMIN_PASSWORD",
}

DEFAULTS = {
    "APLUS_FTP_HOST": "ftp.cellnucleus.com",
    "APLUS_FTP_PORT": "21",
    "APLUS_FTP_SECURE": "auto",
    "APLUS_REMOTE_DIR": "cellnucleus.com",
}


def normalize_key(raw_key: str) -> str:
    key = raw_key.strip().strip('"').strip("'")
    if not key:
        return ""
    lookup = key.lower()
    if lookup in LABEL_MAP:
        return LABEL_MAP[lookup]
    if key.upper().startswith("APLUS_"):
        return key.upper()
    return key.upper().replace(" ", "_").replace("/", "_")


def normalize_value(raw_value: str) -> str:
    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Secrets file not found: {path}")

    secrets: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if "=" in stripped:
            raw_key, raw_value = stripped.split("=", 1)
        elif ":" in stripped:
            raw_key, raw_value = stripped.split(":", 1)
        else:
            continue

        key = normalize_key(raw_key)
        value = normalize_value(raw_value)
        if key and value:
            secrets[key] = value

    for key, value in DEFAULTS.items():
        secrets.setdefault(key, value)
    return secrets


def load_aplus_secrets(path: Path | None = None) -> dict[str, str]:
    env_path = path or DEFAULT_ENV_PATH
    return parse_env_file(env_path)


def redact(values: dict[str, str]) -> dict[str, str]:
    redacted: dict[str, str] = {}
    for key, value in values.items():
        if any(token in key for token in ("PASSWORD", "USERNAME", "SECRET", "TOKEN")):
            redacted[key] = f"<hidden:{len(value)}>"
        else:
            redacted[key] = value
    return redacted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=DEFAULT_ENV_PATH, help="Path to the local secrets file")
    parser.add_argument(
        "--format",
        choices=("shell", "json", "keys"),
        default="keys",
        help="Output format. 'shell' emits export statements; 'json' redacts secret values.",
    )
    args = parser.parse_args()

    secrets = load_aplus_secrets(args.path)
    if args.format == "shell":
        for key in sorted(secrets):
            print(f"export {key}={shlex.quote(secrets[key])}")
        return
    if args.format == "json":
        print(json.dumps(redact(secrets), indent=2, sort_keys=True))
        return
    for key in sorted(secrets):
        print(key)


if __name__ == "__main__":
    main()
