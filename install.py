"""Symlink all skills to ~/.claude/skills"""

import os
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"
TARGET_DIR = Path.home() / ".claude" / "skills"


def main():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    for skill in SKILLS_DIR.iterdir():
        if not skill.is_dir():
            continue

        target = TARGET_DIR / skill.name
        if target.is_symlink() or target.exists():
            if target.is_symlink():
                target.unlink()
            else:
                print(f"Skipping {skill.name}: {target} exists and is not a symlink")
                continue

        target.symlink_to(skill.resolve())
        print(f"Linked {skill.name} -> {target}")


if __name__ == "__main__":
    main()
