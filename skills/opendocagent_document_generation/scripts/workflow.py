"""
OpenDocAgent Document Workflow Manager

Handles the lifecycle of generated documents:
  - wip/      -> Active drafts being built
  - finalized/ -> Completed markdown + rendered outputs

Usage:
  python scripts/workflow.py new <slug>
  python scripts/workflow.py build <slug> --format <fmt>
  python scripts/workflow.py finalize <slug>
  python scripts/workflow.py status
"""

import argparse
import os
import shutil
import sys
import subprocess
from pathlib import Path

# Resolve project root by walking up until we find pyproject.toml
def _find_project_root() -> Path:
    candidate = Path(__file__).resolve().parent
    for _ in range(10):
        if (candidate / "pyproject.toml").exists():
            return candidate
        candidate = candidate.parent
    raise RuntimeError("Could not locate project root (no pyproject.toml found).")

PROJECT_ROOT = _find_project_root()
WIP_DIR = PROJECT_ROOT / "wip"
FINAL_DIR = PROJECT_ROOT / "finalized"


def ensure_dirs():
    WIP_DIR.mkdir(exist_ok=True)
    FINAL_DIR.mkdir(exist_ok=True)


def wip_path(slug: str) -> Path:
    return WIP_DIR / slug


def final_path(slug: str) -> Path:
    return FINAL_DIR / slug


def cmd_new(slug: str):
    """Create a new wip/<slug>/ workspace with a blank markdown stub."""
    ensure_dirs()
    workspace = wip_path(slug)
    if workspace.exists():
        print(f"[workflow] WIP workspace already exists: {workspace}")
        sys.exit(1)

    workspace.mkdir(parents=True)
    md_file = workspace / f"{slug}.md"
    md_file.write_text(
        f"---\nformat: pptx\nstyle: executive\ntitle: \"{slug}\"\nauthor: \"\"\n---\n\n# {slug}\n\nStart writing here.\n",
        encoding="utf-8"
    )
    print(f"[workflow] Created WIP workspace: {workspace}")
    print(f"[workflow] Edit your Markdown: {md_file}")


def cmd_build(slug: str, fmt: str, extra: list):
    """Build the document from wip/<slug>/<slug>.md into wip/<slug>/."""
    ensure_dirs()
    workspace = wip_path(slug)
    md_file = workspace / f"{slug}.md"

    if not md_file.exists():
        print(f"[workflow] Error: Markdown not found at {md_file}")
        sys.exit(1)

    cmd = ["opendoc", "build", str(md_file), "--format", fmt] + extra
    print(f"[workflow] Building: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print("[workflow] Build failed.")
        sys.exit(result.returncode)

    # Move rendered output into the wip workspace folder
    ext_map = {"pptx": "pptx", "docx": "docx", "pdf": "pdf", "beamer": "pdf", "latex": "pdf"}
    out_ext = ext_map.get(fmt, fmt)
    rendered = PROJECT_ROOT / f"{slug}.{out_ext}"
    if rendered.exists():
        dest = workspace / rendered.name
        shutil.move(str(rendered), str(dest))
        print(f"[workflow] Rendered output moved to: {dest}")


def cmd_finalize(slug: str):
    """Promote wip/<slug>/ -> finalized/<slug>/."""
    ensure_dirs()
    src = wip_path(slug)
    dst = final_path(slug)

    if not src.exists():
        print(f"[workflow] Error: No WIP workspace found for '{slug}'")
        sys.exit(1)

    if dst.exists():
        print(f"[workflow] Warning: Overwriting existing finalized workspace: {dst}")
        shutil.rmtree(str(dst))

    shutil.copytree(str(src), str(dst))
    shutil.rmtree(str(src))
    print(f"[workflow] Finalized! Moved {src} -> {dst}")


def cmd_status():
    """List all WIP and finalized workspaces."""
    ensure_dirs()
    wip_items = [d.name for d in WIP_DIR.iterdir() if d.is_dir()]
    final_items = [d.name for d in FINAL_DIR.iterdir() if d.is_dir()]

    print("=== WIP Workspaces ===")
    if wip_items:
        for item in sorted(wip_items):
            files = list(wip_path(item).iterdir())
            print(f"  wip/{item}/ ({len(files)} files)")
    else:
        print("  (none)")

    print("\n=== Finalized Workspaces ===")
    if final_items:
        for item in sorted(final_items):
            files = list(final_path(item).iterdir())
            print(f"  finalized/{item}/ ({len(files)} files)")
    else:
        print("  (none)")


def main():
    parser = argparse.ArgumentParser(
        description="OpenDocAgent Workflow Manager — manage wip/ and finalized/ document lifecycles."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # new
    p_new = subparsers.add_parser("new", help="Create a new WIP workspace")
    p_new.add_argument("slug", help="Short identifier for the document (e.g. q3-report)")

    # build
    p_build = subparsers.add_parser("build", help="Build a WIP document")
    p_build.add_argument("slug", help="WIP workspace slug")
    p_build.add_argument("--format", default="pptx", choices=["pptx", "docx", "pdf", "beamer", "latex"], help="Output format")
    p_build.add_argument("extra", nargs=argparse.REMAINDER, help="Extra flags passed to opendoc")

    # finalize
    p_fin = subparsers.add_parser("finalize", help="Promote a WIP workspace to finalized/")
    p_fin.add_argument("slug", help="WIP workspace slug to finalize")

    # status
    subparsers.add_parser("status", help="List all WIP and finalized workspaces")

    args = parser.parse_args()

    if args.command == "new":
        cmd_new(args.slug)
    elif args.command == "build":
        cmd_build(args.slug, args.format, args.extra)
    elif args.command == "finalize":
        cmd_finalize(args.slug)
    elif args.command == "status":
        cmd_status()


if __name__ == "__main__":
    main()
