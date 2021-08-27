# necessary python modules
# * noise (for perlin stuff)
# * opencv-python
# * pycairo (for text)
# * svgwrite

from pyplot import PenType, Point, ShapeFiller, StandardDrawing
import math
import random
import svgwrite

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

def make_diamond(centre, size):

    return [centre + Point(-size, 0), centre + Point(0, -size), centre + Point(size, 0), centre + Point(0, size), centre + Point(-size, 0)]

def draw_diamonds(d):

    paper_centre = Point(102.5, 148)
    paper_size = Point(192, 270)
    size = 10
    lines = []
    nr = 8
    nc = 12
    for r in range(0, nr):
        for c in range(0, nc):
            d_centre = paper_centre + Point(r - (nr-1)/2, c - (nc-1)/2) * size * 2
            lines.append(make_diamond(d_centre, size))
            
            line1 = make_diamond(d_centre, size/3)
            line2 = make_diamond(d_centre, size*2/3)
            sf = ShapeFiller([line1, line2])
            fill = sf.get_paths(d.pen_type.pen_width * 0.4)
            lines.extend(fill)
                
    for r in range(0, nr-1):
        for c in range(0, nc-1):
            d_centre = paper_centre + Point(r - (nr-2)/2, c - (nc-2)/2) * size * 2
            
            line1 = make_diamond(d_centre, size/2)
            line2 = make_diamond(d_centre, size*3/4)
            sf = ShapeFiller([line1, line2])
            fill = sf.get_paths(d.pen_type.pen_width * 0.4)
            lines.extend(fill)
                
            line3 = make_diamond(d_centre, size/4)
            sf = ShapeFiller([line3])
            fill = sf.get_paths(d.pen_type.pen_width * 0.4)
            lines.extend(fill)
                
    d.add_polylines(lines)
    
def draw_inward_radials(d):

    paper_centre = Point(102.5, 148)
    paper_size = Point(192, 270)
    r_inner = 10
    r_outer = 80
    gap = d.pen_type.pen_width * 1
    n = int(2 * math.pi * r_inner / gap) + 1
    lines1 = []
    lines2 = []
    lines3 = []
    for i in range(0, n):
        a = math.pi * 2 * (i+20) / n
        s = math.sin(a)
        c = math.cos(a)
        a2 = math.pi * 2 * (i+20) / n
        s2 = math.sin(a2)
        c2 = math.cos(a2)
        a3 = math.pi * 2 * (i+40) / n
        s3 = math.sin(a3)
        c3 = math.cos(a3)
        rad = Point(c, s)
        rad2 = Point(c2, s2)
        rad3 = Point(c3, s3)
        
        c2 = paper_centre + Point(0, 0)
        lines1.append([paper_centre + rad2 * r_inner, paper_centre + rad * r_outer])
        lines1.append([paper_centre + rad3 * r_inner, paper_centre + rad * r_outer])
        
    # lines3.append(d.make_dot(paper_centre, r_inner+23, r_start=r_inner+22))

    d.add_polylines(lines1, container=d.add_layer("1")) # , stroke=svgwrite.rgb(0, 100, 100, '%'))
    # d.add_polylines(lines2, container=d.add_layer("2"), stroke=svgwrite.rgb(100, 0, 100, '%'))
    # d.add_polylines(lines3, container=d.add_layer("3"), stroke=svgwrite.rgb(100, 100, 0, '%'))
    
def text_in_circle(d, centre, text, radius, fontsize, family, fill, container=None):

    container = d.default_container(container)
    angle = - math.pi / 2 * 0.9
    lines = []
    for letter in text:
        ext = d.text_bound_letter(letter, fontsize, family)
        w = ext[0]
        angle_diff = w / radius * 1.2
        ((w, h), text_paths) = d.make_spiral_letter(letter, fontsize, centre, radius, angle=angle, family=family)
        angle += angle_diff
        if len(text_paths) > 0:
            if fill:
                sf = ShapeFiller(text_paths)
                filled_text_paths = sf.get_paths(d.pen_type.pen_width / 5)
                lines.extend(filled_text_paths)
            else:
                lines.extend(text_paths)
        
    d.add_polylines(lines, container=container)
    
    if False: # fill:
        d.add_dot(centre, radius + 7.3, r_start = radius  + 5.8, stroke=svgwrite.rgb(0, 0, 0, '%'), container=container)
        d.add_dot(centre, radius - 1.8, r_start = radius  - 3.3, stroke=svgwrite.rgb(0, 0, 0, '%'), container=container)    
    else:
        d.add_circle(centre, radius + 7.3)
        d.add_circle(centre, radius + 5.8)
        d.add_circle(centre, radius - 1.9)
        d.add_circle(centre, radius - 3.3)
    
    lines = []
    lines.append(d.make_circle(centre, radius + 8.3))
    lines.append(d.make_circle(centre, radius - 4.3))
    return lines

def draw_spiral_noise(d, inverse=False, r_initial=None, r_per_circle=None):    

    scale = 80
    direction = 1
    centre = Point(102.5, 148)
    points = []
    r = 0 if r_initial is None else r_initial # initial radius
    a = 0 # starting angle
    r_per_circle = 6 * d.pen_type.pen_width if r_per_circle is None else r_per_circle # gap between spiral paths: 1 is tightest
    c_size = 0.5 # constant distance travelled: something like the nib width is probably best
    
    # draw until we've hit the desired size
    while r <= scale:
    
        # Archimedian spiral with constant length of path
        r_floored = max(r, 0.5)
        a_inc = c_size / r_floored
        a += a_inc * direction
        r += r_per_circle * a_inc / (2 * math.pi)
        # 0 -> 0
        # scale => 0
        factor = math.sin(math.pi * r / scale / 2)
        factor = factor * factor * 2
        if inverse:
            factor = 2 - factor
        # factor = r / scale
        # r_use = r + 1 * (2 * (random.random() - 0.5)) * factor
        
        # output location
        s = math.sin(a)
        c = math.cos(a)
        pt = centre + Point(c, s) * r

        perturb_angle = math.pi * 2 * random.random()
        perturb = Point(math.cos(perturb_angle), math.sin(perturb_angle)) * factor
        pt = pt + perturb
        
        points.append(pt)

    d.add_polyline(points)

def draw_redblue(d):

    # note here that we are writing the lines out one by one to avoid reversing in add_polylines
    # this drastically improves the alignment of lines between the blue & red layers

    layer1 = d.add_layer("1-red")
    layer2 = d.add_layer("2-blue")
    layer3 = d.add_layer("3-black")

    paper_centre = Point(102.5, 148)
    paper_size = Point(192, 270)
    r_inner = 30
    r_outer = 80
    gap = d.pen_type.pen_width * 1
    n = int(2 * math.pi * r_inner / gap) + 1
    lines1 = []
    lines2 = []
    lines3 = []
    gap = 10
    for i in range(0, n):
        a = math.pi * 2 * i / n
        s = math.sin(a)
        c = math.cos(a)
        unit_line = Point(s, c)
        r_red_1 = r_inner - random.random() * gap
        r_red_2 = r_outer + random.random() * gap
        r_blue_1 = r_inner - random.random() * gap
        r_blue_2 = r_outer + random.random() * gap
        
        lines1.append([paper_centre + unit_line * r_red_1, paper_centre + unit_line * r_red_2])
        lines2.append([paper_centre + unit_line * r_blue_1, paper_centre + unit_line * r_blue_2])
        lines3.append([paper_centre + unit_line * r_inner, paper_centre + unit_line * r_outer])
     
    for line in lines1:
        d.add_polyline(line, container=layer1, stroke=svgwrite.rgb(100, 0, 0, '%'))
    for line in lines2:
        d.add_polyline(line, container=layer2, stroke=svgwrite.rgb(0, 0, 100, '%'))
    # d.add_polylines(lines3, container=d.add_layer("3"), stroke=svgwrite.rgb(0, 0, 0, '%'))

def thingy(d):

    paper_centre = Point(102.5, 148)
    paper_size = Point(192, 270)
    
    lines = []
    lines_r = []
    lines_g = []
    lines_b = []
    
    size = 3
    nr = 50
    nc = 30
    for r in range(0, nr+1):
        for c in range(0, nc+1):
            pt = paper_centre + Point(0, 5) * (r - nr/2) + Point(5, 0) * (c - nc/2)
            a = random.random() * math.pi * 2
            line = d.make_square(pt, size)
            line.append(line[0])
            centre = pt + Point(1,1) * size/2
            line = [d.rotate_about(pt, centre, a) for pt in line]
            lines.append(line)
            
            line = d.make_circle(centre, size/4)
            lines_circle = lines_b
            x = random.random()
            if x < 0.333:
                lines_circle = lines_r
            elif x < 0.666:
                lines_circle = lines_g
                
            lines_circle.append(line)
            
            line = d.make_square(pt + Point(1,1)*size/4, size/2)
            line.append(line[0])
            centre = pt + Point(1,1) * size/2
            line = [d.rotate_about(pt, centre, a) for pt in line]
            # lines.append(line)

    d.add_polylines(lines, container=d.add_layer("1"))
    d.add_polylines(lines_r, container=d.add_layer("2"), stroke=svgwrite.rgb(100, 0, 0, '%'))
    d.add_polylines(lines_g, container=d.add_layer("3"), stroke=svgwrite.rgb(0, 50, 0, '%'))
    d.add_polylines(lines_b, container=d.add_layer("4"), stroke=svgwrite.rgb(0, 0, 100, '%'))
    
def linked_shapes(d):

    paper_centre = Point(102.5, 148)
    radius = 70
    node_size = 5
    n = 29

    pts_and_angles = []
    for i in range(0, n):
        a = math.pi * 2 * i / n
        c = math.cos(a)
        s = math.sin(a)
        pt = paper_centre + Point(c, s) * radius
        pts_and_angles.append((pt, a))
        
    unclipped_lines = []
    for i1 in range(0, len(pts_and_angles)):
        for i2 in range(0, i1):
            (pt1, _) = pts_and_angles[i1]
            (pt2, _) = pts_and_angles[i2]
            if pt1.x != pt2.x or pt1.y != pt2.y:
                unclipped_lines.append([pt1, pt2])

    shapes = []
    for (pt, a) in pts_and_angles:
        shape = [pt + Point(1,1)*node_size/2, pt + Point(1,-1)*node_size/2, pt + Point(-1,-1)*node_size/2, pt + Point(-1,1)*node_size/2]
        shape = [StandardDrawing.rotate_about(x, pt, a) for x in shape]
        shapes.append(shape)
        
    sf = ShapeFiller(shapes)
    clipped_lines = sf.clip(unclipped_lines)
    for shape in shapes:
        closed_shape = [x for x in shape]
        closed_shape.append(shape[0])
        clipped_lines.append(closed_shape)
    
    d.add_polylines(clipped_lines)


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
# draw_diamonds(d)
# draw_inward_radials(d)

# Try other pen types on black heavy plots - do they clog less than Pigmas?

# draw_spiral_noise(d, True)
# thingy(d)
# linked_shapes(d)
# sketch.image_sketch3(d)
truchet.draw_truchet(d)

if False:
    # works in progress
    sketch.image_sketch(d)
    sketch.image_sketch2(d)
    sketch.image_sketch3(d)

    # realised ideas I want to keep
    apollonius.apollonian_foam(d)
    cards.draw_tree(d)
    cards.test_hearts(d)
    cards.valentine(d)
    cards.draw_snowflake(d)
    cards.mothers_day(d)
    cards.draw_bridge_card(d)
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
    
    # redblue
    draw_redblue(d)
    
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
    opart.circles(d)
    opart.spiral_moire2(d)
    
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

