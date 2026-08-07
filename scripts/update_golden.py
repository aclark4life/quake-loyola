"""Recompute golden values in tests/test_regression.py from the current map.

This mechanism is self-updating: it re-derives the golden brush/entity
counts and MD5 hash from the same build_map()/build_map_text() code path
that test_regression.py verifies against. That means it has no independent
oracle — blindly re-running this script after a change will "bless" a
regression just as readily as it blesses an intentional change. To guard
against that, this script always prints the old-vs-new delta and requires
an explicit confirmation (or --yes) before overwriting the golden values.
Always look over the resulting `git diff loyola.map` (after `just generate`)
as well, not just the counts printed here.

Isolation from a local ``ql.toml``: the golden values in test_regression.py
are documented as reflecting every flag/build setting at its hardcoded
``config.py`` default, and ``tests/conftest.py`` isolates the whole pytest
session from any local, gitignored ``ql.toml`` override to guarantee that.
This script must isolate the same way — otherwise a repo-root ``ql.toml``
with non-default flags (e.g. a module a developer flipped on for local
iteration) would silently leak into the "golden" values this script writes,
producing a golden file that doesn't match what the test suite actually
computes. See the incident this guarded against: a stray
``WEST_CAMPUS_ENABLED_DORMS = true`` in the repo's ``ql.toml`` leaked into
a golden update, which then failed every regression test because pytest
(correctly isolated) computed different, lower counts.
"""

import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path

# Ensure the project root and src/ are on the path when called from any directory.
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "src"))

# chdir into an empty temp dir *before* importing quake_loyola/generate_map,
# mirroring tests/conftest.py: quake_loyola.config resolves REPO_ROOT/ql.toml
# from cwd at import time, so importing from an isolated, ql.toml-less
# directory guarantees every flag/build setting is exactly its hardcoded
# default, regardless of any local ql.toml at the real repo root.
_tmp_dir = tempfile.TemporaryDirectory(prefix="quake-loyola-golden-config-")
_original_cwd = os.getcwd()
os.chdir(_tmp_dir.name)
try:
    import generate_map  # noqa: E402
finally:
    os.chdir(_original_cwd)

text = generate_map.build_map_text()
new_md5 = hashlib.md5(text.encode()).hexdigest()
mb = generate_map.build_map()
new_brushes = len(mb.brushes)
new_entities = len(mb.entities)

path = root / "tests" / "test_regression.py"
src = path.read_text()

old_brushes = re.search(r"EXPECTED_BRUSHES\s*=\s*(\d+)", src)
old_entities = re.search(r"EXPECTED_ENTITIES\s*=\s*(\d+)", src)
old_md5 = re.search(r'EXPECTED_MD5\s*=\s*"([0-9a-f]+)"', src)

print("Golden value delta (review before confirming!):")
print(
    f"  EXPECTED_BRUSHES  : {old_brushes.group(1) if old_brushes else '?'} -> {new_brushes}"
)
print(
    f"  EXPECTED_ENTITIES : {old_entities.group(1) if old_entities else '?'} -> {new_entities}"
)
print(f"  EXPECTED_MD5      : {old_md5.group(1) if old_md5 else '?'} -> {new_md5}")

if "--yes" not in sys.argv:
    reply = input(
        "\nHave you reviewed the geometry diff (e.g. `just generate` + "
        "`git diff loyola.map`) and confirmed this change is intentional? "
        "[y/N] "
    )
    if reply.strip().lower() not in ("y", "yes"):
        print("Aborted: golden values NOT updated.")
        sys.exit(1)

src = re.sub(r"(EXPECTED_BRUSHES\s*=\s*)\d+", rf"\g<1>{new_brushes}", src)
src = re.sub(r"(EXPECTED_ENTITIES\s*=\s*)\d+", rf"\g<1>{new_entities}", src)
src = re.sub(r'(EXPECTED_MD5\s*=\s*")[0-9a-f]+"', rf'\g<1>{new_md5}"', src)
path.write_text(src)

print("Updated golden values:")
print(f"  EXPECTED_BRUSHES  = {new_brushes}")
print(f"  EXPECTED_ENTITIES = {new_entities}")
print(f"  EXPECTED_MD5      = {new_md5}")
