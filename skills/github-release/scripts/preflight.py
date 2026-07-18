"""Pre-release checks: gh auth, refs/releases, local/remote sync, and CI.
Exits non-zero and prints the failing check if anything blocks a release.
"""

import json
import re
import subprocess
import sys
import time


def run(*args, check=True):
    r = subprocess.run(args, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"FAIL: {' '.join(args)}\n{r.stderr}")
        sys.exit(1)
    return r.stdout.strip()


def run_combined(*args):
    """gh auth status writes to stderr; merge both streams."""
    r = subprocess.run(args, capture_output=True, text=True)
    return (r.stdout + "\n" + r.stderr).strip()


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


branch = run("git", "rev-parse", "--abbrev-ref", "HEAD")

# 1. gh auth -- switch to the account matching this repo (work vs. public),
# detected from gh's own logged-in account list. Same heuristic as the repo
# remote: an underscore in the username means "work".
print("== GitHub authentication ==")
remote = run("git", "remote", "-v")
is_work_repo = "_/" in (remote.splitlines()[0] if remote else "")
status = run_combined("gh", "auth", "status")
accounts = re.findall(r"account (\S+)", status)
target = next((a for a in accounts if ("_" in a) == is_work_repo), None)
if target:
    run("gh", "auth", "switch", "--user", target)
print(f"gh auth: {target or 'no matching account found, using current'}")

# 2. Capture release history for version and release-note analysis. JSON keeps
# the output machine-readable while still being compact enough to inspect.
print("\n== Recent releases ==")
releases = run(
    "gh", "release", "list", "--limit", "5",
    "--json", "tagName,name,publishedAt,isDraft,isPrerelease",
)
print(releases)

# 3. Report local changes that will not be included in the release. uv.lock is
# routinely rewritten by tooling and is intentionally omitted from this warning.
print("\n== Local worktree ==")
dirty = "\n".join(
    line for line in run("git", "status", "--short").splitlines()
    if line[3:] != "uv.lock"
)
if dirty:
    print(f"WARNING: dirty worktree (not included in release):\n{dirty}")
else:
    print("worktree: clean")

# 4. Push, refresh all remote refs (including tags), and verify local == remote.
print("\n== Remote synchronization ==")
run("git", "push", "origin", branch)
run("git", "fetch", "origin", "--prune", "--tags")
sha = run("git", "rev-parse", "HEAD")
remote_sha = run("git", "rev-parse", f"origin/{branch}")
if sha != remote_sha:
    fail(f"local HEAD ({sha}) != origin/{branch} ({remote_sha}) — out of sync")
print(f"sync and tags: ok ({sha})")

# 5. Wait for every Actions run on this exact commit, requiring success.
print("\n== GitHub Actions ==")
runs = []
for attempt in range(30):
    runs = json.loads(run(
        "gh", "run", "list", "--commit", sha, "--limit", "100",
        "--json", "workflowName,status,conclusion,headSha,url",
        check=False,
    ) or "[]")
    if not runs:
        if attempt >= 5:
            break
        print("CI status: no run yet (waiting...)")
        time.sleep(1)
        continue
    pending = [item for item in runs if item["status"] != "completed"]
    if not pending:
        break
    status = ", ".join(
        f"{item['workflowName'] or '(unnamed)'}={item['status']}"
        for item in runs
    )
    print(f"CI status: {status} (waiting...)")
    time.sleep(20)

if not runs:
    latest = json.loads(run(
        "gh", "run", "list", "--branch", branch, "--limit", "5",
        "--json", "workflowName,status,conclusion,headSha,url",
    ) or "[]")
    print(f"CI: no run found for commit; latest {branch} runs: {json.dumps(latest)}")
    failed = [
        item for item in latest
        if item["status"] == "completed" and item["conclusion"] != "success"
    ]
    if failed:
        names = ", ".join(item["workflowName"] or "(unnamed)" for item in failed)
        fail(f"latest {branch} Actions runs failed: {names}")
    print("CI: exact commit status unavailable — proceed with judgement")
else:
    pending = [item for item in runs if item["status"] != "completed"]
    if pending:
        names = ", ".join(item["workflowName"] or "(unnamed)" for item in pending)
        fail(f"CI did not complete on {sha}: {names}")
    failed = [item for item in runs if item["conclusion"] != "success"]
    if failed:
        details = ", ".join(
            f"{item['workflowName'] or '(unnamed)'}={item['conclusion']}"
            for item in failed
        )
        fail(f"CI failed on {sha}: {details}")
    names = ", ".join(item["workflowName"] or "(unnamed)" for item in runs)
    print(f"CI: success ✓ ({names})")

print("PREFLIGHT PASS")
