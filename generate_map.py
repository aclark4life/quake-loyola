#!/usr/bin/env python3
"""Generate loyola.map — cross-shaped Quake 1 deathmatch map.

Cross layout (top-down, Z up):
  E-W arm : X=-960..960, Y=-368..368  — has the bridge + east/west buildings
  N-S arm : X=-368..368, Y=-960..960  — open road that passes UNDER the bridge
  Both arms are 736 wide and 1920 long (symmetric cross).
  Bridge deck at Z=128-144 floats over the N-S ground floor (Z=0).
  128 units of clear headroom under the bridge.
"""
import math

# ── Textures ──────────────────────────────────────────────────────────────────
T_STONE = "stone1_5"
T_FLOOR = "afloor1_4"
T_WALL  = "bricka2_1"
T_METAL = "metal5_4"
T_ROCK  = "rock1_2"
T_SKY   = "sky4"
T_LAVA  = "*lava1"
T_PANEL = "*teleport"

# ── Bridge ────────────────────────────────────────────────────────────────────
BRX1, BRX2 = -512, 512
BRY1, BRY2 = -128, 128
DZ1,  DZ2  = 128, 144

# ── Parapets ──────────────────────────────────────────────────────────────────
PAR_W = 24
PAR_Z = DZ2 + 64   # 208

# ── Pillar caps ───────────────────────────────────────────────────────────────
PXS   = [-384, -128, 128, 384]
P_HW  = 20
P_Z   = DZ2 + 96   # 240
P_CE  = 4
P_CAP = P_Z + 8    # 248

# ── Buildings ─────────────────────────────────────────────────────────────────
WBX1, WBX2 = -768, BRX1
EBX1, EBX2 =  BRX2, 768
BY1,  BY2  = -192, 192
BWALL      = 16
BZ2        = 288
BCEIL      = BZ2 + 16
BOPEN_Y    = BRY2  # 128

# ── Arch dims ─────────────────────────────────────────────────────────────────
A_RIN  = 72
A_ROUT = 96
A_SEGS = 8

# ── Cross cave dims ───────────────────────────────────────────────────────────
WALL_T       = 16
OX1, OX2     = -960,  960   # E-W arm length
OY1, OY2     = -368,  368   # E-W arm width
OZ2          = 480
FZ1, FZ2     = -16, 0
NS_X1, NS_X2 = OY1,  OY2   # N-S arm X width  = -368..368 (same as E-W width)
NS_Y1, NS_Y2 = OX1,  OX2   # N-S arm Y length = -960..960 (same as E-W length)

# ── Geometry helpers ──────────────────────────────────────────────────────────
def fv(v):
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:.6g}"

def pt(x, y, z):
    return f"( {fv(x)} {fv(y)} {fv(z)} )"

def face(p1, p2, p3, tex):
    return f"{pt(*p1)} {pt(*p2)} {pt(*p3)} {tex} 0 0 0 1 1"

def box(x1, y1, z1, x2, y2, z2, tex, tt=None, tb=None):
    tt = tt or tex; tb = tb or tex
    return "{\n" + "\n".join([
        face((x1,y1,z1),(x1,y2,z1),(x1,y1,z2), tex),
        face((x2,y1,z1),(x2,y1,z2),(x2,y2,z1), tex),
        face((x1,y1,z1),(x1,y1,z2),(x2,y1,z1), tex),
        face((x1,y2,z1),(x2,y2,z1),(x1,y2,z2), tex),
        face((x1,y1,z1),(x2,y1,z1),(x1,y2,z1), tb),
        face((x1,y1,z2),(x1,y2,z2),(x2,y1,z2), tt),
    ]) + "\n}"

def arch_seg(xb, xf, yc, zc, rin, rout, t1d, t2d, tex):
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

def arch_wall(x1, x2, y1, y2, floor_z, ceil_z, rin, rout, segs, tex):
    sprz = floor_z + rin
    seg  = 180.0 / segs
    brushes = []
    brushes.append(box(x1, y1, floor_z, x2, -rout, ceil_z, tex))
    brushes.append(box(x1, rout, floor_z, x2, y2, ceil_z, tex))
    brushes.append(box(x1, -rout, floor_z, x2, -rin, sprz, tex))
    brushes.append(box(x1,  rin,  floor_z, x2,  rout, sprz, tex))
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

# ── Build world brushes ───────────────────────────────────────────────────────
B = []

# ════════════════════════════════════════════════════════════════════════════════
# CROSS CAVE SHELL
#
# Strategy: 4 solid corner blocks + 4 arm end walls + floors + sky ceilings.
# The inner faces of the corner blocks automatically form the side walls of
# both arms — no extra wall brushes needed.
# ════════════════════════════════════════════════════════════════════════════════

# 4 corner blocks (solid rock — inner faces ARE the arm side walls)
B.append(box(OX1,   OY2,   FZ1, NS_X1, NS_Y2, OZ2, T_ROCK))  # NW corner
B.append(box(NS_X2, OY2,   FZ1, OX2,   NS_Y2, OZ2, T_ROCK))  # NE corner
B.append(box(OX1,   NS_Y1, FZ1, NS_X1, OY1,   OZ2, T_ROCK))  # SW corner
B.append(box(NS_X2, NS_Y1, FZ1, OX2,   OY1,   OZ2, T_ROCK))  # SE corner

# Arm end walls (cap the 4 open ends of the cross)
B.append(box(OX2-WALL_T, OY1,          FZ1, OX2,   OY2,          OZ2, T_ROCK))  # E end
B.append(box(OX1,        OY1,          FZ1, OX1+WALL_T, OY2,     OZ2, T_ROCK))  # W end
B.append(box(NS_X1,      NS_Y2-WALL_T, FZ1, NS_X2, NS_Y2,        OZ2, T_ROCK))  # N end
B.append(box(NS_X1,      NS_Y1,        FZ1, NS_X2, NS_Y1+WALL_T, OZ2, T_ROCK))  # S end

# Floors
B.append(box(OX1,   OY1,          FZ1, OX2,   OY2,          FZ2, T_ROCK))  # E-W arm
B.append(box(NS_X1, OY2,          FZ1, NS_X2, NS_Y2-WALL_T, FZ2, T_ROCK))  # N arm
B.append(box(NS_X1, NS_Y1+WALL_T, FZ1, NS_X2, OY1,          FZ2, T_ROCK))  # S arm

# Sky ceilings
B.append(box(OX1,   OY1,          OZ2-WALL_T, OX2,   OY2,          OZ2, T_SKY))  # E-W
B.append(box(NS_X1, OY2,          OZ2-WALL_T, NS_X2, NS_Y2-WALL_T, OZ2, T_SKY))  # N arm
B.append(box(NS_X1, NS_Y1+WALL_T, OZ2-WALL_T, NS_X2, OY1,          OZ2, T_SKY))  # S arm

# ════════════════════════════════════════════════════════════════════════════════
# BRIDGE (E-W, unchanged)
# ════════════════════════════════════════════════════════════════════════════════
B.append(box(BRX1, BRY1, DZ1, BRX2, BRY2, DZ2, T_WALL, tt=T_FLOOR))

# Parapets
B.append(box(BRX1, BRY2-PAR_W, DZ2, BRX2, BRY2, PAR_Z, T_STONE))
B.append(box(BRX1, BRY1,       DZ2, BRX2, BRY1+PAR_W, PAR_Z, T_STONE))

# Pillar caps + torches
for px in PXS:
    B.append(box(px-P_HW, BRY2-PAR_W, DZ2, px+P_HW, BRY2, P_Z, T_STONE))
    B.append(box(px-P_HW-P_CE, BRY2-PAR_W-P_CE, P_Z,
                 px+P_HW+P_CE, BRY2+P_CE, P_CAP, T_METAL))
    B.append(box(px-P_HW, BRY1, DZ2, px+P_HW, BRY1+PAR_W, P_Z, T_STONE))
    B.append(box(px-P_HW-P_CE, BRY1-P_CE, P_Z,
                 px+P_HW+P_CE, BRY1+PAR_W+P_CE, P_CAP, T_METAL))
    cy_n = BRY2 - PAR_W//2
    cy_s = BRY1 + PAR_W//2
    B.append(box(px-4, cy_n-4, P_CAP, px+4, cy_n+4, P_CAP+10, T_STONE, tt=T_LAVA))
    B.append(box(px-4, cy_s-4, P_CAP, px+4, cy_s+4, P_CAP+10, T_STONE, tt=T_LAVA))

# End arches under bridge
EARCH_RIN   = (BRY2 - BRY1) // 2   # 128
EARCH_ROUT  = EARCH_RIN + 16        # 144
EARCH_ZC    = DZ1 - EARCH_RIN       # 0
EARCH_THICK = 24
seg = 180.0 / A_SEGS
for ex in [BRX1, BRX2]:
    xb = ex - EARCH_THICK // 2
    xf = ex + EARCH_THICK // 2
    for j in range(A_SEGS):
        B.append(arch_seg(xb, xf, 0.0, float(EARCH_ZC),
                          EARCH_RIN, EARCH_ROUT, j*seg, (j+1)*seg, T_STONE))

# Light panels on parapet inner faces
panel_xs = []
all_x = [BRX1] + PXS + [BRX2]
for i in range(len(all_x) - 1):
    panel_xs.append((all_x[i] + all_x[i+1]) // 2)
PANEL_H = DZ2 + 16
PANEL_T = PANEL_H + 20
for px in panel_xs:
    B.append(box(px-8, BRY2-PAR_W-3, PANEL_H, px+8, BRY2-PAR_W, PANEL_T, T_PANEL))
    B.append(box(px-8, BRY1+PAR_W,   PANEL_H, px+8, BRY1+PAR_W+3, PANEL_T, T_PANEL))

# ════════════════════════════════════════════════════════════════════════════════
# EAST + WEST BUILDINGS (unchanged)
# ════════════════════════════════════════════════════════════════════════════════

# West building
B.append(box(WBX1, BY1, FZ2, WBX2, BY2, DZ2, T_STONE))
B.append(box(WBX1+BWALL, BY1, BZ2, WBX2, BY2, BCEIL, T_FLOOR))
B.append(box(WBX1+BWALL, BY2-BWALL, DZ2, WBX2, BY2, BZ2, T_WALL))
B.append(box(WBX1+BWALL, BY1, DZ2, WBX2, BY1+BWALL, BZ2, T_WALL))
B.append(box(WBX2-BWALL, BY1+BWALL, DZ2, WBX2, -BOPEN_Y, BZ2, T_WALL))
B.append(box(WBX2-BWALL, BOPEN_Y, DZ2, WBX2, BY2-BWALL, BZ2, T_WALL))
B.extend(arch_wall(WBX1, WBX1+BWALL, BY1, BY2, DZ2, BZ2, A_RIN, A_ROUT, A_SEGS, T_WALL))

# East building
B.append(box(EBX1, BY1, FZ2, EBX2, BY2, DZ2, T_STONE))
B.append(box(EBX1, BY1, BZ2, EBX2-BWALL, BY2, BCEIL, T_FLOOR))
B.append(box(EBX1, BY2-BWALL, DZ2, EBX2-BWALL, BY2, BZ2, T_WALL))
B.append(box(EBX1, BY1, DZ2, EBX2-BWALL, BY1+BWALL, BZ2, T_WALL))
B.append(box(EBX1, BY1+BWALL, DZ2, EBX1+BWALL, -BOPEN_Y, BZ2, T_WALL))
B.append(box(EBX1, BOPEN_Y, DZ2, EBX1+BWALL, BY2-BWALL, BZ2, T_WALL))
B.extend(arch_wall(EBX2-BWALL, EBX2, BY1, BY2, DZ2, BZ2, A_RIN, A_ROUT, A_SEGS, T_WALL))

# ── Assemble worldspawn ───────────────────────────────────────────────────────
worldspawn = (
    '{\n'
    '"classname" "worldspawn"\n'
    '"wad" "quake101.wad"\n'
    '"message" "Loyola Bridge"\n'
    '"sky" "sky4"\n'
    '"ambient" "40"\n'
    '"dmflags" "128"\n'
    + "\n".join(B) +
    "\n}"
)

# ── Entities ──────────────────────────────────────────────────────────────────
E = []

DECK_Z = DZ2 + 8   # items on bridge deck / building floor
ROAD_Z = FZ2 + 8   # items on ground-level road (N-S corridor)

E.append(ent("info_player_start", origin="-640 0 176"))

# Deathmatch spawns: buildings (deck level) + road (ground level)
for pos in [
    (-640, -80, 176), (-640,  0, 176), (-640,  80, 176),  # west building
    ( 640, -80, 176), ( 640,  0, 176), ( 640,  80, 176),  # east building
    (   0, 550, ROAD_Z), (  60, 700, ROAD_Z), ( -60, 700, ROAD_Z),  # N road
    (   0,-550, ROAD_Z), (  60,-700, ROAD_Z), ( -60,-700, ROAD_Z),  # S road
    ( 200,   0, ROAD_Z), (-200,   0, ROAD_Z),              # under bridge
]:
    E.append(ent("info_player_deathmatch",
                 origin=f"{pos[0]} {pos[1]} {pos[2]}"))

# Weapons
E.append(ent("weapon_rocketlauncher", origin=f"0    0    {DECK_Z}"))  # bridge centre
E.append(ent("weapon_rocketlauncher", origin=f"-640 0    {DECK_Z}"))  # west
E.append(ent("weapon_rocketlauncher", origin=f" 640 0    {DECK_Z}"))  # east
E.append(ent("weapon_rocketlauncher", origin=f"0    600  {ROAD_Z}"))  # N road
E.append(ent("weapon_rocketlauncher", origin=f"0   -600  {ROAD_Z}"))  # S road

# Ammo — bridge
for ax in [-384, -128, 128, 384]:
    E.append(ent("item_rockets", origin=f"{ax} 0 {DECK_Z}"))
for bx in [-60, 60]:
    E.append(ent("item_rockets", origin=f"-640 {bx} {DECK_Z}"))
    E.append(ent("item_rockets", origin=f" 640 {bx} {DECK_Z}"))
# Ammo — road
for ry in [-800, -550, -300, 300, 550, 800]:
    E.append(ent("item_rockets", origin=f"0 {ry} {ROAD_Z}"))

# Health
E.append(ent("item_health", origin=f"-128 0 {DECK_Z}"))
E.append(ent("item_health", origin=f" 128 0 {DECK_Z}"))
E.append(ent("item_health", origin=f"0  450 {ROAD_Z}"))
E.append(ent("item_health", origin=f"0 -450 {ROAD_Z}"))

# Torch lights on pillar caps
for px in PXS:
    cy_n = BRY2 - PAR_W//2
    cy_s = BRY1 + PAR_W//2
    E.append(ent("light", origin=f"{px} {cy_n} {P_CAP+20}", light="300", style="1"))
    E.append(ent("light", origin=f"{px} {cy_s} {P_CAP+20}", light="300", style="1"))

# Light panel glow
for px in panel_xs:
    E.append(ent("light", origin=f"{px} {BRY2-PAR_W-8} {PANEL_H+10}", light="180"))
    E.append(ent("light", origin=f"{px} {BRY1+PAR_W+8} {PANEL_H+10}", light="180"))

# Building interior lights
E.append(ent("light", origin=f"-640 0 260", light="350"))
E.append(ent("light", origin=f" 640 0 260", light="350"))

# Bridge end arch lights
for ex in [BRX1, BRX2]:
    E.append(ent("light", origin=f"{ex} 0 {DZ1-20}", light="220"))

# Under-bridge road lights (Z=64 — well below the deck at 128)
for rx in [-280, 0, 280]:
    E.append(ent("light", origin=f"{rx} 0 64", light="240"))

# N/S road arm lights
for ry in [-800, -600, -420, 420, 600, 800]:
    E.append(ent("light", origin=f"0 {ry} 300", light="320"))

# ── Write file ────────────────────────────────────────────────────────────────
map_text = worldspawn + "\n" + "\n".join(E) + "\n"
with open("loyola.map", "w") as fh:
    fh.write(map_text)

print(f"loyola.map written — {len(B)} worldspawn brushes, {len(E)} entities")
