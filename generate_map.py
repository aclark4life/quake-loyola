#!/usr/bin/env python3
"""Generate loyola.map — Quake 1 deathmatch map.

Bridge runs East-West along the X axis.
Y = width (N/S), Z = height.

Structure matches reference screenshots:
- Open bridge span with stone parapet walls + pillar caps + torches
- Bridge supported by rectangular piers below the deck
- Rocky cave environment (no sky box)
- Semicircular arches in the outer building walls (cave-facing)
"""
import math

# ── Textures ─────────────────────────────────────────────────────────────────
T_STONE = "stone1_5"     # parapets, pillar caps, arch ring
T_FLOOR = "afloor1_4"    # bridge deck top, building floor/ceiling
T_WALL  = "bricka2_1"    # building walls, arch jambs
T_METAL = "metal5_4"     # pillar cap overhang trim
T_ROCK  = "rock1_2"      # cave outer walls
T_SKY   = "sky4"         # open sky above bridge
T_LAVA  = "*lava1"       # torch flame (fullbright orange)
T_PANEL = "*teleport"    # light panel (fullbright blue)

# ── Bridge dimensions ────────────────────────────────────────────────────────
BRX1, BRX2 = -512, 512       # Bridge X extent
BRY1, BRY2 = -128, 128       # Bridge Y extent (256 wide)
DZ1,  DZ2  = 128, 144        # Deck slab (bottom, top)

# ── Parapet walls (solid stone sides on the bridge span) ─────────────────────
PAR_W = 24                   # parapet Y-thickness
PAR_Z = DZ2 + 64             # parapet top Z = 208

# ── Pillar caps (square posts on top of parapets at regular X intervals) ─────
PXS   = [-384, -128, 128, 384]
P_HW  = 20                   # pillar half-Y (40 wide, flush with parapet outer face)
P_Z   = DZ2 + 96             # pillar post top Z = 240
P_CE  = 4                    # cap overhang each side in Y
P_CAP = P_Z + 8              # cap slab top Z = 248

# ── Bridge piers (rectangular supports below deck at pillar X positions) ─────
PIER_HW = 16                 # pier half-width in X and Y

# ── Buildings ────────────────────────────────────────────────────────────────
WBX1, WBX2 = -768, BRX1      # West building X: -768 to -512
EBX1, EBX2 =  BRX2, 768      # East building X:  512 to 768
BY1,  BY2  = -192, 192        # Building Y
BWALL      = 16               # Wall thickness
BZ2        = 288              # Building ceiling bottom
BCEIL      = BZ2 + 16         # Building ceiling top = 304
BOPEN_Y    = BRY2             # Bridge-side door half-width = 128

# ── Semicircular arch in outer building walls (cave-facing) ──────────────────
# West building: arch in WEST outer wall (WBX1 to WBX1+BWALL)
# East building: arch in EAST outer wall (EBX2-BWALL to EBX2)
# A_RIN = 72 → spring line at DZ2 + A_RIN = 216
#            → crown at 216 + 72 = 288 = BZ2 (arch crown exactly meets ceiling)
A_RIN  = 72                   # arch inner radius (half-width of opening)
A_ROUT = 96                   # arch outer radius (ring = 24 units thick)
A_SEGS = 8                    # voussoir segments
A_SPRZ = DZ2 + A_RIN          # spring line Z = 216

# ── Outer cave box ───────────────────────────────────────────────────────────
OX1, OX2 = -960, 960
OY1, OY2 = -368, 368          # narrower than bridge span for cave feel
OZ2      = 480                # cave ceiling
FZ1, FZ2 = -16, 0             # cave floor slab

# ── Geometry helpers ─────────────────────────────────────────────────────────
def fv(v):
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:.6g}"

def pt(x, y, z):
    return f"( {fv(x)} {fv(y)} {fv(z)} )"

def face(p1, p2, p3, tex):
    return f"{pt(*p1)} {pt(*p2)} {pt(*p3)} {tex} 0 0 0 1 1"

def box(x1, y1, z1, x2, y2, z2, tex, tt=None, tb=None):
    """Axis-aligned box brush. Face normals OUTWARD (ericw-tools convention)."""
    tt = tt or tex; tb = tb or tex
    return "{\n" + "\n".join([
        face((x1,y1,z1),(x1,y2,z1),(x1,y1,z2), tex),   # -X
        face((x2,y1,z1),(x2,y1,z2),(x2,y2,z1), tex),   # +X
        face((x1,y1,z1),(x1,y1,z2),(x2,y1,z1), tex),   # -Y
        face((x1,y2,z1),(x2,y2,z1),(x1,y2,z2), tex),   # +Y
        face((x1,y1,z1),(x2,y1,z1),(x1,y2,z1), tb),    # -Z
        face((x1,y1,z2),(x1,y2,z2),(x2,y1,z2), tt),    # +Z
    ]) + "\n}"

def arch_seg(xb, xf, yc, zc, rin, rout, t1d, t2d, tex):
    """Single arch voussoir wedge in the Y-Z plane. Face normals OUTWARD."""
    t1, t2 = math.radians(t1d), math.radians(t2d)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    yi, zi = yc + rin  * cm, zc + rin  * sm
    yo, zo = yc + rout * cm, zc + rout * sm
    return "{\n" + "\n".join([
        face((xf,yc,zc), (xf,yc,zc+1), (xf,yc+1,zc), tex),
        face((xb,yc,zc), (xb,yc+1,zc), (xb,yc,zc+1), tex),
        face((xf,yc,zc), (xf, yc+c1, zc+s1), (xb,yc,zc), tex),
        face((xf,yc,zc), (xb,yc,zc), (xf, yc+c2, zc+s2), tex),
        face((xf,yi,zi), (xb,yi,zi), (xf, yi-sm, zi+cm), tex),
        face((xf,yo,zo), (xf, yo-sm, zo+cm), (xb,yo,zo), tex),
    ]) + "\n}"

def arch_seg_xz(yb, yf, xc, zc, rin, rout, t1d, t2d, tex):
    """Arch voussoir in the X-Z plane (arch spans E-W, depth in Y).
    Angles: 0=+X, 90=+Z. Crown at 90° faces upward. Face normals OUTWARD."""
    t1, t2 = math.radians(t1d), math.radians(t2d)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    xi, zi = xc + rin  * cm, zc + rin  * sm
    xo, zo = xc + rout * cm, zc + rout * sm
    return "{\n" + "\n".join([
        face((xc,   yf, zc),     (xc+1, yf, zc),     (xc,   yf, zc+1),   tex),  # +Y
        face((xc,   yb, zc),     (xc,   yb, zc+1),   (xc+1, yb, zc),     tex),  # -Y
        face((xc,   yf, zc),     (xc,   yb, zc),     (xc+c1,yf, zc+s1),  tex),  # right radial
        face((xc,   yf, zc),     (xc+c2,yf, zc+s2),  (xc,   yb, zc),     tex),  # left radial
        face((xi,   yf, zi),     (xi-sm,yf, zi+cm),   (xi,   yb, zi),     tex),  # inner
        face((xo,   yf, zo),     (xo,   yb, zo),     (xo-sm,yf, zo+cm),  tex),  # outer
    ]) + "\n}"

def arch_wall(x1, x2, y1, y2, floor_z, ceil_z, rin, rout, segs, tex):
    """Wall with centred semicircular arch opening.
    rin must satisfy: floor_z + 2*rin == ceil_z (crown meets ceiling exactly).
    Returns list of brush strings."""
    sprz = floor_z + rin
    seg  = 180.0 / segs
    brushes = []
    # Solid sections outside arch ring
    brushes.append(box(x1, y1, floor_z, x2, -rout, ceil_z, tex))
    brushes.append(box(x1, rout, floor_z, x2, y2, ceil_z, tex))
    # Straight jambs (±rin to ±rout, below spring line)
    brushes.append(box(x1, -rout, floor_z, x2, -rin, sprz, tex))
    brushes.append(box(x1,  rin,  floor_z, x2,  rout, sprz, tex))
    # Arch ring voussoirs
    for i in range(segs):
        brushes.append(arch_seg(x1, x2, 0.0, float(sprz),
                                rin, rout, i*seg, (i+1)*seg, tex))
    return brushes

def ent(cls, **kw):
    lines = ["{", f'"classname" "{cls}"']
    for k, v in kw.items():
        lines.append(f'"{k}" "{v}"')
    lines.append("}")
    return "\n".join(lines)

# ── Build worldspawn brushes ─────────────────────────────────────────────────
B = []

# ── Outer cave box (rock walls seal the map) ─────────────────────────────────
B.append(box(OX1, OY1, FZ1,     OX2, OY2, FZ2,    T_ROCK))   # cave floor
B.append(box(OX1, OY1, OZ2-16,  OX2, OY2, OZ2,    T_SKY))    # sky ceiling (open sky above bridge)
B.append(box(OX1, OY2-16, FZ1,  OX2, OY2, OZ2,    T_ROCK))   # N cave wall
B.append(box(OX1, OY1, FZ1,     OX2, OY1+16, OZ2, T_ROCK))   # S cave wall
B.append(box(OX2-16, OY1, FZ1,  OX2, OY2, OZ2,    T_ROCK))   # E cave wall
B.append(box(OX1, OY1, FZ1,     OX1+16, OY2, OZ2, T_ROCK))   # W cave wall

# ── Bridge deck ───────────────────────────────────────────────────────────────
B.append(box(BRX1, BRY1, DZ1, BRX2, BRY2, DZ2, T_WALL, tt=T_FLOOR))

# ── Parapet walls (continuous N/S strips along bridge span) ──────────────────
B.append(box(BRX1, BRY2-PAR_W, DZ2, BRX2, BRY2, PAR_Z, T_STONE))  # N parapet
B.append(box(BRX1, BRY1, DZ2, BRX2, BRY1+PAR_W, PAR_Z, T_STONE))  # S parapet

# ── Pillar caps (4 per side, N and S; taller and wider than parapet) ─────────
for px in PXS:
    # North side (outer face flush with BRY2)
    B.append(box(px-P_HW, BRY2-PAR_W, DZ2, px+P_HW, BRY2, P_Z, T_STONE))
    B.append(box(px-P_HW-P_CE, BRY2-PAR_W-P_CE, P_Z,
                 px+P_HW+P_CE, BRY2+P_CE, P_CAP, T_METAL))
    # South side (outer face flush with BRY1)
    B.append(box(px-P_HW, BRY1, DZ2, px+P_HW, BRY1+PAR_W, P_Z, T_STONE))
    B.append(box(px-P_HW-P_CE, BRY1-P_CE, P_Z,
                 px+P_HW+P_CE, BRY1+PAR_W+P_CE, P_CAP, T_METAL))
    # Torch flame brush on top of each cap (fullbright lava top = visible flame)
    cy_n = BRY2 - PAR_W//2          # north cap centre Y = 116
    cy_s = BRY1 + PAR_W//2          # south cap centre Y = -116
    B.append(box(px-4, cy_n-4, P_CAP, px+4, cy_n+4, P_CAP+10, T_STONE, tt=T_LAVA))
    B.append(box(px-4, cy_s-4, P_CAP, px+4, cy_s+4, P_CAP+10, T_STONE, tt=T_LAVA))

# ── End arches under the bridge (Y-Z plane, one at each bridge end) ──────────
# Each arch spans the bridge Y width (BRY1 to BRY2 = 256u), crown at DZ1.
# Uses arch_seg (Y-Z plane, depth in X).
EARCH_RIN  = (BRY2 - BRY1) // 2   # 128 — half bridge width
EARCH_ROUT = EARCH_RIN + 16        # 144
EARCH_ZC   = DZ1 - EARCH_RIN      # spring line Z = 0 (crown = DZ1 = 128)
EARCH_THICK = 24                    # arch ring depth in X
seg = 180.0 / A_SEGS
for ex, direction in [(BRX1, "west"), (BRX2, "east")]:
    xb = ex - EARCH_THICK // 2
    xf = ex + EARCH_THICK // 2
    for j in range(A_SEGS):
        B.append(arch_seg(xb, xf, 0.0, float(EARCH_ZC),
                          EARCH_RIN, EARCH_ROUT, j*seg, (j+1)*seg, T_STONE))

# ── Light panels (bright *teleport brushes on inner parapet face) ─────────────
# Between every pair of adjacent pillar caps, centred, at eye-level on parapet
panel_xs = []
all_x = [BRX1] + PXS + [BRX2]
for i in range(len(all_x) - 1):
    panel_xs.append((all_x[i] + all_x[i+1]) // 2)
PANEL_H = DZ2 + 16   # panel bottom Z
PANEL_T = PANEL_H + 20  # panel top Z
for px in panel_xs:
    # North parapet inner face at Y = BRY2-PAR_W = 104
    B.append(box(px-8, BRY2-PAR_W-3, PANEL_H, px+8, BRY2-PAR_W, PANEL_T, T_PANEL))
    # South parapet inner face at Y = BRY1+PAR_W = -104
    B.append(box(px-8, BRY1+PAR_W, PANEL_H, px+8, BRY1+PAR_W+3, PANEL_T, T_PANEL))

# ── West building ─────────────────────────────────────────────────────────────
B.append(box(WBX1, BY1, FZ2, WBX2, BY2, DZ2, T_STONE))               # foundation
B.append(box(WBX1+BWALL, BY1, BZ2, WBX2, BY2, BCEIL, T_FLOOR))       # ceiling (excl. arch wall X)
B.append(box(WBX1+BWALL, BY2-BWALL, DZ2, WBX2, BY2, BZ2, T_WALL))   # N wall
B.append(box(WBX1+BWALL, BY1, DZ2, WBX2, BY1+BWALL, BZ2, T_WALL))   # S wall
# East wall (bridge side): jambs only — opening matches bridge width ±128
B.append(box(WBX2-BWALL, BY1+BWALL, DZ2, WBX2, -BOPEN_Y, BZ2, T_WALL))  # E jamb S
B.append(box(WBX2-BWALL, BOPEN_Y, DZ2, WBX2, BY2-BWALL, BZ2, T_WALL))   # E jamb N
# West wall (cave side): semicircular arch opening
B.extend(arch_wall(WBX1, WBX1+BWALL, BY1, BY2, DZ2, BZ2,
                   A_RIN, A_ROUT, A_SEGS, T_WALL))

# ── East building (mirror of west) ───────────────────────────────────────────
B.append(box(EBX1, BY1, FZ2, EBX2, BY2, DZ2, T_STONE))
B.append(box(EBX1, BY1, BZ2, EBX2-BWALL, BY2, BCEIL, T_FLOOR))
B.append(box(EBX1, BY2-BWALL, DZ2, EBX2-BWALL, BY2, BZ2, T_WALL))   # N wall
B.append(box(EBX1, BY1, DZ2, EBX2-BWALL, BY1+BWALL, BZ2, T_WALL))   # S wall
# West wall (bridge side): jambs only
B.append(box(EBX1, BY1+BWALL, DZ2, EBX1+BWALL, -BOPEN_Y, BZ2, T_WALL))  # W jamb S
B.append(box(EBX1, BOPEN_Y, DZ2, EBX1+BWALL, BY2-BWALL, BZ2, T_WALL))   # W jamb N
# East wall (cave side): semicircular arch opening
B.extend(arch_wall(EBX2-BWALL, EBX2, BY1, BY2, DZ2, BZ2,
                   A_RIN, A_ROUT, A_SEGS, T_WALL))

# ── Assemble worldspawn entity ────────────────────────────────────────────────
worldspawn = (
    '{\n'
    '"classname" "worldspawn"\n'
    '"wad" "quake101.wad"\n'
    '"message" "Loyola Bridge"\n'
    '"sky" "sky4"\n'
    '"ambient" "40"\n'
    + "\n".join(B) +
    "\n}"
)

# ── Other entities ────────────────────────────────────────────────────────────
E = []

# Single-player start (required to avoid crash on connect)
E.append(ent("info_player_start", origin="-640 0 176"))

# Deathmatch spawns
for pos in [
    (-640, -80, 176), (-640,  0, 176), (-640,  80, 176),   # west building
    ( 640, -80, 176), ( 640,  0, 176), ( 640,  80, 176),   # east building
]:
    E.append(ent("info_player_deathmatch",
                 origin=f"{pos[0]} {pos[1]} {pos[2]}"))

# Weapons
E.append(ent("weapon_supershotgun",   origin="0 0 152"))
E.append(ent("weapon_rocketlauncher", origin="-256 0 152"))
E.append(ent("weapon_nailgun",        origin=" 256 0 152"))

# Health & armour
E.append(ent("item_health", origin="-128 0 152"))
E.append(ent("item_health", origin=" 128 0 152"))
E.append(ent("item_health", origin="0 80 152"))
E.append(ent("item_armortype", origin="-640 0 152"))

# Torches on pillar caps — flickering lights at torch brush position
for px in PXS:
    cy_n = BRY2 - PAR_W//2
    cy_s = BRY1 + PAR_W//2
    E.append(ent("light", origin=f"{px} {cy_n} {P_CAP+20}",
                 light="300", style="1"))
    E.append(ent("light", origin=f"{px} {cy_s} {P_CAP+20}",
                 light="300", style="1"))

# Light panel glow (steady, close to panel face)
for px in panel_xs:
    E.append(ent("light", origin=f"{px} {BRY2-PAR_W-8} {PANEL_H+10}", light="180"))
    E.append(ent("light", origin=f"{px} {BRY1+PAR_W+8} {PANEL_H+10}", light="180"))

# Building interior lights (bright, steady)
for lx, ll in [(-640, 350), (640, 350)]:
    E.append(ent("light", origin=f"{lx} 0 260", light=str(ll)))

# Lights at bridge ends, illuminating the end arches
for ex in [BRX1, BRX2]:
    E.append(ent("light", origin=f"{ex} 0 {DZ1 - 20}", light="220"))

# ── Write file ────────────────────────────────────────────────────────────────
map_text = worldspawn + "\n" + "\n".join(E) + "\n"

with open("loyola.map", "w") as fh:
    fh.write(map_text)

print(f"loyola.map written — {len(B)} worldspawn brushes, {len(E)} entities")
