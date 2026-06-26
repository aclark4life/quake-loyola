"""Pack one or more loose files into a Quake PAK file.

Usage: python3 scripts/make_pak3.py <src_file> <output.pak> [<src2> ...]

The PAK entry name is the basename of each source file.
"""

import os
import struct
import sys

sources = sys.argv[1:-1]  # all args except last
out_path = sys.argv[-1]

files = [(os.path.basename(s), s) for s in sources]
header_size = 12
entry_size = 64

data_size = sum(os.path.getsize(s) for _, s in files)
dir_offset = header_size + data_size

with open(out_path, "wb") as pak:
    pak.write(b"PACK")
    pak.write(struct.pack("<II", dir_offset, len(files) * entry_size))
    for name, path in files:
        with open(path, "rb") as f:
            pak.write(f.read())
    offset = header_size
    for name, path in files:
        size = os.path.getsize(path)
        pak.write(name.encode("ascii").ljust(56, b"\x00"))
        pak.write(struct.pack("<II", offset, size))
        offset += size

print(f"wrote {out_path} ({len(files)} file(s))")
