"""Tests for opendocagent.cli — build and lint sub-commands."""

import sys
import pytest
from unittest.mock import patch
from opendocagent.cli import main


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def test_cli_build(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("---\nformat: docx\ntitle: T\nauthor: A\n---\n# Test\n", encoding="utf-8")

    with patch.object(sys, "argv", ["opendoc", "build", str(md_file)]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

    assert (tmp_path / "test.docx").exists()


def test_cli_build_missing_file(tmp_path):
    with patch.object(sys, "argv", ["opendoc", "build", str(tmp_path / "ghost.md")]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1


# ---------------------------------------------------------------------------
# lint — exit 0 on clean docs
# ---------------------------------------------------------------------------

def test_cli_lint_clean(tmp_path):
    md_file = tmp_path / "clean.md"
    md_file.write_text(
        "---\nformat: pdf\nstyle: technical\ntitle: T\nauthor: A\n---\n"
        "## Purpose\n\nWhy.\n\n## Scope\n\nWhat.\n\n## Methodology\n\nHow.\n",
        encoding="utf-8",
    )

    with patch.object(sys, "argv", ["opendoc", "lint", str(md_file)]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0


# ---------------------------------------------------------------------------
# lint — exit 1 when ERRORs present
# ---------------------------------------------------------------------------

def test_cli_lint_error_exit(tmp_path):
    md_file = tmp_path / "bad.md"
    # No frontmatter at all → F001 ERROR
    md_file.write_text("# Just a heading, no frontmatter\n", encoding="utf-8")

    with patch.object(sys, "argv", ["opendoc", "lint", str(md_file)]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1


def test_cli_lint_missing_file(tmp_path):
    with patch.object(sys, "argv", ["opendoc", "lint", str(tmp_path / "nope.md")]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1


# ---------------------------------------------------------------------------
# lint — warnings only still exit 0
# ---------------------------------------------------------------------------

def test_cli_lint_warnings_only_exit_0(tmp_path):
    md_file = tmp_path / "warn.md"
    # Valid format/style, missing title (WARNING F003), no methodology (WARNING S004)
    # but no ERRORs → should exit 0
    md_file.write_text(
        "---\nformat: pdf\nstyle: technical\nauthor: A\n---\n# Content\n\nSome text.\n",
        encoding="utf-8",
    )

    with patch.object(sys, "argv", ["opendoc", "lint", str(md_file)]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
