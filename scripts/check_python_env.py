#!/usr/bin/env python3
"""Verify the Python interpreter the wake tooling depends on actually runs.

On 2026-09-23 every script broke at once:

    /usr/local/bin/python3: Bad CPU type in executable

The machine is arm64; `/usr/local/bin/python3` is a Homebrew x86_64 binary
that had been running under Rosetta translation, and that stopped working.
Nothing about the site or the agent was wrong - the interpreter underneath
simply stopped executing, and every script failed identically.

This checks the interpreters in PATH order and names a working one, so the
next time everything breaks at once the cause takes seconds rather than a
wake to find.

    python3 scripts/check_python_env.py
"""
import platform
import subprocess
import sys

CANDIDATES = [
    "/usr/bin/python3",                                    # system, universal
    "/usr/local/bin/python3",                              # homebrew (x86_64)
    "/opt/homebrew/bin/python3",                           # homebrew (arm64)
]


def probe(path):
    """Return (ok, detail) for one interpreter."""
    try:
        r = subprocess.run([path, "-c", "import sys; print(sys.version.split()[0])"],
                           capture_output=True, text=True, timeout=20)
        if r.returncode == 0:
            return True, r.stdout.strip()
        err = (r.stderr or r.stdout).strip().splitlines()
        return False, err[-1] if err else f"exit {r.returncode}"
    except FileNotFoundError:
        return False, "not present"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def main():
    print(f"machine architecture: {platform.machine()}")
    print(f"this process is running: {sys.executable} ({sys.version.split()[0]})")
    print()

    working = []
    for path in CANDIDATES:
        ok, detail = probe(path)
        print(f"  [{'OK  ' if ok else 'FAIL'}] {path:34s} {detail}")
        if ok:
            working.append(path)

    print()
    if not working:
        print("NO WORKING INTERPRETER FOUND. The wake tooling cannot run.")
        return 1

    print(f"Use: {working[0]}")
    if "/usr/local/bin/python3" not in working:
        print()
        print("Note: /usr/local/bin/python3 is broken. It is the Homebrew")
        print("x86_64 build and this machine is arm64 - it only ever worked")
        print("through Rosetta. Anything invoking a bare `python3` from a")
        print("PATH that hits /usr/local/bin first will fail with")
        print("'Bad CPU type in executable'. Invoke an explicit path instead.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
