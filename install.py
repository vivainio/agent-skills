"""Symlink all skills to ~/.claude/skills"""

import argparse
import os
import shutil
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"
EXTRA_SKILLS_DIR = Path(__file__).parent / "extra-skills"
TARGET_DIR = Path.home() / ".claude" / "skills"

TRAINING_SKILLS = {"zaira", "chat-transcript"}


def link_skills(source_dir: Path, only: set[str] | None = None, copy: bool = False) -> None:
    for skill in source_dir.iterdir():
        if not skill.is_dir():
            continue
        if only and skill.name not in only:
            continue

        target = TARGET_DIR / skill.name
        if target.is_symlink() or target.exists():
            if target.is_symlink():
                target.unlink()
            else:
                print(f"Skipping {skill.name}: {target} exists and is not a symlink")
                continue

        if copy:
            shutil.copytree(skill.resolve(), target)
            print(f"Copied {skill.name} -> {target}")
        else:
            try:
                target.symlink_to(skill.resolve())
            except OSError as e:
                if os.name == "nt":
                    print(f"Failed to create symlink for {skill.name}: {e}")
                    print("On Windows, run this script as Administrator or enable Developer Mode.")
                    sys.exit(1)
                raise
            print(f"Linked {skill.name} -> {target}")


def main():
    parser = argparse.ArgumentParser(description="Symlink skills to ~/.claude/skills")
    parser.add_argument("--extra", action="store_true", help="Also install extra skills")
    parser.add_argument("--training", action="store_true", help="Only install training skills (zaira, chat-transcript)")
    args = parser.parse_args()

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    only = TRAINING_SKILLS if args.training else None
    link_skills(SKILLS_DIR, only=only, copy=args.training)

    if args.extra:
        link_skills(EXTRA_SKILLS_DIR, only=only, copy=args.training)


if __name__ == "__main__":
    main()
