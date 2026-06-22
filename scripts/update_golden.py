"""Recompute golden values in tests/test_regression.py from the current map."""

import hashlib
import re
import sys
from pathlib import Path

# Ensure the project root is on the path when called from any directory.
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

import generate_map  # noqa: E402

text = generate_map.build_map_text()
new_md5 = hashlib.md5(text.encode()).hexdigest()
mb = generate_map.build_map()
new_brushes = len(mb.brushes)
new_entities = len(mb.entities)

path = root / "tests" / "test_regression.py"
src = path.read_text()
src = re.sub(r"(EXPECTED_BRUSHES\s*=\s*)\d+", rf"\g<1>{new_brushes}", src)
src = re.sub(r"(EXPECTED_ENTITIES\s*=\s*)\d+", rf"\g<1>{new_entities}", src)
src = re.sub(r'(EXPECTED_MD5\s*=\s*")[0-9a-f]+"', rf'\g<1>{new_md5}"', src)
path.write_text(src)

print("Updated golden values:")
print(f"  EXPECTED_BRUSHES  = {new_brushes}")
print(f"  EXPECTED_ENTITIES = {new_entities}")
print(f"  EXPECTED_MD5      = {new_md5}")
