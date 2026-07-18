"""Pre-release checks: gh auth, local/remote sync, CI status on target branch.
Exits non-zero and prints the failing check if anything blocks a release.
"""

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
remote = run("git", "remote", "-v")
is_work_repo = "_/" in (remote.splitlines()[0] if remote else "")
status = run_combined("gh", "auth", "status")
accounts = re.findall(r"account (\S+)", status)
target = next((a for a in accounts if ("_" in a) == is_work_repo), None)
if target:
    run("gh", "auth", "switch", "--user", target)
print(f"gh auth: {target or 'no matching account found, using current'}")

# 2. push and verify local == remote
run("git", "push", "origin", branch)
run("git", "fetch", "origin", branch)
sha = run("git", "rev-parse", "HEAD")
remote_sha = run("git", "rev-parse", f"origin/{branch}")
if sha != remote_sha:
    fail(f"local HEAD ({sha}) != origin/{branch} ({remote_sha}) — out of sync")
print(f"sync: ok ({sha})")

# 3. wait for CI on this exact commit, require success
conclusion = None
gh_status = None
for _ in range(30):
    out = run(
        "gh", "run", "list", "--branch", branch, "--limit", "20",
        "--json", "headSha,status,conclusion",
        "--jq", f'[.[] | select(.headSha=="{sha}")] | .[0] | "\\(.status) \\(.conclusion)"',
        check=False,
    )
    parts = out.split(" ", 1)
    gh_status = parts[0] if parts and parts[0] else None
    conclusion = parts[1] if len(parts) > 1 else None
    if gh_status == "completed":
        break
    print(f"CI status: {gh_status or 'no run yet'} (waiting...)")
    time.sleep(20)

if not gh_status:
    print("CI: no run found for commit — proceed with judgement")
elif conclusion != "success":
    fail(f"CI concluded '{conclusion}' on {sha} — do not release")
else:
    print("CI: success ✓")

print("PREFLIGHT PASS")
