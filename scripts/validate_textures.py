import struct
import sys
from pathlib import Path

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from quake_loyola.constants import WORLDSPAWN_FIELDS, Textures


def list_wad_textures(wad_path):
    if not Path(wad_path).exists():
        print(f"Warning: WAD file not found: {wad_path}")
        return []
    with open(wad_path, "rb") as f:
        magic = f.read(4)
        if magic not in (b"WAD2", b"WAD3"):
            print(f"Warning: Invalid WAD magic in {wad_path}: {magic}")
            return []
        num_lumps = struct.unpack("<I", f.read(4))[0]
        dir_ofs = struct.unpack("<I", f.read(4))[0]

        f.seek(dir_ofs)
        names = []
        for _ in range(num_lumps):
            entry = f.read(32)
            if len(entry) < 32:
                break
            name = entry[16:32].split(b"\0")[0].decode("ascii", errors="ignore")
            names.append(name.lower())
        return names


def validate_textures():
    # 1. Get WADs from WORLDSPAWN_FIELDS
    wad_str = WORLDSPAWN_FIELDS.get("wad", "")
    wad_paths = [w.strip() for w in wad_str.split(";") if w.strip()]

    print(f"Loading textures from WADs: {', '.join(wad_paths)}")
    available_textures = set()
    for wp in wad_paths:
        available_textures.update(list_wad_textures(wp))

    print(f"Total available textures: {len(available_textures)}")

    # 2. Get textures from Textures class
    referenced_textures = {}  # name -> field_name
    for attr in dir(Textures):
        if not attr.startswith("_"):
            val = getattr(Textures, attr)
            if isinstance(val, str):
                referenced_textures[val.lower()] = attr

    print(
        f"Checking {len(referenced_textures)} unique textures referenced in constants.py..."
    )

    missing = []
    for tex, attr in referenced_textures.items():
        # Quake handles '*' prefix for animated textures specially,
        # but they should still be in the WAD (usually as *lava1, etc.)
        if tex not in available_textures:
            missing.append((tex, attr))

    if missing:
        print(f"\nFound {len(missing)} MISSING textures:")
        for tex, attr in sorted(missing):
            print(f"  * '{tex}' (referenced by Textures.{attr})")
    else:
        print("\nAll textures found in WADs!")


if __name__ == "__main__":
    validate_textures()
