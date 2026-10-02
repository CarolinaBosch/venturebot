#!/usr/bin/env python3
"""Run every generator, then verify. One command for the whole publish step.

Written 2026-10-02 after a wake updated runway.json, skipped both generators,
and reported "12/12 checks pass" while two checks were failing and seventeen
exist.

The generators were already written and already worked. sync_storefront.py
was built on 09-30 specifically to end seven wakes of hand-fixing the price;
build_sitemap.py has existed since 09-19. Neither ran, because nothing made
them run - they were tools a wake had to remember, and remembering is the
thing that keeps failing.

This is the publish step. Run it before committing:

    /usr/bin/python3 scripts/publish.py

It regenerates every derived artifact from runway.json, mirrors the tracker,
and reports what changed. It does NOT commit - that stays deliberate.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable

GENERATORS = [
    ("storefront price", "sync_storefront.py"),
    ("sitemap", "build_sitemap.py"),
    ("social card", "make_og_image.py"),
]


def run(script):
    r = subprocess.run([PY, str(ROOT / "scripts" / script)],
                       capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    print("=== regenerating derived artifacts from runway.json ===")
    failed = []
    for label, script in GENERATORS:
        code, out = run(script)
        first = out.splitlines()[0] if out else "(no output)"
        print(f"  [{'ok  ' if code == 0 else 'FAIL'}] {label:18s} {first[:72]}")
        if code != 0:
            failed.append(label)
            for line in out.splitlines()[:4]:
                print(f"         {line}")

    # mirror the tracker; Jekyll does not serve _data/ so the root copy is
    # what the public actually reads, and the two must never disagree.
    print("\n=== mirroring runway.json ===")
    src = ROOT / "runway.json"
    dst = ROOT / "_data" / "runway.json"
    try:
        json.loads(src.read_text())          # fail loudly on malformed JSON
        dst.write_text(src.read_text())
        same = src.read_text() == dst.read_text()
        print(f"  [{'ok  ' if same else 'FAIL'}] mirrors byte-identical")
        if not same:
            failed.append("mirror")
    except Exception as e:
        print(f"  [FAIL] {type(e).__name__}: {e}")
        failed.append("mirror")

    print("\n=== uncommitted changes ===")
    r = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                       text=True, cwd=ROOT)
    changed = [l for l in r.stdout.strip().splitlines() if l.strip()]
    for line in changed:
        print(f"  {line}")
    if not changed:
        print("  (none - everything already in sync)")

    print()
    if failed:
        print(f"{len(failed)} GENERATOR(S) FAILED: {failed}")
        print("Do not commit until these are resolved.")
        return 1

    print("All generators ran. Commit, push, then:")
    print("  /usr/bin/python3 scripts/wait_deploy.py --path /runway.json "
          "--contains '<marker>'")
    print("  /usr/bin/python3 scripts/verify_site.py")
    print()
    print("verify_site.py runs 17 checks against the LIVE site. Report the")
    print("number it prints, not a number from memory.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
