from __future__ import annotations

from pathlib import Path
import re

_ROW_PATTERN = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([0-9]{4})\s*\|$")
_REQUIRED_ROW = ("demo.customer10@example.com", "1234")


def _default_testdata_path() -> Path:
    return Path(__file__).resolve().parents[3] / "testdata.md"


def load_demo_credentials(path: Path | None = None) -> dict[str, str]:
    file_path = path or _default_testdata_path()
    if not file_path.exists():
        raise FileNotFoundError(f"Missing demo credential file: {file_path}")

    rows: dict[str, str] = {}
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        match = _ROW_PATTERN.match(raw_line.strip())
        if not match:
            continue

        email, pin = match.group(1).strip(), match.group(2)
        if email.lower() == "email":
            continue
        if email in rows:
            raise ValueError(f"Duplicate demo email in testdata.md: {email}")
        rows[email] = pin

    if not rows:
        raise ValueError("No demo credentials found in testdata.md")

    return rows


def validate_testdata_contract(path: Path | None = None) -> dict[str, str]:
    rows = load_demo_credentials(path)
    required_email, required_pin = _REQUIRED_ROW

    if rows.get(required_email) != required_pin:
        raise ValueError(
            "testdata.md contract mismatch: "
            f"expected {required_email} to map to PIN {required_pin}"
        )

    return rows
