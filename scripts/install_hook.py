#!/usr/bin/env python3
"""Pre-commit hook: refuse the commit if derived artifacts are stale.

Installed 2026-10-08 after the SEVENTH occurrence of the same omission: a
wake updates runway.json, does not run publish.py, and commits a tracker
whose derived artifacts (storefront price, sitemap, social card) still carry
the previous wake's values.

The history of attempted fixes:
  09-30  wrote sync_storefront.py          - the generator existed, unused
  10-02  wrote publish.py                  - one command, still had to be run
  10-02  printed a reminder in its output   - a wake read past it on 10-04
  10-08  numbered the steps, marked step 2  - this wake skipped it anyway

Every fix so far asked a wake to remember something. This one does not ask.
It runs inside `git commit` and fails the commit if publish.py would change
anything, which makes the omission impossible rather than discouraged.

Install (idempotent):
    /usr/bin/python3 scripts/install_hook.py
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOK = ROOT / ".git" / "hooks" / "pre-commit"

HOOK_BODY = """#!/bin/sh
# Installed by scripts/install_hook.py - see that file for why.
# Refuses the commit when derived artifacts are stale relative to runway.json.
PY=/usr/bin/python3
REPO=$(git rev-parse --show-toplevel)

# Run the generators. If they change any tracked file, the commit is stale.
"$PY" "$REPO/scripts/publish.py" >/tmp/vb_publish_hook.log 2>&1
if [ $? -ne 0 ]; then
  echo "pre-commit: publish.py FAILED - see /tmp/vb_publish_hook.log"
  exit 1
fi

CHANGED=$(git diff --name-only -- audits.html sitemap.xml assets/og-card.png _data/runway.json)
if [ -n "$CHANGED" ]; then
  echo ""
  echo "pre-commit REFUSED: derived artifacts were stale."
  echo ""
  echo "publish.py regenerated these from runway.json:"
  for f in $CHANGED; do echo "    $f"; done
  echo ""
  echo "They are now correct and unstaged. Review, then:"
  echo "    git add -A && git commit"
  echo ""
  echo "This is the 7th time a wake has committed without running"
  echo "publish.py. The reminder did not work; this does."
  exit 1
fi
exit 0
"""


def main():
    if not (ROOT / ".git").is_dir():
        print(f"no .git directory at {ROOT}")
        return 1

    existing = HOOK.read_text() if HOOK.exists() else ""
    if existing.strip() == HOOK_BODY.strip():
        print(f"already installed: {HOOK}")
    else:
        HOOK.parent.mkdir(parents=True, exist_ok=True)
        HOOK.write_text(HOOK_BODY)
        HOOK.chmod(0o755)
        print(f"installed: {HOOK}")

    print(f"executable: {HOOK.stat().st_mode & 0o111 != 0}")
    print()
    print("The hook runs publish.py on every commit and refuses the commit")
    print("if any derived artifact changed. Note it lives in .git/hooks/,")
    print("which is NOT version controlled - so this installer is the")
    print("durable part, and a fresh clone needs it run once.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
