#!/usr/bin/env python3
"""Generate loyola.map — cross-shaped Quake 1 deathmatch map.

Bridge matches Loyola Maryland campus bridge:
  - Parabolic arch deck (rises 64 units at centre)
  - Stone pillar posts (stone1_5) at regular intervals
  - Cement parapet walls (wbrick1_5) between pillars
"""

import math

# ── Textures ──────────────────────────────────────────────────────────────────
T_STONE = "stone1_5"  # pillar posts + arch ring
T_FLOOR = "afloor1_4"  # deck top surface
T_CEMENT = "wbrick1_5"  # parapet / bridge walls (cement look)
T_WALL = "bricka2_1"  # building walls
T_METAL = "metal5_4"  # pillar cap trim
T_ROCK = "rock1_2"  # cave outer shell
T_SKY = "sky4"  # open sky ceiling
T_LAVA = "*lava1"  # torch flame
T_LIGHT_PANEL = "light1_1"  # light panel
T_TELEPORT = "*teleport"  # teleport effect

# ── Bridge spine ──────────────────────────────────────────────────────────────
BRX1, BRX2 = -512, 512
BRY1, BRY2 = -128, 128
DZ1, DZ2 = 128, 144  # flat deck bottom / top (arch offsets added on top)

# ── Arch profile ──────────────────────────────────────────────────────────────
ARCH_RISE = 64  # centre rises 64 units above ends
ARCH_SEGS = 16  # segments approximating the curve
SEG_W = (BRX2 - BRX1) // ARCH_SEGS  # 64 units per segment


def arch_z(x):
    """Z offset above flat datum for parabolic arch at x."""
    xc = (BRX1 + BRX2) / 2.0
    half = (BRX2 - BRX1) / 2.0
    return ARCH_RISE * max(0.0, 1.0 - ((x - xc) / half) ** 2)


def dtop(x):
    return DZ2 + arch_z(x)  # deck surface Z at x


def dbot(x):
    return DZ1 + arch_z(x)  # deck bottom  Z at x


# ── Parapet + pillar heights (above deck surface) ─────────────────────────────
PAR_H = 32  # parapet wall height above deck
PIL_EXTRA = 48  # how much pillar post sticks above parapet top
PIL_CAP_H = 8  # cap slab height
P_HW = 20  # pillar half-width in X
P_CE = 4  # cap overhang each side

# ── Pillar X positions ────────────────────────────────────────────────────────
PXS = [-384, -128, 128, 384]

# ── Buildings ─────────────────────────────────────────────────────────────────
WBX1, WBX2 = -768, BRX1
EBX1, EBX2 = BRX2, 768
BY1, BY2 = -192, 192
BWALL = 16
BZ2 = 288
BCEIL = BZ2 + 16
BOPEN_Y = BRY2  # 128

# ── Arch ring (building outer walls) ─────────────────────────────────────────
A_RIN = 72
A_ROUT = 96
A_SEGS = 8

# ── Cross cave dims ───────────────────────────────────────────────────────────
WALL_T = 16
OX1, OX2 = -960, 960
OY1, OY2 = -368, 368
OZ2 = 480
FZ1, FZ2 = -16, 0
NS_X1, NS_X2 = OY1, OY2  # N-S arm X = -368..368
NS_Y1, NS_Y2 = OX1, OX2  # N-S arm Y = -960..960


# ── Geometry helpers ──────────────────────────────────────────────────────────
def fv(v):
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:.6g}"


def pt(x, y, z):
    return f"( {fv(x)} {fv(y)} {fv(z)} )"


def face(p1, p2, p3, tex):
    return f"{pt(*p1)} {pt(*p2)} {pt(*p3)} {tex} 0 0 0 1 1"


def box(x1, y1, z1, x2, y2, z2, tex, tt=None, tb=None):
    tt = tt or tex
    tb = tb or tex
    return (
        "{\n"
        + "\n".join(
            [
                face((x1, y1, z1), (x1, y2, z1), (x1, y1, z2), tex),
                face((x2, y1, z1), (x2, y1, z2), (x2, y2, z1), tex),
                face((x1, y1, z1), (x1, y1, z2), (x2, y1, z1), tex),
                face((x1, y2, z1), (x2, y2, z1), (x1, y2, z2), tex),
                face((x1, y1, z1), (x2, y1, z1), (x1, y2, z1), tb),
                face((x1, y1, z2), (x1, y2, z2), (x2, y1, z2), tt),
            ]
        )
        + "\n}"
    )


def ramp_slab(x1, x2, y1, y2, zb1, zb2, zt1, zt2, tex, tt=None, tb=None):
    """Prismatic slab whose bottom and top faces are sloped in the X direction.
    zb1/zt1 = bottom/top Z at x=x1;  zb2/zt2 = bottom/top Z at x=x2."""
    tt = tt or tex
    tb = tb or tex
    return (
        "{\n"
        + "\n".join(
            [
                face((x1, y1, zb1), (x1, y2, zb1), (x1, y1, zt1), tex),  # -X
                face((x2, y1, zb2), (x2, y1, zt2), (x2, y2, zb2), tex),  # +X
                face((x1, y1, zb1), (x1, y1, zt1), (x2, y1, zb2), tex),  # -Y
                face((x1, y2, zb1), (x2, y2, zb2), (x1, y2, zt1), tex),  # +Y
                face((x1, y1, zb1), (x2, y1, zb2), (x1, y2, zb1), tb),  # sloped bottom
                face((x1, y1, zt1), (x1, y2, zt1), (x2, y1, zt2), tt),  # sloped top
            ]
        )
        + "\n}"
    )


def arch_seg(xb, xf, yc, zc, rin, rout, t1d, t2d, tex):
    t1, t2 = math.radians(t1d), math.radians(t2d)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    yi, zi = yc + rin * cm, zc + rin * sm
    yo, zo = yc + rout * cm, zc + rout * sm
    return (
        "{\n"
        + "\n".join(
            [
                face((xf, yc, zc), (xf, yc, zc + 1), (xf, yc + 1, zc), tex),
                face((xb, yc, zc), (xb, yc + 1, zc), (xb, yc, zc + 1), tex),
                face((xf, yc, zc), (xf, yc + c1, zc + s1), (xb, yc, zc), tex),
                face((xf, yc, zc), (xb, yc, zc), (xf, yc + c2, zc + s2), tex),
                face((xf, yi, zi), (xb, yi, zi), (xf, yi - sm, zi + cm), tex),
                face((xf, yo, zo), (xf, yo - sm, zo + cm), (xb, yo, zo), tex),
            ]
        )
        + "\n}"
    )


def arch_wall(x1, x2, y1, y2, floor_z, ceil_z, rin, rout, segs, tex, stilt_h=None):
    """Stone wall with arched opening centred at Y=0.

    stilt_h: height of straight sides before the arch springs (defaults to rin,
             giving a plain semicircle; set > rin for a tall stilted/gothic arch).
    """
    stilt_h = rin if stilt_h is None else stilt_h
    sprz = floor_z + stilt_h  # Z where arch springs
    seg = 180.0 / segs
    brushes = []
    brushes.append(box(x1, y1, floor_z, x2, -rout, ceil_z, tex))
    brushes.append(box(x1, rout, floor_z, x2, y2, ceil_z, tex))
    brushes.append(box(x1, -rout, floor_z, x2, -rin, sprz, tex))
    brushes.append(box(x1, rin, floor_z, x2, rout, sprz, tex))
    for i in range(segs):
        brushes.append(
            arch_seg(x1, x2, 0.0, float(sprz), rin, rout, i * seg, (i + 1) * seg, tex)
        )
    return brushes


def ent(cls, **kw):
    lines = ["{", f'"classname" "{cls}"']
    for k, v in kw.items():
        lines.append(f'"{k}" "{v}"')
    lines.append("}")
    return "\n".join(lines)


def brush_ent(cls, brushes, **kw):
    lines = ["{", f'"classname" "{cls}"']
    for k, v in kw.items():
        lines.append(f'"{k}" "{v}"')
    for b in brushes:
        # Each b is a string "{\n...\n}" from box/ramp_slab
        # Keep the braces for the brush within the entity
        lines.append(b)
    lines.append("}")
    return "\n".join(lines)


# ── Build world brushes ───────────────────────────────────────────────────────
B = []

# ════════════════════════════════════════════════════════════════════════════════
# CROSS CAVE SHELL — 4 corner blocks + N/S end walls + floors + sky ceilings
# ════════════════════════════════════════════════════════════════════════════════
B.append(box(OX1, OY2, FZ1, NS_X1, NS_Y2, OZ2, T_ROCK))  # NW corner
B.append(box(NS_X2, OY2, FZ1, OX2, NS_Y2, OZ2, T_ROCK))  # NE corner
B.append(box(OX1, NS_Y1, FZ1, NS_X1, OY1, OZ2, T_ROCK))  # SW corner
B.append(box(NS_X2, NS_Y1, FZ1, OX2, OY1, OZ2, T_ROCK))  # SE corner

# Restore rock walls at the E and W ends of the pathways
B.append(box(OX2 - WALL_T, OY1, FZ1, OX2, OY2, OZ2, T_ROCK))  # E end
B.append(box(OX1, OY1, FZ1, OX1 + WALL_T, OY2, OZ2, T_ROCK))  # W end
B.append(box(NS_X1, NS_Y2 - WALL_T, FZ1, NS_X2, NS_Y2, OZ2, T_ROCK))  # N end
B.append(box(NS_X1, NS_Y1, FZ1, NS_X2, NS_Y1 + WALL_T, OZ2, T_ROCK))  # S end

B.append(box(OX1, OY1, FZ1, OX2, OY2, FZ2, T_ROCK))  # E-W floor
B.append(box(NS_X1, OY2, FZ1, NS_X2, NS_Y2 - WALL_T, FZ2, T_ROCK))  # N arm floor
B.append(box(NS_X1, NS_Y1 + WALL_T, FZ1, NS_X2, OY1, FZ2, T_ROCK))  # S arm floor

# E-W sky ceiling (single brush — keeps BSP solid)
B.append(box(OX1, OY1, OZ2 - WALL_T, OX2, OY2, OZ2, T_SKY))  # E-W sky
B.append(box(NS_X1, OY2, OZ2 - WALL_T, NS_X2, NS_Y2 - WALL_T, OZ2, T_SKY))  # N arm sky
B.append(box(NS_X1, NS_Y1 + WALL_T, OZ2 - WALL_T, NS_X2, OY1, OZ2, T_SKY))  # S arm sky

# ════════════════════════════════════════════════════════════════════════════════
# ARCHED BRIDGE DECK — extended to map boundaries OX1, OX2
# ════════════════════════════════════════════════════════════════════════════════
# Extend bridge deck from BRX1 to OX1 and BRX2 to OX2
B.append(box(OX1, BRY1, DZ1, BRX1, BRY2, DZ2, T_STONE, tt=T_FLOOR, tb=T_FLOOR))
B.append(box(BRX2, BRY1, DZ1, OX2, BRY2, DZ2, T_STONE, tt=T_FLOOR, tb=T_FLOOR))

for i in range(ARCH_SEGS):
    sx1 = BRX1 + i * SEG_W
    sx2 = sx1 + SEG_W
    B.append(
        ramp_slab(
            sx1,
            sx2,
            BRY1,
            BRY2,
            dbot(sx1),
            dbot(sx2),
            dtop(sx1),
            dtop(sx2),
            T_STONE,
            tt=T_FLOOR,
            tb=T_FLOOR,
        )
    )

# ── Parapet walls — extended to map boundaries ───────────────────────────────
# Extend parapets from BRX1 to OX1 and BRX2 to OX2
B.append(box(OX1, BRY2 - 24, DZ2, BRX1, BRY2, DZ2 + PAR_H, T_CEMENT))  # North
B.append(box(OX1, BRY1, DZ2, BRX1, BRY1 + 24, DZ2 + PAR_H, T_CEMENT))  # South
B.append(box(BRX2, BRY2 - 24, DZ2, OX2, BRY2, DZ2 + PAR_H, T_CEMENT))  # North
B.append(box(BRX2, BRY1, DZ2, OX2, BRY1 + 24, DZ2 + PAR_H, T_CEMENT))  # South

for i in range(ARCH_SEGS):
    sx1 = BRX1 + i * SEG_W
    sx2 = sx1 + SEG_W
    pb1, pb2 = dtop(sx1), dtop(sx2)  # parapet base follows deck top
    pt1, pt2 = pb1 + PAR_H, pb2 + PAR_H  # parapet top = base + PAR_H
    # North parapet
    B.append(ramp_slab(sx1, sx2, BRY2 - 24, BRY2, pb1, pb2, pt1, pt2, T_CEMENT))
    # South parapet
    B.append(ramp_slab(sx1, sx2, BRY1, BRY1 + 24, pb1, pb2, pt1, pt2, T_CEMENT))


# ── Pillar posts (stone, tall — sit on deck surface at each arch height) ──────
for px in PXS:
    pbase = dtop(px)  # base = deck surface at this X
    ppar = pbase + PAR_H  # parapet top
    ppil = ppar + PIL_EXTRA  # pillar post top
    pcap = ppil + PIL_CAP_H  # cap slab top
    cy_n = BRY2 - 12  # north cap centre Y
    cy_s = BRY1 + 12  # south cap centre Y

    # North pillar post + cap
    B.append(box(px - P_HW, BRY2 - 24, pbase, px + P_HW, BRY2, ppil, T_STONE))
    B.append(
        box(
            px - P_HW - P_CE,
            BRY2 - 24 - P_CE,
            ppil,
            px + P_HW + P_CE,
            BRY2 + P_CE,
            pcap,
            T_STONE,
        )
    )
    # South pillar post + cap
    B.append(box(px - P_HW, BRY1, pbase, px + P_HW, BRY1 + 24, ppil, T_STONE))
    B.append(
        box(
            px - P_HW - P_CE,
            BRY1 - P_CE,
            ppil,
            px + P_HW + P_CE,
            BRY1 + 24 + P_CE,
            pcap,
            T_STONE,
        )
    )
    # Torch flames on cap top
    B.append(
        box(px - 4, cy_n - 4, pcap, px + 4, cy_n + 4, pcap + 10, T_STONE, tt=T_LAVA)
    )
    B.append(
        box(px - 4, cy_s - 4, pcap, px + 4, cy_s + 4, pcap + 10, T_STONE, tt=T_LAVA)
    )

# ── End abutments restored as supports (capped at deck height DZ2) ──────────────
EARCH_RIN = 64
EARCH_ROUT = 80  # ring 16 units thick
EARCH_STILT = 64  # straight sides; crown = stilt + rin = 128 = DZ1
EARCH_CROWN = EARCH_STILT + EARCH_RIN  # 128
EARCH_CEIL = DZ2  # top of abutment wall (level with bridge deck)
EARCH_T = 40  # arch thickness in X
for ex, sign in [(BRX1, 1), (BRX2, -1)]:
    xb = ex if sign == 1 else ex - EARCH_T
    xf = ex + EARCH_T if sign == 1 else ex
    B.extend(
        arch_wall(
            xb,
            xf,
            BRY1,
            BRY2,
            FZ2,
            EARCH_CEIL,
            EARCH_RIN,
            EARCH_ROUT,
            A_SEGS,
            T_STONE,
            stilt_h=EARCH_STILT,
        )
    )
    # Fill above arch crown — solid stone abutment up to deck top
    B.append(box(xb, -EARCH_ROUT, EARCH_CROWN, xf, EARCH_ROUT, EARCH_CEIL, T_STONE))

# ── Hanging glow panel beneath arch centre (photo-accurate skylight look) ────
# Placed well below the arch ceiling (deck bottom at arch ends = DZ1=128).
# At X=0 the deck bottom is at 192; panel at Z=148..160 clears all deck brushes.
PANEL_Z = 148
B.append(box(-48, -48, PANEL_Z, 48, 48, PANEL_Z + 12, T_LIGHT_PANEL))

# ── Light panels on inner parapet face (arch-aware Z) ────────────────────────
panel_xs = []
all_x = [BRX1] + PXS + [BRX2]
for i in range(len(all_x) - 1):
    panel_xs.append((all_x[i] + all_x[i + 1]) // 2)
for px in panel_xs:
    pbase = dtop(px)
    ph = pbase + PAR_H // 2 - 10
    pt_ = ph + 20
    B.append(box(px - 8, BRY2 - 27, ph, px + 8, BRY2 - 24, pt_, T_LIGHT_PANEL))
    B.append(box(px - 8, BRY1 + 24, ph, px + 8, BRY1 + 27, pt_, T_LIGHT_PANEL))


# ── Worldspawn ────────────────────────────────────────────────────────────────
worldspawn = (
    "{\n"
    '"classname" "worldspawn"\n'
    '"wad" "quake101.wad"\n'
    '"message" "Loyola Bridge"\n'
    '"sky" "sky4"\n'
    '"ambient" "40"\n'
    '"dmflags" "128"\n' + "\n".join(B) + "\n}"
)

# ── Entities ──────────────────────────────────────────────────────────────────
E = []
DECK_Z = dtop(0) + 8  # centre of arch deck + a bit (spawn/item height)
ROAD_Z = FZ2 + 8

# Teleport destinations
E.append(
    ent(
        "info_teleport_destination",
        targetname="dest_east",
        origin="900 0 176",
        angle="180",
    )
)
E.append(
    ent(
        "info_teleport_destination",
        targetname="dest_west",
        origin="-900 0 176",
        angle="0",
    )
)

# Teleport triggers at the ends of the bridge
# West end trigger -> East destination
west_trigger_brush = box(
    OX1 + WALL_T, BRY1, DZ2, OX1 + WALL_T + 16, BRY2, DZ2 + 64, T_TELEPORT
)
E.append(brush_ent("trigger_teleport", [west_trigger_brush], target="dest_east"))

# East end trigger -> West destination
east_trigger_brush = box(
    OX2 - WALL_T - 16, BRY1, DZ2, OX2 - WALL_T, BRY2, DZ2 + 64, T_TELEPORT
)
E.append(brush_ent("trigger_teleport", [east_trigger_brush], target="dest_west"))


E.append(ent("info_player_start", origin=f"0 0 {int(dtop(0) + 32)}"))

for pos in [
    (0, 0, int(dtop(0) + 32)),
    (-160, 0, int(dtop(-160) + 32)),
    (160, 0, int(dtop(160) + 32)),
    (-320, 0, int(dtop(-320) + 32)),
    (320, 0, int(dtop(320) + 32)),
    (0, 64, int(dtop(0) + 32)),
    (0, 550, ROAD_Z),
    (60, 700, ROAD_Z),
    (-60, 700, ROAD_Z),
    (0, -550, ROAD_Z),
    (60, -700, ROAD_Z),
    (-60, -700, ROAD_Z),
    (200, 0, ROAD_Z),
    (-200, 0, ROAD_Z),
]:
    E.append(ent("info_player_deathmatch", origin=f"{pos[0]} {pos[1]} {pos[2]}"))

E.append(ent("weapon_rocketlauncher", origin=f"0    0    {DECK_Z}"))
E.append(ent("weapon_rocketlauncher", origin=f"-640 0    176"))
E.append(ent("weapon_rocketlauncher", origin=f" 640 0    176"))
E.append(ent("weapon_rocketlauncher", origin=f"0    600  {ROAD_Z}"))
E.append(ent("weapon_rocketlauncher", origin=f"0   -600  {ROAD_Z}"))

for ax in [-384, -128, 128, 384]:
    E.append(ent("item_rockets", origin=f"{ax} 0 {int(dtop(ax) + 8)}"))
for bx in [-60, 60]:
    E.append(ent("item_rockets", origin=f"-640 {bx} 176"))
    E.append(ent("item_rockets", origin=f" 640 {bx} 176"))
for ry in [-800, -550, -300, 300, 550, 800]:
    E.append(ent("item_rockets", origin=f"0 {ry} {ROAD_Z}"))

E.append(ent("item_health", origin=f"0    0    {DECK_Z}"))
E.append(ent("item_health", origin=f"0  450    {ROAD_Z}"))
E.append(ent("item_health", origin=f"0 -450    {ROAD_Z}"))

# Torch lights on pillar caps
for px in PXS:
    pbase = dtop(px)
    pcap = pbase + PAR_H + PIL_EXTRA + PIL_CAP_H
    cy_n = BRY2 - 12
    cy_s = BRY1 + 12
    E.append(
        ent("light", origin=f"{px} {cy_n} {int(pcap + 20)}", light="300", style="1")
    )
    E.append(
        ent("light", origin=f"{px} {cy_s} {int(pcap + 20)}", light="300", style="1")
    )

# Panel glow
for px in panel_xs:
    pbase = dtop(px)
    ph = int(pbase + PAR_H // 2)
    E.append(ent("light", origin=f"{px} {BRY2 - 30} {ph}", light="180"))
    E.append(ent("light", origin=f"{px} {BRY1 + 30} {ph}", light="180"))

# Building interior lights
E.append(ent("light", origin="-640 0 260", light="350"))
E.append(ent("light", origin=" 640 0 260", light="350"))

# Bridge end arch lights — illuminate the stone arch faces
for ex in [BRX1 + 20, BRX2 - 20]:
    E.append(ent("light", origin=f"{ex} 0 90", light="300"))

# Under-bridge road lights — moody, bright pool under the glow panel
E.append(
    ent("light", origin=f"0 0 {PANEL_Z - 10}", light="520", style="1")
)  # glow panel light
for rx in [-280, 280]:
    E.append(ent("light", origin=f"{rx} 0 64", light="160"))

# N/S road arm lights
for ry in [-800, -600, -420, 420, 600, 800]:
    E.append(ent("light", origin=f"0 {ry} 300", light="320"))

# ── Write ─────────────────────────────────────────────────────────────────────
map_text = worldspawn + "\n" + "\n".join(E) + "\n"
with open("loyola.map", "w") as fh:
    fh.write(map_text)
print(f"loyola.map written — {len(B)} worldspawn brushes, {len(E)} entities")
