"""Symlink all skills to ~/.claude/skills"""

import argparse
import os
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"
EXTRA_SKILLS_DIR = Path(__file__).parent / "extra-skills"
TARGET_DIR = Path.home() / ".claude" / "skills"


def link_skills(source_dir: Path) -> None:
    for skill in source_dir.iterdir():
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


def main():
    parser = argparse.ArgumentParser(description="Symlink skills to ~/.claude/skills")
    parser.add_argument("--extra", action="store_true", help="Also install extra skills")
    args = parser.parse_args()

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    link_skills(SKILLS_DIR)

    if args.extra:
        link_skills(EXTRA_SKILLS_DIR)


if __name__ == "__main__":
    main()
