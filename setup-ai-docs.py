#!/usr/bin/env python3
"""
setup-ai-docs.py

Builder script:
1) Reads master-prompt.md
2) Asks target OS
3) Generates a drop-in executable bootstrap file that can be copied to any project
   to create AI agent markdown documentation files.

Architecture: This script now integrates with modularized src/ components:
- src/lib.py: 30+ utility functions
- src/constants/: All compliance frameworks, archetypes, hints
- src/core/: Context building and metadata
- src/bootstrap_builder/: Bootstrap generation
- src/generators/: Compliance scanning generators
"""

from __future__ import annotations

import stat
from pathlib import Path

from src.bootstrap_template import build_bootstrap_script


def ask_target_os() -> str:
    options = {
        "1": "macos",
        "2": "linux",
        "3": "windows",
        "4": "auto",
    }
    print("Select target OS for the generated executable:")
    print("  1) macOS")
    print("  2) Linux")
    print("  3) Windows")
    print("  4) Auto (recommended)")

    while True:
        choice = input("Enter choice [1-4] (default 4): ").strip() or "4"
        if choice in options:
            return options[choice]
        print("Invalid choice. Please select 1, 2, 3, or 4.")




def main() -> None:
    script_dir = Path(__file__).resolve().parent
    prompt_path = script_dir / "master-prompt.md"

    if not prompt_path.exists():
        raise SystemExit(f"Missing required file: {prompt_path}")

    master_prompt = prompt_path.read_text(encoding="utf-8")
    target_os = ask_target_os()

    if target_os in {"macos", "linux", "auto"}:
        output_name = "ai-docs-bootstrap"
    else:
        output_name = "ai-docs-bootstrap.py"

    output_path = script_dir / output_name
    bootstrap_content = build_bootstrap_script(master_prompt, target_os)
    output_path.write_text(bootstrap_content, encoding="utf-8")

    # Mark executable on Unix-like systems.
    if output_name == "ai-docs-bootstrap":
        mode = output_path.stat().st_mode
        output_path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print("\nBootstrap executable generated successfully.")
    print(f"- Source prompt: {prompt_path}")
    print(f"- Target OS profile: {target_os}")
    print(f"- Output: {output_path}")
    print("\nUsage examples:")
    if output_name == "ai-docs-bootstrap":
        print("  ./ai-docs-bootstrap --project /path/to/project")
    else:
        print("  python ai-docs-bootstrap.py --project C:\\path\\to\\project")


if __name__ == "__main__":
    main()
