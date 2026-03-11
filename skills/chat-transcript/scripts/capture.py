#!/usr/bin/env python3
"""
Capture the current AI session as a markdown transcript.

Supports:
  - Claude Code  (Linux: ~/.claude/projects/  |  Windows: %APPDATA%/claude/projects/)
  - Copilot CLI + VS Code Copilot Chat  (Linux: ~/.copilot/session-state/  |  Windows: %USERPROFILE%/.copilot/session-state/)

Usage:
  python3 capture.py [output_file]        # auto-detect most recent session for cwd
  python3 capture.py --session <id> [output_file]
  python3 capture.py --list               # list recent sessions

Output defaults to transcript.md in the current directory.
"""

import argparse
import json
import os
import platform
import sys
import uuid
from datetime import datetime
from pathlib import Path

TOKEN_FILE = Path.home() / ".claude" / "skills" / "chat-transcript" / ".last-token"


# ── Platform paths ────────────────────────────────────────────────────────────

def is_windows() -> bool:
    return platform.system() == "Windows"


def claude_base() -> Path:
    if is_windows():
        appdata = os.environ.get("APPDATA", "")
        return Path(appdata) / "claude" / "projects"
    return Path.home() / ".claude" / "projects"


def copilot_base() -> Path:
    if is_windows():
        return Path.home() / ".copilot" / "session-state"
    return Path.home() / ".copilot" / "session-state"


def encode_project_path(project_dir: str) -> str:
    """
    Encode a project directory path the same way Claude Code does.
    Both / and \\ separators become -, drive colon (C:) also becomes -.
    E.g. /home/v/foo  ->  -home-v-foo
         C:\\Users\\v\\foo  ->  C--Users-v-foo
    """
    return project_dir.replace("\\", "-").replace("/", "-").replace(":", "-")


# ── Token marking ────────────────────────────────────────────────────────────

def cmd_mark() -> str:
    """Generate a unique token, save it, and print it so it's captured in the session."""
    token = f"TRANSCRIPT-TOKEN-{uuid.uuid4().hex[:8]}"
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(token)
    print(token)
    return token


def find_session_by_token(token: str) -> tuple[Path, str] | tuple[None, None]:
    """Search all known session files for the token. Returns (file, tool_name)."""
    candidates: list[tuple[Path, str]] = []

    # Claude Code: search all projects
    claude_projects = claude_base()
    if claude_projects.exists():
        for f in claude_projects.rglob("*.jsonl"):
            candidates.append((f, "Claude Code"))

    # Copilot: search all sessions
    copilot_sessions = copilot_base()
    if copilot_sessions.exists():
        for f in copilot_sessions.rglob("events.jsonl"):
            candidates.append((f, "Copilot CLI / VS Code Copilot Chat"))

    for path, tool in candidates:
        try:
            if token in path.read_text(encoding="utf-8", errors="ignore"):
                return path, tool
        except OSError:
            continue

    return None, None


# ── Claude Code ───────────────────────────────────────────────────────────────

def find_claude_session(project_dir: str) -> Path | None:
    encoded = encode_project_path(project_dir)
    d = claude_base() / encoded
    if not d.exists():
        return None
    files = list(d.glob("*.jsonl"))
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


def parse_claude_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type", "")
            if btype == "text":
                parts.append(block.get("text", ""))
            elif btype == "tool_use":
                name = block.get("name", "tool")
                inp = json.dumps(block.get("input", {}), ensure_ascii=False)
                if len(inp) > 200:
                    inp = inp[:200] + "…"
                parts.append(f"*[tool: {name}({inp})]*")
            elif btype == "tool_result":
                r = block.get("content", "")
                if isinstance(r, list):
                    r = " ".join(x.get("text", "") for x in r if isinstance(x, dict))
                r = str(r)[:200]
                parts.append(f"*[tool result: {r}]*")
        return "\n".join(p for p in parts if p)
    return str(content)


def load_claude_messages(session_file: Path) -> list[dict]:
    messages = []
    with open(session_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") not in ("user", "assistant"):
                continue
            msg = entry.get("message", {})
            role = msg.get("role", entry["type"])
            content = parse_claude_content(msg.get("content", ""))
            if content.strip():
                messages.append({
                    "role": role,
                    "content": content,
                    "timestamp": entry.get("timestamp", ""),
                })
    return messages


# ── Copilot CLI / VS Code Copilot Chat ───────────────────────────────────────

def find_copilot_session(project_dir: str) -> Path | None:
    base = copilot_base()
    if not base.exists():
        return None

    best_file = None
    best_mtime = 0.0

    for session_dir in base.iterdir():
        events_file = session_dir / "events.jsonl"
        if not events_file.exists():
            continue

        # Prefer sessions whose cwd matches project_dir
        cwd_match = False
        try:
            with open(events_file, encoding="utf-8") as f:
                first = json.loads(f.readline())
            cwd = first.get("data", {}).get("context", {}).get("cwd", "")
            cwd_match = bool(cwd) and project_dir.startswith(cwd) or cwd.startswith(project_dir)
        except Exception:
            pass

        mtime = events_file.stat().st_mtime
        # Weight: matching cwd sessions sort above non-matching
        score = mtime + (1e12 if cwd_match else 0)
        if score > best_mtime:
            best_mtime = score
            best_file = events_file

    return best_file


def load_copilot_messages(events_file: Path) -> list[dict]:
    messages = []
    pending_assistant: dict[str, list[tuple[str, str]]] = {}  # messageId -> [(ts, chunk)]

    def flush(chunks: list[tuple[str, str]]) -> dict | None:
        text = "".join(c for _, c in chunks).strip()
        if not text:
            return None
        return {"role": "assistant", "content": text, "timestamp": chunks[0][0] if chunks else ""}

    with open(events_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            t = entry.get("type", "")
            data = entry.get("data", {})
            ts = entry.get("timestamp", "")

            if t == "user.message":
                content = data.get("content", "").strip()
                if content:
                    messages.append({"role": "user", "content": content, "timestamp": ts})

            elif t == "assistant.message":
                mid = data.get("messageId", "__default__")
                chunk = data.get("content", "")
                pending_assistant.setdefault(mid, []).append((ts, chunk))

            elif t == "assistant.turn_end":
                for mid, chunks in pending_assistant.items():
                    msg = flush(chunks)
                    if msg:
                        messages.append(msg)
                pending_assistant.clear()

    # Flush remaining (session still in progress)
    for chunks in pending_assistant.values():
        msg = flush(chunks)
        if msg:
            messages.append(msg)

    return messages


# ── Listing ───────────────────────────────────────────────────────────────────

def list_sessions(project_dir: str):
    encoded = encode_project_path(project_dir)
    print(f"=== Claude Code  ({claude_base() / encoded}) ===")
    d = claude_base() / encoded
    if d.exists():
        for f in sorted(d.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
            ts = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            print(f"  {f.stem}  ({ts})")
    else:
        print("  (none)")

    print(f"\n=== Copilot  ({copilot_base()}) ===")
    base = copilot_base()
    if base.exists():
        rows = []
        for sd in base.iterdir():
            ef = sd / "events.jsonl"
            if not ef.exists():
                continue
            try:
                with open(ef, encoding="utf-8") as f:
                    first = json.loads(f.readline())
                cwd = first.get("data", {}).get("context", {}).get("cwd", "?")
            except Exception:
                cwd = "?"
            rows.append((ef.stat().st_mtime, ef.parent.name, cwd))
        for mtime, sid, cwd in sorted(rows, reverse=True)[:5]:
            ts = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            print(f"  {sid}  ({ts})  cwd={cwd}")
    else:
        print("  (none)")


# ── Formatting ────────────────────────────────────────────────────────────────

def format_transcript(messages: list[dict], source: str, tool: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Chat Transcript",
        f"**Tool:** {tool}",
        f"**Session:** `{source}`",
        f"**Captured:** {now}",
        "",
        "---",
        "",
    ]
    for msg in messages:
        label = "**User**" if msg["role"] == "user" else "**Assistant**"
        ts = msg["timestamp"][:19].replace("T", " ") if msg["timestamp"] else ""
        heading = f"### {label}" + (f" _{ts}_" if ts else "")
        lines += [heading, "", msg["content"], "", "---", ""]
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Capture AI session transcript")
    parser.add_argument("output", nargs="?", default="transcript.md")
    parser.add_argument("--session", help="Session ID or path to session file")
    parser.add_argument("--list", action="store_true", help="List recent sessions")
    parser.add_argument("--mark", action="store_true", help="Generate a token to pin this session, print it into the chat")
    parser.add_argument("--dir", default=os.getcwd(), help="Project directory (default: cwd)")
    args = parser.parse_args()

    project_dir = args.dir

    if args.mark:
        cmd_mark()
        return

    if args.list:
        list_sessions(project_dir)
        return

    messages = None
    source = ""
    tool = ""

    # Token-based detection (most reliable)
    if not args.session and TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text().strip()
        session_file, detected_tool = find_session_by_token(token)
        if session_file:
            tool = detected_tool
            if session_file.name == "events.jsonl":
                messages = load_copilot_messages(session_file)
                source = session_file.parent.name
            else:
                messages = load_claude_messages(session_file)
                source = session_file.stem

    if args.session:
        p = Path(args.session)
        if not p.exists():
            # Try as Claude session ID
            cf = claude_base() / encode_project_path(project_dir) / f"{args.session}.jsonl"
            cp = copilot_base() / args.session / "events.jsonl"
            if cf.exists():
                p = cf
            elif cp.exists():
                p = cp
            else:
                print(f"Session not found: {args.session}", file=sys.stderr)
                sys.exit(1)

        if p.name == "events.jsonl":
            messages = load_copilot_messages(p)
            tool = "Copilot CLI / VS Code Copilot Chat"
            source = p.parent.name
        else:
            messages = load_claude_messages(p)
            tool = "Claude Code"
            source = p.stem
    else:
        # Auto-detect: Claude Code first (scoped to project), then Copilot
        cf = find_claude_session(project_dir)
        if cf:
            messages = load_claude_messages(cf)
            tool = "Claude Code"
            source = cf.stem
        else:
            pf = find_copilot_session(project_dir)
            if pf:
                messages = load_copilot_messages(pf)
                tool = "Copilot CLI / VS Code Copilot Chat"
                source = pf.parent.name

    if not messages:
        print(f"No session found for {project_dir}\nUse --list to see available sessions.", file=sys.stderr)
        sys.exit(1)

    out = Path(args.output)
    out.write_text(format_transcript(messages, source, tool), encoding="utf-8")
    print(f"Saved {len(messages)} messages → {out}  [{tool}]")


if __name__ == "__main__":
    main()
