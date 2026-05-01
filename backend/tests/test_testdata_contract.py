from pathlib import Path

import pytest

from app.services.testdata_contract import load_demo_credentials, validate_testdata_contract


def test_load_demo_credentials_parses_markdown_table(tmp_path: Path) -> None:
    test_file = tmp_path / "testdata.md"
    test_file.write_text(
        "\n".join(
            [
                "# Demo Login Credentials",
                "",
                "| Email | PIN |",
                "|-------|-----|",
                "| demo.customer1@example.com | 1111 |",
                "| demo.customer10@example.com | 1234 |",
            ]
        ),
        encoding="utf-8",
    )

    rows = load_demo_credentials(test_file)
    assert rows["demo.customer1@example.com"] == "1111"
    assert rows["demo.customer10@example.com"] == "1234"


def test_validate_testdata_contract_rejects_missing_required_row(tmp_path: Path) -> None:
    test_file = tmp_path / "testdata.md"
    test_file.write_text(
        "\n".join(
            [
                "| Email | PIN |",
                "|-------|-----|",
                "| demo.customer1@example.com | 1111 |",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="contract mismatch"):
        validate_testdata_contract(test_file)


def test_validate_real_testdata_when_present() -> None:
    root_testdata = Path(__file__).resolve().parents[2] / "testdata.md"
    if not root_testdata.exists():
        pytest.skip("Local-only testdata.md is not present in this environment")

    rows = validate_testdata_contract(root_testdata)
    assert rows["demo.customer10@example.com"] == "1234"
