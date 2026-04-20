---
name: chat-transcript
description: Capture and save the current AI chat session as a markdown transcript file. Use when the user asks to "save transcript", "capture session", "write transcript.md", or wants to export the current conversation for review. Supports Claude Code and GitHub Copilot (CLI + VS Code Chat) on Linux, WSL, and Windows.
---

# Chat Transcript

Save the current AI session to a markdown file for trainer/reviewer use.

## Quick start

**Step 1** — mark this session with a unique token (run this first, in the chat):

```bash
python ~/.claude/skills/chat-transcript/scripts/capture.py --mark
```

This prints a token like `TRANSCRIPT-TOKEN-a3f8c2d1` and saves it. The token appearing in the chat response pins this exact session.

**Step 2** — capture the transcript:

```bash
python ~/.claude/skills/chat-transcript/scripts/capture.py [output.md]
```

The script finds the session containing the token and saves it to `transcript.md` (or the specified file).

Other options:

```bash
# List recent sessions
python ~/.claude/skills/chat-transcript/scripts/capture.py --list

# Capture a specific session by ID
python ~/.claude/skills/chat-transcript/scripts/capture.py --session <session-id>
```

## How session detection works

`--mark` prints a unique token that gets recorded in the chat session. `capture.py` then greps known session-storage locations (Claude Code, Copilot CLI, VS Code Copilot Chat) for that token to pick the exact session.

Without `--mark`, falls back to the most-recently-modified session for the current cwd.

## Output format

```markdown
# Chat Transcript
**Tool:** Claude Code
**Session:** `f110653a-...`
**Captured:** 2026-03-11 20:40

---

### **User** _2026-03-11 18:31_

<message text>

---

### **Assistant** _2026-03-11 18:32_

<message text>
```

Tool calls are shown inline as `*[tool: name(args)]*` and `*[tool result: ...]*`.
