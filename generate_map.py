#!/usr/bin/env python3
"""Generate loyola_bridge.map — Quake 1 deathmatch map.

Bridge runs East-West along the X axis.
Y = width, Z = height.
"""
import math

# ── Textures ─────────────────────────────────────────────────────────────────
T_STONE = "brown66"
T_FLOOR = "floor0_1"
T_WALL  = "brown25"
T_METAL = "metal5_4"
T_ROCK  = "rock1_1"
T_SKY   = "sky4"

# ── Dimensions ───────────────────────────────────────────────────────────────
BRX1, BRX2 = -512, 512       # Bridge X extent
BRY1, BRY2 = -128, 128       # Bridge Y extent
DZ1, DZ2   = 128, 144        # Deck Z (bottom, top)

WBX1, WBX2 = -768, BRX1      # West building X
EBX1, EBX2 =  BRX2, 768      # East building X
BY1,  BY2  = -192, 192        # Building Y
BZ2        = 320              # Building interior ceiling (bottom of ceil slab)
BCEIL      = BZ2 + 16
BWALL      = 16
BOPEN_Y    = BRY2             # Door opening ±Y = 128

OX1, OX2   = -896, 896        # Outer bounding box
OY1, OY2   = -512, 512
OZ2        = 576
FZ1, FZ2   = -16, 0           # Ravine floor slab

# Pillars
PXS = [-352, -128, 128, 352]
PHW =  16                     # pillar half-width → 32×32 base
PTZ =  240                    # pillar top Z (96 tall above deck)
PCZ =  PTZ + 8                # pillar cap top Z
PCE =  4                      # cap overhang on each side

# Railings
RZ2 = DZ2 + 24                # railing top = 168
RIY =  120; ROY =  136        # inner/outer Y from centre

# Arch gates (entry portals at each end of the span)
ARCH_HX  = 16                 # half-thickness in X → 32-unit thick arch
W_ARCH_X = -448               # west arch centre X
E_ARCH_X =  448               # east arch centre X
A_RIN    =  96                # opening half-width  (inner radius)
A_ROUT   = 128                # outer radius = column outer Y
A_SPRZ   = 288                # spring-line Z (top of columns, base of arch ring)
A_SEGS   =  8                 # voussoir segments (22.5° each, 8 × 22.5 = 180°)

# ── Geometry helpers ─────────────────────────────────────────────────────────
def fv(v):
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:.6g}"

def pt(x, y, z):
    return f"( {fv(x)} {fv(y)} {fv(z)} )"

def face(p1, p2, p3, tex):
    return f"{pt(*p1)} {pt(*p2)} {pt(*p3)} {tex} 0 0 0 1 1"

def box(x1, y1, z1, x2, y2, z2, tex, tt=None, tb=None):
    """Axis-aligned box brush. tt=top texture, tb=bottom texture."""
    tt = tt or tex; tb = tb or tex
    return "{\n" + "\n".join([
        face((x1,y1,z1),(x1,y1,z2),(x1,y2,z1), tex),   # -X
        face((x2,y1,z1),(x2,y2,z1),(x2,y1,z2), tex),   # +X
        face((x1,y1,z1),(x2,y1,z1),(x1,y1,z2), tex),   # -Y
        face((x1,y2,z1),(x1,y2,z2),(x2,y2,z1), tex),   # +Y
        face((x1,y1,z1),(x1,y2,z1),(x2,y1,z1), tb),    # -Z
        face((x1,y1,z2),(x2,y1,z2),(x1,y2,z2), tt),    # +Z
    ]) + "\n}"

def arch_seg(xb, xf, yc, zc, rin, rout, t1d, t2d, tex):
    """Single arch voussoir wedge in the Y-Z plane.
    Angles measured from +Y axis, increasing toward +Z.
    """
    t1, t2 = math.radians(t1d), math.radians(t2d)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    # key points on inner/outer circles at segment midpoint
    yi, zi = yc + rin  * cm, zc + rin  * sm
    yo, zo = yc + rout * cm, zc + rout * sm
    return "{\n" + "\n".join([
        # +X front face  — outward normal +X
        face((xf,yc,zc), (xf,yc+1,zc), (xf,yc,zc+1), tex),
        # -X back face   — outward normal -X
        face((xb,yc,zc), (xb,yc,zc+1), (xb,yc+1,zc), tex),
        # Right radial cut (at θ=t1) — outward normal (0, sin t1, -cos t1)
        face((xf,yc,zc), (xb,yc,zc), (xf, yc+c1, zc+s1), tex),
        # Left  radial cut (at θ=t2) — outward normal (0, -sin t2, cos t2)
        face((xf,yc,zc), (xf, yc+c2, zc+s2), (xb,yc,zc), tex),
        # Inner face (tangent to inner circle at θ_mid) — normal toward centre
        face((xf,yi,zi), (xf, yi-sm, zi+cm), (xb,yi,zi), tex),
        # Outer face (tangent to outer circle at θ_mid) — normal away from centre
        face((xf,yo,zo), (xb,yo,zo), (xf, yo-sm, zo+cm), tex),
    ]) + "\n}"

def arch_gate(cx, tex):
    """Full arch gate: 2 columns + A_SEGS voussoir segments + crown cap."""
    xb, xf = cx - ARCH_HX, cx + ARCH_HX
    yc, zc = 0.0, float(A_SPRZ)
    brushes = []
    # Left column  (Y = -A_ROUT → -A_RIN)
    brushes.append(box(xb, -A_ROUT, DZ2, xf, -A_RIN, A_SPRZ, tex))
    # Right column (Y =  A_RIN  →  A_ROUT)
    brushes.append(box(xb,  A_RIN,  DZ2, xf,  A_ROUT, A_SPRZ, tex))
    # Arch ring voussoirs
    seg = 180.0 / A_SEGS
    for i in range(A_SEGS):
        brushes.append(arch_seg(xb, xf, yc, zc,
                                A_RIN, A_ROUT,
                                i * seg, (i+1) * seg, tex))
    # Crown cap — sits directly on top of the arch ring
    crown_z = A_SPRZ + A_ROUT          # = 416
    brushes.append(box(xb, -A_ROUT, crown_z, xf, A_ROUT, crown_z + 24, tex))
    return brushes

def pillar(cx, cy, tex, cap_tex):
    """Stone pillar + metal cap centred at (cx, cy), standing on deck top."""
    return [
        box(cx-PHW,   cy-PHW,   DZ2, cx+PHW,   cy+PHW,   PTZ, tex),
        box(cx-PHW-PCE, cy-PHW-PCE, PTZ, cx+PHW+PCE, cy+PHW+PCE, PCZ, cap_tex),
    ]

def ent(cls, **kw):
    lines = ["{", f'"classname" "{cls}"']
    for k, v in kw.items():
        lines.append(f'"{k}" "{v}"')
    lines.append("}")
    return "\n".join(lines)

# ── Build worldspawn brushes ─────────────────────────────────────────────────
B = []

# -- Outer bounding box (sky shell sealing the map) --
B.append(box(OX1, OY1, FZ1,     OX2, OY2, FZ2,    T_ROCK))          # ravine floor
B.append(box(OX1, OY1, OZ2-16,  OX2, OY2, OZ2,    T_SKY))           # sky ceiling
B.append(box(OX1, OY2-16, FZ2,  OX2, OY2, OZ2-16, T_SKY))           # N wall
B.append(box(OX1, OY1, FZ2,     OX2, OY1+16, OZ2-16, T_SKY))        # S wall
B.append(box(OX2-16, OY1, FZ2,  OX2, OY2, OZ2-16, T_SKY))           # E wall
B.append(box(OX1, OY1, FZ2,     OX1+16, OY2, OZ2-16, T_SKY))        # W wall

# -- Bridge deck --
B.append(box(BRX1, BRY1, DZ1, BRX2, BRY2, DZ2, T_WALL, tt=T_FLOOR))

# -- West building --
B.append(box(WBX1, BY1, FZ2, WBX2, BY2, DZ1, T_STONE))              # foundation
B.append(box(WBX1, BY1, BZ2, WBX2, BY2, BCEIL, T_STONE))            # ceiling slab
B.append(box(WBX1,        BY1,        DZ2, WBX1+BWALL, BY2,        BZ2, T_STONE))  # W outer wall
B.append(box(WBX1+BWALL,  BY2-BWALL,  DZ2, WBX2,       BY2,        BZ2, T_STONE))  # N wall
B.append(box(WBX1+BWALL,  BY1,        DZ2, WBX2,        BY1+BWALL, BZ2, T_STONE))  # S wall
B.append(box(WBX2-BWALL,  BY1+BWALL,  DZ2, WBX2, -BOPEN_Y,        BZ2, T_STONE))  # E jamb L
B.append(box(WBX2-BWALL,  BOPEN_Y,    DZ2, WBX2,  BY2-BWALL,      BZ2, T_STONE))  # E jamb R

# -- East building (mirror of west) --
B.append(box(EBX1, BY1, FZ2, EBX2, BY2, DZ1, T_STONE))
B.append(box(EBX1, BY1, BZ2, EBX2, BY2, BCEIL, T_STONE))
B.append(box(EBX2-BWALL,  BY1,        DZ2, EBX2, BY2,        BZ2, T_STONE))  # E outer wall
B.append(box(EBX1,        BY2-BWALL,  DZ2, EBX2-BWALL, BY2,  BZ2, T_STONE))  # N wall
B.append(box(EBX1,        BY1,        DZ2, EBX2-BWALL,  BY1+BWALL, BZ2, T_STONE))  # S wall
B.append(box(EBX1,        BY1+BWALL,  DZ2, EBX1+BWALL, -BOPEN_Y,  BZ2, T_STONE))  # W jamb L
B.append(box(EBX1,        BOPEN_Y,    DZ2, EBX1+BWALL,  BY2-BWALL, BZ2, T_STONE))  # W jamb R

# -- 8 pillars (4 north, 4 south) --
for px in PXS:
    B.extend(pillar(px, BRY2, T_STONE, T_METAL))   # north side (Y = +128)
    B.extend(pillar(px, BRY1, T_STONE, T_METAL))   # south side (Y = -128)

# -- Railings (split around arch gate X extents to avoid brush overlap) --
wa_xb = W_ARCH_X - ARCH_HX   # -464
wa_xf = W_ARCH_X + ARCH_HX   # -432
ea_xb = E_ARCH_X - ARCH_HX   #  432
ea_xf = E_ARCH_X + ARCH_HX   #  464

rail_spans = [
    (WBX2,       wa_xb),            # W building → W arch
    (wa_xf,      PXS[0] - PHW),     # W arch     → pillar 0
    (PXS[0]+PHW, PXS[1] - PHW),     # pillar 0   → pillar 1
    (PXS[1]+PHW, PXS[2] - PHW),     # pillar 1   → pillar 2
    (PXS[2]+PHW, PXS[3] - PHW),     # pillar 2   → pillar 3
    (PXS[3]+PHW, ea_xb),            # pillar 3   → E arch
    (ea_xf,      EBX1),             # E arch     → E building
]

for x1, x2 in rail_spans:
    B.append(box(x1,  RIY,  DZ2, x2,  ROY,  RZ2, T_METAL))   # N rail
    B.append(box(x1, -ROY,  DZ2, x2, -RIY,  RZ2, T_METAL))   # S rail

# -- Arch gates --
B.extend(arch_gate(W_ARCH_X, T_STONE))
B.extend(arch_gate(E_ARCH_X, T_STONE))

# ── Assemble worldspawn entity ────────────────────────────────────────────────
worldspawn = (
    '{\n'
    '"classname" "worldspawn"\n'
    '"wad" "quake101.wad"\n'
    '"sky" "sky4"\n'
    '"message" "Loyola Bridge"\n'
    + "\n".join(B) +
    "\n}"
)

# ── Other entities ────────────────────────────────────────────────────────────
E = []

# Deathmatch spawns — 3 per building room, 32 units above floor (Z=176)
for pos in [
    (-680, -80, 176), (-680,  0, 176), (-680,  80, 176),   # west building
    ( 680, -80, 176), ( 680,  0, 176), ( 680,  80, 176),   # east building
]:
    E.append(ent("info_player_deathmatch",
                 origin=f"{pos[0]} {pos[1]} {pos[2]}"))

# Weapons
E.append(ent("weapon_supershotgun",   origin="0 0 152"))      # bridge centre
E.append(ent("weapon_rocketlauncher", origin="-448 0 300"))   # under west arch
E.append(ent("weapon_nailgun",        origin=" 448 0 300"))   # under east arch

# Health
E.append(ent("item_health", origin="-256 0 152"))
E.append(ent("item_health", origin=" 256 0 152"))
E.append(ent("item_health", origin="0 80 152"))

# Armour
E.append(ent("item_armortype", origin="-660 0 152"))

# Lights
lights = [
    (-640,  0, 260, 250),   # west building interior
    ( 640,  0, 260, 250),   # east building interior
    (-352,  0, 220, 200),
    (-128,  0, 220, 200),
    (   0,  0, 220, 200),   # bridge centre
    ( 128,  0, 220, 200),
    ( 352,  0, 220, 200),
    (-448,  0, 360, 220),   # west arch crown
    ( 448,  0, 360, 220),   # east arch crown
]
for lx, ly, lz, ll in lights:
    E.append(ent("light", origin=f"{lx} {ly} {lz}", light=str(ll)))

# ── Write file ────────────────────────────────────────────────────────────────
map_text = worldspawn + "\n" + "\n".join(E) + "\n"

with open("loyola_bridge.map", "w") as fh:
    fh.write(map_text)

print(f"loyola_bridge.map written — {len(B)} worldspawn brushes, {len(E)} entities")
