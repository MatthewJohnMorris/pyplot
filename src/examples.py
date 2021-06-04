# necessary python modules
# * noise (for perlin stuff)
# * opencv-python
# * pycairo (for text)
# * svgwrite

from pyplot import PenType, Point, StandardDrawing

import apollonius
import calibration
import cards
import colour
import drawtext
import hash_shading
import lsystem
import mandala
import nets
import opart
import perlin
import prophets
import shape_clips
import sketch
import spirograph
import threed
import truchet

# Note - if you use GellyRollOnBlack you will have a black rectangle added (on a layer whose name starts with "x") so you
# can get some idea of what things will look like - SVG doesn't let you set a background colour. You should either delete this rectangle
# before plotting, or use the "Layers" tab to plot - by default everything is written to layer "0-default"
# d = StandardDrawing(pen_type = PenType.GellyRollMetallicOnBlack())
# d = StandardDrawing(pen_type = PenType.GellyRollMoonlightOnBlack())
d = StandardDrawing(pen_type = PenType.PigmaMicron05())
# d = StandardDrawing(pen_type = PenType.PigmaMicron03())
# d = StandardDrawing(pen_type = PenType.PigmaMicron01())
# d = StandardDrawing(pen_type = PenType.StaedtlerPigment08())
# d = StandardDrawing(pen_type = PenType.StaedtlerPigment05())
# d = StandardDrawing(pen_type = PenType.StaedtlerPigment03())
# d = StandardDrawing(pen_type = PenType.StaedtlerPigment01())
# d = StandardDrawing(pen_type = PenType.StaedtlerPigment005())
# d = StandardDrawing(pen_type = PenType.RotringTikky05())
# d = StandardDrawing(pen_type = PenType.RotringTikky03())
# d = StandardDrawing(pen_type = PenType.PilotG207())

# take (102.5, 148) as centre of A4 given where everything currently sits
# effective area in each direction is (94, 138), e.g. (8,10) at top left
# restriction is at max-y - could get a few mm more by shifting paper in neg-y direction, but doesn't seem worth it
paper_centre = Point(102.5, 148)
paper_size = Point(192, 270)

# import cProfile
# cProfile.run('draw_3d(d)')
truchet.draw_truchet(d, redline=True)

if False:
    # works in progress
    sketch.image_sketch(d)

    # realised ideas I want to keep
    apollonius.apollonian_foam(d)
    cards.draw_tree(d)
    cards.test_hearts(d)
    cards.valentine(d)
    cards.draw_snowflake(d)
    cards.mothers_day(d)
    colour.random_coloured_rects(d)
    colour.test_line_colour(d)
    mandala.star_gen(d)
    perlin.plot_perlin_spirals(d)
    perlin.plot_perlin_drape_spiral(d, 6)
    perlin.plot_perlin_drape_spiral(d, 8)
    perlin.plot_perlin_surface(d)
    prophets.draw_false_prophets(d)
    prophets.multi_burroughs(d)
    prophets.burroughs_medal(d)
    prophets.wakefield_medal(d)
    prophets.draw_wakefield(d)
    
    # 3d
    threed.draw_3d(d)
    threed.draw_3d_shade(d)
    threed.draw_unknown_pleasures(d)
    shape_clips.draw_shape_clips(d)
    shape_clips.draw_shape_clips2(d)
    shape_clips.draw_shape_clips3(d)
    nets.draw_net(d)
    
    # hashing
    hash_shading.draw_hash(d)
    hash_shading.draw_hash2(d)
    hash_shading.draw_hash3(d)

    # op art
    opart.draw_riley_blaze(d)
    opart.draw_riley_movement_in_squares(d)
    opart.draw_riley_backoff_test(d)
    opart.draw_xor_circles_othello(d)
    opart.spiral_moire(d)
    
    # lsystems, tiling, spirograph
    lsystem.lsystem_test(d)
    truchet.draw_truchet(d)
    truchet.draw_truchet2(d)
    spirograph.spirograph1(d)
    spirograph.spirograph2(d)
    spirograph.spirograph3(d)
    spirograph.spirograph4(d)
    spirograph.spirograph5(d)
    spirograph.spirograph6(d)
    spirograph.spirograph7(d)
    spirograph.spirograph8(d)
    spirograph.spirograph9(d)
    spirograph.spirograph10(d)

    # text
    drawtext.draw_big_a(d)
    drawtext.draw_word_square(d)
    drawtext.test_text_sizes(d)
    drawtext.test_text_and_shape(d)
    drawtext.test_boxed_text(d)
    drawtext.draw_text_by_letter_and_whole_for_comparison(d, family='CNC Vector') # , s="a l l w o r k a n d n o p l a y m a k e s jackadullboy")

    # spiral plotting
    d.add_spiral_text((100.75, 100.75), 60)
    d.add_spiral((60, 60), 30)
    d.add_spiral((61.6666, 61.666), 30)
    d.image_spiral_single(d.dwg, 'testCard_F.jpg', (100, 100), 40)
    d.image_spiral_single(d.dwg, 'bear2.jpg', (100, 140), 20)
    d.image_spiral_single(d.dwg, 'burroughs.jpg', (100, 100), 80)
    # d.image_spiral_cmyk('testCard_F.jpg', (100, 120), 40)
    # d.image_spiral_cmyk('test_wheel.jpg', paper_centre, 20)
    # d.image_spiral_cmyk('muppets.jpeg', paper_centre, 80)

    # testing stuff: fill quality, pen line quality under various speeds, etc
    calibration.line_quality_test(d)
    calibration.speed_limit_test(d)
    calibration.fill_test(d)
    calibration.test_drawing_extent(d)
    calibration.complex_fill(d)
    calibration.test_shape_filler(d)
    calibration.test_bounds(d)

d.dwg.save()

