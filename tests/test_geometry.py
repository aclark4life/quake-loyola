import math
import unittest

from quake_loyola.constants import BRIDGE_EAST_PIVOT_X, BRIDGE_EAST_SPAN_ANGLE
from quake_loyola.geometry import (
    arch_fill,
    arch_pie_seg,
    arch_plate_ring,
    arch_seg,
    arch_seg_chord,
    arch_wall,
    arch_wall_y,
    box,
    box_with_round_hole,
    brush_ent,
    carve_box,
    corner_ramp,
    corner_window,
    curb_seg,
    east_y_shift,
    elevator_shaft,
    ent,
    entrance_arch_xwall,
    entrance_arch_ywall,
    fascia_sign,
    gable_slats,
    iron_fence,
    layered_wall,
    loop_railing_x,
    make_bush,
    make_giant_tree,
    make_pixel_tree,
    make_tree,
    octagon_column,
    polygon_prism,
    radial_fan_fills,
    ramp_slab,
    ramp_slab_y,
    render_text_flat,
    render_text_flat_x,
    square_wall,
    stair_railing_x,
    stair_railing_y,
    stairwell,
    tile_face_plates,
    torch_flame,
    torch_flame_only,
    tri_prism,
    win_frame_xwall,
    win_frame_ywall,
)
from quake_loyola.mapdata import Brush, Entity


class BoxTests(unittest.TestCase):
    def test_box_returns_brush_with_six_faces(self):
        b = box(-64, -64, 0, 64, 64, 64, "city2_7")
        self.assertIsInstance(b, Brush)
        self.assertEqual(len(b.faces), 6)

    def test_box_serialization_is_stable(self):
        expected = (
            "{\n"
            "( 0 0 0 ) ( 0 1 0 ) ( 0 0 1 ) t 0 0 0 1 1\n"
            "( 1 0 0 ) ( 1 0 1 ) ( 1 1 0 ) t 0 0 0 1 1\n"
            "( 0 0 0 ) ( 0 0 1 ) ( 1 0 0 ) t 0 0 0 1 1\n"
            "( 0 1 0 ) ( 1 1 0 ) ( 0 1 1 ) t 0 0 0 1 1\n"
            "( 0 0 0 ) ( 1 0 0 ) ( 0 1 0 ) t 0 0 0 1 1\n"
            "( 0 0 1 ) ( 0 1 1 ) ( 1 0 1 ) t 0 0 0 1 1\n"
            "}"
        )
        self.assertEqual(box(0, 0, 0, 1, 1, 1, "t").to_map(), expected)

    def test_box_distinct_top_bottom_textures(self):
        b = box(0, 0, 0, 1, 1, 1, "side", tt="top", tb="bot")
        self.assertEqual(b.faces[4].tex, "bot")  # -Z bottom
        self.assertEqual(b.faces[5].tex, "top")  # +Z top


class EntityHelperTests(unittest.TestCase):
    def test_ent_returns_point_entity(self):
        e = ent("item_health", origin="1 2 3")
        self.assertIsInstance(e, Entity)
        self.assertEqual(e.classname, "item_health")
        self.assertEqual(e.fields, {"origin": "1 2 3"})
        self.assertEqual(e.brushes, [])

    def test_brush_ent_with_list(self):
        bs = [box(0, 0, 0, 1, 1, 1, "t"), box(2, 2, 2, 3, 3, 3, "t")]
        e = brush_ent("func_detail", bs, foo="bar")
        self.assertIsInstance(e, Entity)
        self.assertEqual(len(e.brushes), 2)
        self.assertEqual(e.fields, {"foo": "bar"})

    def test_brush_ent_accepts_single_brush(self):
        e = brush_ent("func_wall", box(0, 0, 0, 1, 1, 1, "t"))
        self.assertEqual(len(e.brushes), 1)

    def test_torch_flame_returns_light_and_flame_entities(self):
        entities = torch_flame(1, 2, 3)
        self.assertEqual(
            [e.classname for e in entities], ["light", "light_flame_large_yellow"]
        )
        self.assertEqual(
            [e.fields for e in entities],
            [
                {"origin": "1 2 3", "light": "300"},
                {"origin": "1 2 7"},
            ],
        )
        self.assertTrue(all(e.brushes == [] for e in entities))

    def test_torch_flame_only_returns_standalone_flame_entity(self):
        entity = torch_flame_only(1, 2, 3)
        self.assertEqual(entity.classname, "light_flame_large_yellow")
        self.assertEqual(entity.fields, {"origin": "1 2 3"})
        self.assertEqual(entity.brushes, [])


class CompositeShapeTests(unittest.TestCase):
    def test_make_tree_returns_four_brushes(self):
        brushes = make_tree(0, 0, 0)
        self.assertEqual(len(brushes), 4)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_make_giant_tree_returns_four_brushes(self):
        brushes = make_giant_tree(0, 0, 0)
        self.assertEqual(len(brushes), 4)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_make_bush_returns_three_brushes(self):
        brushes = make_bush(0, 0, 0)
        self.assertEqual(len(brushes), 3)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_square_wall_returns_brush_list(self):
        brushes = square_wall(-8, 8, -200, 200, 0, 128, 48, "t")
        self.assertTrue(len(brushes) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_ramp_slab_y_full_prism_has_six_faces(self):
        b = ramp_slab_y(0, 10, 0, 10, 0, 0, 5, 5, "t")
        self.assertEqual(len(b.faces), 6)

    def test_ramp_slab_y_knife_edge_drops_endcap(self):
        # zt2 == zb2 at the far end -> that end tapers to an edge, face omitted
        b = ramp_slab_y(0, 10, 0, 10, 0, 0, 5, 0, "t")
        self.assertEqual(len(b.faces), 5)

    def test_tri_prism_returns_five_faces(self):
        b = tri_prism(0, 0, 10, 0, 0, 10, 0, 20, "t")
        self.assertIsInstance(b, Brush)
        self.assertEqual(len(b.faces), 5)

    def test_corner_ramp_returns_four_faces(self):
        b = corner_ramp(10, 0, 20, 10, 0, 20, "t")
        self.assertIsInstance(b, Brush)
        self.assertEqual(len(b.faces), 4)

    def test_arch_seg_returns_six_faces(self):
        b = arch_seg(0, 10, 0, 0, 16, 32, 0, 45, "t")
        self.assertIsInstance(b, Brush)
        self.assertEqual(len(b.faces), 6)

    def test_octagon_column_returns_ten_faces(self):
        b = octagon_column(0, 0, 0, 64, 32, "t")
        self.assertIsInstance(b, Brush)
        # 8 side faces + top + bottom
        self.assertEqual(len(b.faces), 10)

    def test_layered_wall_omits_covered_cells_and_keeps_others(self):
        # A single opening exactly matching one grid cell should leave that cell
        # out of the result while still emitting the surrounding wall pieces.
        brushes = layered_wall(0, -8, 0, 100, 0, 100, [(40, 20, 60, 80)], "t")
        self.assertTrue(len(brushes) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))
        # No brush should span exactly the opening's x/z extent (it must be omitted)
        for b in brushes:
            pts = [p for f in b.faces for p in (f.p1, f.p2, f.p3)]
            xs = sorted({p[0] for p in pts})
            zs = sorted({p[2] for p in pts})
            self.assertFalse(
                min(xs) == 40 and max(xs) == 60 and min(zs) == 20 and max(zs) == 80
            )

    def test_layered_wall_no_openings_returns_single_slab(self):
        brushes = layered_wall(0, -8, 0, 100, 0, 100, [], "t")
        self.assertEqual(len(brushes), 1)


class GuardClauseTests(unittest.TestCase):
    def test_iron_fence_rejects_non_positive_spacing(self):
        with self.assertRaises(ValueError):
            iron_fence([(0, 100)], -8, 8, "t", 0, spacing=0)

    def test_gable_slats_rejects_zero_denominator(self):
        # ridge_z == eave_z + slab_t -> denom is zero, must raise instead of
        # hanging or dividing by zero deep inside edge_x().
        with self.assertRaises(ValueError):
            gable_slats(0, 100, 50, 0, 16, 16, 0, 8, "t")


class HelperFunctionTests(unittest.TestCase):
    def test_east_y_shift_is_zero_at_and_west_of_pivot(self):
        self.assertEqual(east_y_shift(BRIDGE_EAST_PIVOT_X), 0.0)
        self.assertEqual(east_y_shift(BRIDGE_EAST_PIVOT_X - 1), 0.0)

    def test_east_y_shift_is_negative_east_of_pivot(self):
        shift = east_y_shift(BRIDGE_EAST_PIVOT_X + 10)
        expected = -10 * math.tan(math.radians(BRIDGE_EAST_SPAN_ANGLE))
        self.assertLess(shift, 0.0)
        self.assertAlmostEqual(shift, expected)


class RoundHoleAndRadialFanTests(unittest.TestCase):
    def test_box_with_round_hole_returns_brushes_around_circle(self):
        pieces = box_with_round_hole(-64, -64, 0, 64, 64, 64, 0, 0, 16, "t", n=16)
        self.assertTrue(len(pieces) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in pieces))

    def test_radial_fan_fills_covers_corner_gaps(self):
        fills = radial_fan_fills(0, 0, 16, -64, -64, 64, 64, 0, 64, "t", n=16)
        self.assertTrue(len(fills) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in fills))

    def test_radial_fan_fills_rejects_too_few_segments(self):
        with self.assertRaises(ValueError):
            radial_fan_fills(0, 0, 16, -64, -64, 64, 64, 0, 64, "t", n=2)


class TextRenderingTests(unittest.TestCase):
    def test_render_text_flat_x_returns_brushes_for_nonblank_text(self):
        brushes = render_text_flat_x("A", 0, 0, 0, 4, 4, 2, "t")
        self.assertTrue(len(brushes) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_render_text_flat_returns_brushes_for_nonblank_text(self):
        brushes = render_text_flat("A", 0, 0, 0, 4, 4, 2, "t")
        self.assertTrue(len(brushes) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_render_text_flat_blank_space_returns_no_brushes(self):
        self.assertEqual(render_text_flat(" ", 0, 0, 0, 4, 4, 2, "t"), [])


class PixelTreeTests(unittest.TestCase):
    def test_make_pixel_tree_returns_brushes(self):
        brushes = make_pixel_tree(0, 0, 0)
        self.assertTrue(len(brushes) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_make_pixel_tree_rejects_ring_segs_of_one(self):
        with self.assertRaises(ValueError):
            make_pixel_tree(0, 0, 0, ring_segs=1)


class PolygonPrismNormalizationTests(unittest.TestCase):
    def test_polygon_prism_normalizes_reversed_z_bounds(self):
        pts = [(0, 0), (10, 0), (10, 10), (0, 10)]
        a = polygon_prism(pts, 0, 20, "t")
        b = polygon_prism(pts, 20, 0, "t")
        self.assertEqual(len(a.faces), len(b.faces))

    def test_polygon_prism_rejects_degenerate_polygon(self):
        with self.assertRaises(ValueError):
            polygon_prism([(0, 0), (1, 0), (2, 0)], 0, 10, "t")

    def test_polygon_prism_rejects_zero_height(self):
        with self.assertRaises(ValueError):
            polygon_prism([(0, 0), (1, 0), (1, 1)], 5, 5, "t")


class PrimitiveValidationTests(unittest.TestCase):
    def test_tri_prism_rejects_clockwise_winding(self):
        with self.assertRaises(ValueError):
            tri_prism(0, 0, 0, 10, 10, 0, 0, 20, "t")

    def test_tri_prism_rejects_reversed_z(self):
        with self.assertRaises(ValueError):
            tri_prism(0, 0, 10, 0, 0, 10, 20, 0, "t")

    def test_arch_seg_rejects_reversed_radii(self):
        with self.assertRaises(ValueError):
            arch_seg(0, 10, 0, 0, 32, 16, 0, 45, "t")

    def test_arch_seg_rejects_reversed_angles(self):
        with self.assertRaises(ValueError):
            arch_seg(0, 10, 0, 0, 16, 32, 45, 0, "t")

    def test_arch_seg_rejects_reversed_xb_xf(self):
        with self.assertRaises(ValueError):
            arch_seg(10, 0, 0, 0, 16, 32, 0, 45, "t")

    def test_arch_seg_chord_rejects_reversed_xb_xf(self):
        with self.assertRaises(ValueError):
            arch_seg_chord(10, 0, 0, 0, 16, 32, 0, 45, "t")

    def test_arch_pie_seg_rejects_reversed_xb_xf(self):
        with self.assertRaises(ValueError):
            arch_pie_seg(10, 0, 0, 0, 32, 0, 45, "t")

    def test_curb_seg_rejects_reversed_z_bounds(self):
        with self.assertRaises(ValueError):
            curb_seg(0, 0, 10, 0, 16, 32, 0, 45, "t")


class TileAndArchPlateRingTests(unittest.TestCase):
    def test_tile_face_plates_covers_face_with_tile_sized_boxes(self):
        brushes = tile_face_plates(0, 8, 0, 100, 0, 100, "t", tile=34, gap=3)
        self.assertTrue(brushes)
        for b in brushes:
            self.assertEqual(len(b.faces), 6)

    def test_tile_face_plates_too_small_face_returns_no_brushes(self):
        # Smaller than one tile on either axis produces no tile brushes.
        self.assertEqual(tile_face_plates(0, 8, 0, 10, 0, 10, "t"), [])

    def test_tile_face_plates_rejects_zero_thickness(self):
        with self.assertRaises(ValueError):
            tile_face_plates(0, 0, 0, 100, 0, 100, "t")

    def test_tile_face_plates_negative_thickness_normalizes_x_range(self):
        brushes = tile_face_plates(50, -8, 0, 100, 0, 100, "t")
        self.assertTrue(brushes)

    def test_arch_plate_ring_returns_chord_segments(self):
        brushes = arch_plate_ring(0, 8, 0, 0, 64, "t", tile=34, gap=3)
        self.assertTrue(brushes)
        for b in brushes:
            self.assertEqual(len(b.faces), 6)


class ArchWallTests(unittest.TestCase):
    def test_arch_wall_returns_brushes_with_side_walls_and_arch_segments(self):
        brushes = arch_wall(0, 16, -100, 100, 0, 128, 32, 48, 4, "t")
        self.assertTrue(brushes)
        for b in brushes:
            self.assertGreaterEqual(len(b.faces), 5)

    def test_arch_wall_rejects_non_positive_segs(self):
        with self.assertRaises(ValueError):
            arch_wall(0, 16, -100, 100, 0, 128, 32, 48, 0, "t")

    def test_arch_wall_rejects_reversed_x_bounds(self):
        with self.assertRaises(ValueError):
            arch_wall(16, 0, -100, 100, 0, 128, 32, 48, 4, "t")

    def test_arch_wall_freestanding_omits_ceiling_slab(self):
        framed = arch_wall(0, 16, -100, 100, 0, 128, 32, 48, 4, "t")
        freestanding = arch_wall(
            0, 16, -100, 100, 0, 128, 32, 48, 4, "t", freestanding=True
        )
        # The freestanding variant skips the box spanning the arch opening up
        # to the ceiling, so it produces fewer brushes than the framed wall.
        self.assertLess(len(freestanding), len(framed))

    def test_arch_wall_with_base_h_adds_base_brush(self):
        without_base = arch_wall(0, 16, -100, 100, 0, 128, 32, 48, 4, "t")
        with_base = arch_wall(0, 16, -100, 100, 0, 128, 32, 48, 4, "t", base_h=8)
        self.assertEqual(len(with_base), len(without_base) + 1)

    def test_arch_wall_y_returns_side_walls_and_arch_segments(self):
        brushes = arch_wall_y(-100, 100, 0, 32, 48, 4, "t")
        self.assertTrue(brushes)

    def test_arch_wall_y_rejects_non_positive_segs(self):
        with self.assertRaises(ValueError):
            arch_wall_y(-100, 100, 0, 32, 48, 0, "t")

    def test_arch_wall_y_rejects_reversed_bounds(self):
        with self.assertRaises(ValueError):
            arch_wall_y(100, -100, 0, 32, 48, 4, "t")

    def test_arch_fill_rejects_reversed_x_bounds(self):
        with self.assertRaises(ValueError):
            arch_fill(16, 0, 0, 0, 32, 4, "t")


class EntranceArchTests(unittest.TestCase):
    def test_entrance_arch_xwall_returns_brushes(self):
        brushes = entrance_arch_xwall(0, 0, 32, 96, 0, 1, "t")
        self.assertTrue(brushes)
        for b in brushes:
            self.assertIsInstance(b, Brush)

    def test_entrance_arch_ywall_returns_brushes(self):
        brushes = entrance_arch_ywall(0, 0, 32, 96, 0, 1, "t")
        self.assertTrue(brushes)
        for b in brushes:
            self.assertIsInstance(b, Brush)

    def test_entrance_arch_xwall_and_ywall_produce_same_brush_count(self):
        # The y-wall variant mirrors the x-wall geometry across axes, so both
        # should emit the same number of brushes for equivalent parameters.
        xwall = entrance_arch_xwall(0, 0, 32, 96, 0, 1, "t")
        ywall = entrance_arch_ywall(0, 0, 32, 96, 0, 1, "t")
        self.assertEqual(len(xwall), len(ywall))


class WinFrameTests(unittest.TestCase):
    def test_win_frame_xwall_returns_brushes(self):
        brushes = win_frame_xwall(0, 64, 0, 64, 0, 1, "t", fd=16)
        self.assertTrue(brushes)
        for b in brushes:
            self.assertIsInstance(b, Brush)

    def test_win_frame_ywall_returns_brushes(self):
        brushes = win_frame_ywall(0, 64, 0, 64, 0, 1, "t", fd=16)
        self.assertTrue(brushes)
        for b in brushes:
            self.assertIsInstance(b, Brush)

    def test_win_frame_xwall_without_crossbar_or_bottom_omits_bars(self):
        full = win_frame_xwall(0, 64, 0, 64, 0, 1, "t", fd=16)
        minimal = win_frame_xwall(
            0, 64, 0, 64, 0, 1, "t", fd=16, crossbar=False, bottom=False
        )
        self.assertLess(len(minimal), len(full))

    def test_win_frame_xwall_small_opening_omits_inner_muntins(self):
        # An opening too small for the inner muntin bars should still return
        # the outer frame without raising.
        brushes = win_frame_xwall(0, 20, 0, 20, 0, 1, "t", fd=16)
        self.assertTrue(brushes)

    def test_win_frame_xwall_rejects_fd_not_exceeding_2x_inner_recess(self):
        # fd=4, inner_recess=2 collapses the inner muntin depth to zero, which
        # used to raise an opaque "degenerate brush" ValueError deep inside
        # box() instead of a clear, actionable message. Defaults no longer
        # trigger this (inner_recess default is now 1), so pass explicit
        # incompatible values.
        with self.assertRaises(ValueError):
            win_frame_xwall(0, 64, 0, 64, 0, 1, "t", fd=4, inner_recess=2)

    def test_win_frame_ywall_rejects_fd_not_exceeding_2x_inner_recess(self):
        with self.assertRaises(ValueError):
            win_frame_ywall(0, 64, 0, 64, 0, 1, "t", fd=4, inner_recess=2)


class StairRailingTests(unittest.TestCase):
    def test_rail_is_level_sloped_level_with_a_post_at_each_end(self):
        brushes = stair_railing_y(0, 4, 0, 96, 48, 0, 40, "t", end_run=16, post_ovh=6)
        self.assertEqual(len(brushes), 5)
        top, slope, bottom, top_post, bottom_post = (b.get_bbox() for b in brushes)
        self.assertEqual((top[0][1], top[1][1]), (-16, 0))
        self.assertEqual((top[0][2], top[1][2]), (85, 88))
        self.assertEqual((slope[0][1], slope[1][1]), (0, 96))
        self.assertEqual((slope[0][2], slope[1][2]), (37, 88))
        self.assertEqual((bottom[0][1], bottom[1][1]), (96, 112))
        self.assertEqual((bottom[0][2], bottom[1][2]), (37, 40))
        self.assertEqual((top_post[0][1], top_post[1][1]), (-10, -7))
        self.assertEqual((bottom_post[0][1], bottom_post[1][1]), (103, 106))

    def test_posts_are_sunk_below_the_walking_surface(self):
        brushes = stair_railing_y(0, 4, 0, 96, 48, 0, 40, "t", post_drop=6)
        top_post, bottom_post = (b.get_bbox() for b in brushes[3:])
        self.assertEqual(top_post[0][2], 42)
        self.assertEqual(bottom_post[0][2], -6)

    def test_rejects_a_non_positive_run(self):
        with self.assertRaises(ValueError):
            stair_railing_y(0, 4, 96, 96, 0, 48, 40, "t")

    def test_rejects_an_end_run_too_short_for_its_post_and_overhang(self):
        with self.assertRaises(ValueError):
            stair_railing_y(0, 4, 0, 96, 48, 0, 40, "t", post_w=8, end_run=10)

    def test_x_variant_is_the_y_one_rotated(self):
        brushes = stair_railing_x(0, 4, 0, 96, 48, 0, 40, "t", end_run=16, post_ovh=6)
        self.assertEqual(len(brushes), 5)
        top, slope, bottom, top_post, bottom_post = (b.get_bbox() for b in brushes)
        self.assertEqual((top[0][0], top[1][0]), (-16, 0))
        self.assertEqual((top[0][2], top[1][2]), (85, 88))
        self.assertEqual((slope[0][0], slope[1][0]), (0, 96))
        self.assertEqual((slope[0][2], slope[1][2]), (37, 88))
        self.assertEqual((bottom[0][0], bottom[1][0]), (96, 112))
        self.assertEqual((bottom[0][2], bottom[1][2]), (37, 40))
        self.assertEqual((top_post[0][0], top_post[1][0]), (-10, -7))
        self.assertEqual((bottom_post[0][0], bottom_post[1][0]), (103, 106))

    def test_x_variant_rejects_a_non_positive_run(self):
        with self.assertRaises(ValueError):
            stair_railing_x(0, 4, 96, 96, 0, 48, 40, "t")

    def test_x_variant_rejects_an_end_run_too_short_for_its_post(self):
        with self.assertRaises(ValueError):
            stair_railing_x(0, 4, 0, 96, 48, 0, 40, "t", post_w=8, end_run=10)


class CarveBoxTests(unittest.TestCase):
    def setUp(self):
        self.src = box(0, 0, 0, 100, 100, 100, "t")
        self.out = carve_box([self.src], 20, 20, 50, 80, 80, 200)

    def covers(self, brushes, p):
        return any(b.contains(p) for b in brushes)

    def test_the_carved_volume_is_emptied(self):
        for p in ((50, 50, 60), (21, 21, 51), (79, 79, 99)):
            self.assertTrue(self.covers([self.src], p))
            self.assertFalse(self.covers(self.out, p), p)

    def test_everything_outside_the_box_is_kept(self):
        for p in (
            (50, 50, 40),
            (10, 50, 60),
            (90, 50, 60),
            (50, 10, 60),
            (50, 90, 60),
            (1, 1, 1),
            (99, 99, 99),
        ):
            self.assertTrue(self.covers(self.out, p), p)

    def test_the_pieces_it_returns_are_all_convex_brushes(self):
        for piece in self.out:
            self.assertIsInstance(piece, Brush)
            mins, maxs = piece.get_bbox()
            for lo, hi in zip(mins, maxs, strict=True):
                self.assertGreater(hi, lo)

    def test_a_brush_clear_of_the_box_is_passed_through_untouched(self):
        clear = box(200, 200, 0, 300, 300, 100, "t")
        out = carve_box([clear], 20, 20, 50, 80, 80, 200)
        self.assertEqual(out, [clear])

    def test_a_brush_swallowed_by_the_box_disappears(self):
        inner = box(30, 30, 60, 40, 40, 70, "t")
        self.assertEqual(carve_box([inner], 20, 20, 50, 80, 80, 200), [])

    def test_it_carves_sloped_brushes_too(self):
        slope = ramp_slab(0, 100, 0, 100, 0, 0, 100, 20, "t")
        out = carve_box([slope], 20, 20, -10, 80, 80, 200)
        for p in ((50, 50, 10), (50, 50, 30)):
            self.assertFalse(any(b.contains(p) for b in out), p)
        self.assertTrue(any(b.contains((10, 50, 40)) for b in out))

    def test_the_pieces_carry_no_face_that_bounds_nothing(self):
        # Clipping keeps every plane of the original brush; the ones the cut
        # reduced to an edge or a point are dropped, or the compiler would
        # crunch them away and warn.
        for piece in self.out:
            self.assertLessEqual(len(piece.faces), 6)

    def test_rejects_a_degenerate_box(self):
        with self.assertRaises(ValueError):
            carve_box([self.src], 20, 20, 50, 20, 80, 200)


class LoopRailingTests(unittest.TestCase):
    def setUp(self):
        self.brushes = loop_railing_x(
            0, 3, 0, 96, 48, 0, 44, "t", loop_h=24, posts=4, post_ovh=6, cap_segs=6
        )
        self.boxes = [b.get_bbox() for b in self.brushes]
        self.rails, self.caps, self.posts = (
            self.boxes[:2],
            self.boxes[2:14],
            (self.boxes[14:]),
        )

    def test_returns_two_rails_a_swept_round_at_each_end_and_the_posts(self):
        self.assertEqual(len(self.brushes), 2 + 2 * 6 + 4)

    def test_the_straight_rails_stop_short_to_leave_room_for_the_rounds(self):
        for rail in self.rails:
            self.assertEqual((rail[0][0], rail[1][0]), (13.5, 82.5))

    def test_the_rails_fall_with_the_surface_a_loop_apart(self):
        top, lower = self.rails
        self.assertEqual((top[0][2], top[1][2]), (47.75, 85.25))
        self.assertEqual((lower[0][2], lower[1][2]), (23.75, 61.25))

    def test_the_rounds_close_the_o_within_its_own_run(self):
        self.assertAlmostEqual(min(b[0][0] for b in self.caps), 0)
        self.assertAlmostEqual(max(b[1][0] for b in self.caps), 96)
        # Each round turns through a half circle a loop deep, so the O is no
        # taller at its ends than the pair of rails is between them.
        # The round is turned on the same annulus the rails sit on, so it
        # meets the top of one and the bottom of the other exactly.
        head = [b for b in self.caps if b[0][0] < 48]
        self.assertAlmostEqual(max(b[1][2] for b in head), 85.25)
        self.assertAlmostEqual(min(b[0][2] for b in head), 85.25 - 24 - 3)

    def test_the_posts_run_the_full_height_up_to_the_top_rail(self):
        for i, (mins, maxs) in enumerate(self.posts):
            surface = 48 - mins[0] / 2
            self.assertAlmostEqual(maxs[2], surface + 44)
            self.assertAlmostEqual(mins[2], surface - 4)
            self.assertEqual(maxs[0] - mins[0], 3, f"post {i}")

    def test_the_posts_are_evenly_spaced_within_the_straight_run(self):
        xs = [b[0][0] for b in self.posts]
        self.assertEqual(xs[0], 13.5 + 6)
        self.assertEqual(xs[-1], 82.5 - 6 - 3)
        gaps = [b - a for a, b in zip(xs[:-1], xs[1:], strict=True)]
        for gap in gaps[1:]:
            self.assertAlmostEqual(gap, gaps[0])

    def test_the_o_overhangs_the_outermost_posts(self):
        self.assertLess(0, self.posts[0][0][0])
        self.assertGreater(96, self.posts[-1][1][0])

    def test_rejects_a_non_positive_run(self):
        with self.assertRaises(ValueError):
            loop_railing_x(0, 3, 96, 96, 48, 0, 44, "t")

    def test_rejects_a_loop_too_shallow_to_turn_a_round_in(self):
        with self.assertRaises(ValueError):
            loop_railing_x(0, 3, 0, 96, 48, 0, 44, "t", rail_t=8, loop_h=8)

    def test_rejects_a_railing_with_no_end_posts(self):
        with self.assertRaises(ValueError):
            loop_railing_x(0, 3, 0, 96, 48, 0, 44, "t", posts=1)

    def test_rejects_a_run_too_short_to_turn_both_rounds_in(self):
        with self.assertRaises(ValueError):
            loop_railing_x(0, 3, 0, 20, 48, 0, 44, "t", loop_h=24)

    def test_rejects_a_run_too_short_for_its_posts(self):
        with self.assertRaises(ValueError):
            loop_railing_x(0, 3, 0, 30, 48, 0, 44, "t", loop_h=24, post_ovh=6, post_w=8)


class StairwellTests(unittest.TestCase):
    def test_stairwell_returns_brushes_per_floor(self):
        brushes = stairwell(
            0,
            256,
            0,
            256,
            128,
            [0, 256, 512],
            256,
            hn=6,
            tread_x=32,
            step_r=16,
            post_w=8,
            rail_h=64,
            rail_t=4,
            tex="t",
            rail_tex="r",
        )
        self.assertTrue(brushes)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_stairwell_brush_count_scales_with_floor_count(self):
        one_floor = stairwell(
            0,
            256,
            0,
            256,
            128,
            [0],
            256,
            hn=6,
            tread_x=32,
            step_r=16,
            post_w=8,
            rail_h=64,
            rail_t=4,
            tex="t",
            rail_tex="r",
        )
        two_floors = stairwell(
            0,
            256,
            0,
            256,
            128,
            [0, 256],
            256,
            hn=6,
            tread_x=32,
            step_r=16,
            post_w=8,
            rail_h=64,
            rail_t=4,
            tex="t",
            rail_tex="r",
        )
        self.assertEqual(len(two_floors), 2 * len(one_floor))


class ElevatorShaftTests(unittest.TestCase):
    def test_elevator_shaft_returns_brushes_with_door_openings(self):
        brushes = elevator_shaft(
            0,
            96,
            0,
            192,
            0,
            768,
            [(16, 0, 176, 128), (16, 256, 176, 384)],
            16,
            "t",
        )
        self.assertTrue(brushes)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))


class CornerWindowTests(unittest.TestCase):
    def test_corner_window_returns_mullion_and_transom_brushes(self):
        brushes = corner_window(
            64,
            0,
            8,
            0,
            800,
            256,
            3,
            40,
            8,
            4,
            "t",
            "r",
        )
        self.assertTrue(brushes)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))
        # Two mullion posts plus a transom/sill pair per floor.
        self.assertEqual(len(brushes), 2 + 3 * 2 - 1)


class FasciaSignTests(unittest.TestCase):
    def test_fascia_sign_returns_panel_and_lettering(self):
        brushes = fascia_sign(
            "KNOTT HALL",
            100,
            200,
            400,
            panel_h=128,
            panel_padding=16,
            px_w=8,
            px_h=8,
            panel_tex="t",
            text_tex="r",
        )
        self.assertTrue(brushes)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))
        # A backing panel plus at least one glyph brush.
        self.assertGreater(len(brushes), 1)


if __name__ == "__main__":
    unittest.main()
