import math
import random
import svgwrite

from pyplot import Point, ShapeFiller, StandardDrawing

def draw_tree(d):
    all_polylines = []
    
    pos = Point(105, 105)
    line = Point(0, 30)
    max_depth = 7
    cut = 2 / 3
    a_disp = math.pi / 6
    # a_disp = math.pi / 12
    num_branches = 21
    thickness_mm = 1.2
    layer0 = d.add_layer("0-dot")
    layers = [d.add_layer("1-green"), d.add_layer("2-orange"), d.add_layer("3-yellow")]
    strokes = [svgwrite.rgb(0, 255, 0, '%'), svgwrite.rgb(255, 0, 0, '%'), svgwrite.rgb(255, 255, 0, '%')]
    # strokes = [svgwrite.rgb(255, 255, 255, '%'), svgwrite.rgb(255, 255, 255, '%'), svgwrite.rgb(255, 255, 255, '%')]
    for i in range(0, num_branches):
        ix_layer = i % 3
        layer = layers[ix_layer]
        stroke = strokes[ix_layer]
        disp_rot = StandardDrawing.rotate_about(Point(0, 10), Point.Origin(), i * 2 * math.pi / num_branches)
        pos_start = pos + disp_rot
        branch_polylines = d.make_branch(pos_start, StandardDrawing.rotate_about(line, Point.Origin(), i * 2 * math.pi / num_branches), cut, a_disp, max_depth, thickness_mm)
        # don't bunch all the polylines together in a single bulk-add: there are loads of them and it'll make the optimisation of drawing order take ages
        d.add_polylines(branch_polylines, stroke=stroke, container=layer)
        
    d.add_dot(pos, 10, r_start=9, stroke=svgwrite.rgb(64, 64, 64, '%'))
    d.add_dot(pos, 8, stroke=svgwrite.rgb(64, 64, 64, '%'))

def add_checkboard(d, layerA, layerB, topleft, sqsize, sep):

    d.add_square((topleft[0] + 0*sep, topleft[1] + 0*sep), sqsize, container=layerA, stroke=svgwrite.rgb(0, 255, 0, '%'))
    d.add_square((topleft[0] + 1*sep, topleft[1] + 1*sep), sqsize, container=layerA, stroke=svgwrite.rgb(0, 255, 0, '%'))
    d.add_square((topleft[0] + 2*sep, topleft[1] + 2*sep), sqsize, container=layerA, stroke=svgwrite.rgb(0, 255, 0, '%'))
    d.add_square((topleft[0] + 2*sep, topleft[1] + 0*sep), sqsize, container=layerA, stroke=svgwrite.rgb(0, 255, 0, '%'))
    d.add_square((topleft[0] + 0*sep, topleft[1] + 2*sep), sqsize, container=layerA, stroke=svgwrite.rgb(0, 255, 0, '%'))

    d.add_square((topleft[0] + 0*sep, topleft[1] + 1*sep), sqsize, container=layerB, stroke=svgwrite.rgb(255, 64, 64, '%'))
    d.add_square((topleft[0] + 1*sep, topleft[1] + 0*sep), sqsize, container=layerB, stroke=svgwrite.rgb(255, 64, 64, '%'))
    d.add_square((topleft[0] + 2*sep, topleft[1] + 1*sep), sqsize, container=layerB, stroke=svgwrite.rgb(255, 64, 64, '%'))
    d.add_square((topleft[0] + 1*sep, topleft[1] + 2*sep), sqsize, container=layerB, stroke=svgwrite.rgb(255, 64, 64, '%'))

def xy_heart(r, a1):

    a = a1
    s = math.sin(a)
    x = r * s*s*s
    y = - r * (1/16)*(13 * math.cos(a) - 5 * math.cos(2*a) - 2 * math.cos(3*a) - math.cos(4*a))
    return(x,y)
            
def test_hearts(d):            
            
    for c in range(0, 8):
        d.add_dot((44 + 12*c, 216), 5 * (c+1) / 8, xy_func=xy_heart)
    for c in range(0, 8):
        d.add_dot((44 + 12*c, 228), 5, xy_func=xy_heart, r_start = 5 * (c+1) / 8)

def valentine(d):
    pen_width = d.pen_type.pen_width

    centre = (100,140)

    layer1 = d.add_layer('1-white')
    d.image_spiral_single(layer1, 'bear3.jpg', (100, 140), 20)
    
    layer2 = d.add_layer('2-gold')
    d.add_dot((100, 140), 24, container=layer2, stroke=svgwrite.rgb(255, 255, 0, '%'), r_start=22)
    d.add_dot((100, 140), 37, container=layer2, stroke=svgwrite.rgb(255, 255, 0, '%'), r_start=35)
    d.add_dot((100, 140), 50, container=layer2, stroke=svgwrite.rgb(255, 255, 0, '%'), r_start=48)
    d.add_square((50, 90), 100, start_size=96.4, container=layer2, stroke=svgwrite.rgb(255, 255, 0, '%'))
    d.add_dot((100, 140), 71, container=layer2, stroke=svgwrite.rgb(255, 255, 0, '%'), r_start=69)
    
    layer3 = d.add_layer('3-red')
    points = d.make_dot((100, 110), 3, xy_func=xy_heart, r_start = 2)
    d.add_rotated_polyline(points, centre, 16, stroke=svgwrite.rgb(255, 0, 0, '%'), container=layer3)
        
    points = d.make_dot((100, 79), 8, xy_func=xy_heart, r_start = 6)
    d.add_rotated_polyline(points, centre, 4, stroke=svgwrite.rgb(255, 0, 0, '%'), container=layer3)
    
    layer4 = d.add_layer('4-blue')
    points = d.make_dot((100, 181), 1)
    d.add_rotated_polyline(points, centre, 32, stroke=svgwrite.rgb(0, 0, 255, '%'), container=layer4)
    
    layer5 = d.add_layer('5-purple')
    points = d.make_dot((100, 181), 1)
    d.add_rotated_polyline(points, centre, 32, phase_add=0.5, stroke=svgwrite.rgb(255, 0, 255, '%'), container=layer5)
    
    layer6 = d.add_layer('6-silver')
    points = d.make_dot((100, 184), 1)
    d.add_rotated_polyline(points, centre, 64, phase_add=0.5, stroke=svgwrite.rgb(128, 128, 127, '%'), container=layer6)

    layer7 = d.add_layer('7-green')
    layer8 = d.add_layer('8-pink')
    add_checkboard(d, layer7, layer8, (54, 94), 2, 3)
    add_checkboard(d, layer7, layer8, (138, 94), 2, 3)
    add_checkboard(d, layer7, layer8, (54, 178), 2, 3)
    add_checkboard(d, layer7, layer8, (138, 178), 2, 3)

    layer9 = d.add_layer('9-blue')
    
    points = d.make_dot((120, 82), 5, r_start=4.25)
    d.add_rotated_polyline(points, centre, 4, stroke=svgwrite.rgb(0, 0, 255, '%'), container=layer9)
    points = d.make_dot((80, 82), 5, r_start=4.25)
    d.add_rotated_polyline(points, centre, 4, stroke=svgwrite.rgb(0, 0, 255, '%'), container=layer9)
    points = d.make_dot((120, 82), 1)
    d.add_rotated_polyline(points, centre, 4, stroke=svgwrite.rgb(0, 0, 255, '%'), container=layer9)
    points = d.make_dot((80, 82), 1)
    d.add_rotated_polyline(points, centre, 4, stroke=svgwrite.rgb(0, 0, 255, '%'), container=layer9)

    layer10 = d.add_layer('10-purple')
    points = d.make_dot((120, 82), 3, r_start=2.25)
    d.add_rotated_polyline(points, centre, 4, stroke=svgwrite.rgb(255, 0, 255, '%'), container=layer10)
    points = d.make_dot((80, 82), 3, r_start=2.25)
    d.add_rotated_polyline(points, centre, 4, stroke=svgwrite.rgb(255, 0, 255, '%'), container=layer10)
            
    layer12 = d.add_layer('12-test')
    d.add_square((50, 90), 100, start_size=99, container=layer12, stroke=svgwrite.rgb(255, 255, 0, '%'))
    
    layer13 = d.add_layer('13-test')
    d.add_dot((100, 140), 71, container=layer13, stroke=svgwrite.rgb(255, 255, 0, '%'), r_start=70)


def mothers_day(d):

    all_polylines = []
    
    pos = Point(105, 105)
    line = Point(0, 15)
    max_depth = 7
    cut = 2 / 3
    a_disp = math.pi / 6
    # a_disp = math.pi / 12
    num_branches = 21
    thickness_mm = 1.2
    layers = [d.add_layer("1-green"), d.add_layer("2-orange"), d.add_layer("3-yellow")]
    strokes = [svgwrite.rgb(0, 255, 0, '%'), svgwrite.rgb(255, 0, 0, '%'), svgwrite.rgb(255, 255, 0, '%')]
    # strokes = [svgwrite.rgb(255, 255, 255, '%'), svgwrite.rgb(255, 255, 255, '%'), svgwrite.rgb(255, 255, 255, '%')]
    inner_radius = 18
    for i in range(0, num_branches):
        ix_layer = i % 3
        layer = layers[ix_layer]
        stroke = strokes[ix_layer]
        disp_rot = StandardDrawing.rotate_about(Point(0, inner_radius), Point.Origin(), i * 2 * math.pi / num_branches)
        pos_start = pos + disp_rot
        branch_polylines = d.make_branch(pos_start, StandardDrawing.rotate_about(line, Point.Origin(), i * 2 * math.pi / num_branches), cut, a_disp, max_depth, thickness_mm)
        # don't bunch all the polylines together in a single bulk-add: there are loads of them and it'll make the optimisation of drawing order take ages
        d.add_polylines(branch_polylines, stroke=stroke, container=layer)
        
    layer4 = d.add_layer("4-dot")
    w = 0.8
    d.add_dot(pos, inner_radius-0*w, r_start=(inner_radius-1*w), stroke=svgwrite.rgb(64, 64, 64, '%'), container=layer4)

    layer5 = d.add_layer("5-text")
    inner_stroke = svgwrite.rgb(255, 255, 255, '%')
    family = "Sylfaen"
    family = "Arial"
    family = "Rubik"
    ext = d.text_bound("Mother's", 24, family=family)
    pos_text = pos - Point(ext.width/2, -ext.height/2)
    text_shapes = d.make_text("Mother's", pos_text, 24, family=family)
    sf = ShapeFiller(text_shapes)
    text_paths = sf.get_paths(d.pen_type.pen_width / 5)
    d.add_polylines(text_paths, container=layer5, stroke=inner_stroke)
    
    ext = d.text_bound("Happy", 24, family=family)
    pos_text = pos - Point(ext.width/2, -ext.height/2 + ext.height*1.5)
    text_shapes = d.make_text("Happy", pos_text, 24, family=family)
    sf = ShapeFiller(text_shapes)
    text_paths = sf.get_paths(d.pen_type.pen_width / 5)
    d.add_polylines(text_paths, container=layer5, stroke=inner_stroke)
    
    ext = d.text_bound("Day", 24, family=family)
    pos_text = pos - Point(ext.width/2, -ext.height/2 - ext.height*1.1)
    text_shapes = d.make_text("Day", pos_text, 24, family=family)
    sf = ShapeFiller(text_shapes)
    text_paths = sf.get_paths(d.pen_type.pen_width / 5)
    d.add_polylines(text_paths, container=layer5, stroke=inner_stroke)
    
    d.add_circle(pos, 60)

def draw_snowflake(drawing):

    import lsystem
    factor = 2.1
    all_lines = lsystem.test_lsystem_koch_snowflake(order=5, size=0.5)
    all_lines2= lsystem.test_lsystem_koch_snowflake(order=4, size=0.5*factor)
    all_lines3 = lsystem.test_lsystem_koch_snowflake(order=3, size=0.5*factor*factor)
    all_lines4 = lsystem.test_lsystem_koch_snowflake(order=2, size=0.5*factor*factor*factor)
    all_lines5 = lsystem.test_lsystem_koch_snowflake(order=1, size=0.5*factor*factor*factor*factor)

    def centre_on(polylines, new_centre):
        n = 0
        sumx = 0
        sumy = 0
        for line in polylines:
            for point in line[:-1]:
                n += 1
                sumx += point.x
                sumy += point.y
        centre = Point(sumx / n, sumy / n)
        adj = paper_centre - centre
        return [[p + adj for p in line] for line in polylines]
    
    # centre the drawing on the paper
    paper_centre = Point(102.5, 148)
    drawing.add_polylines(centre_on(all_lines, paper_centre))
    drawing.add_polylines(centre_on(all_lines2, paper_centre))
    drawing.add_polylines(centre_on(all_lines3, paper_centre))
    drawing.add_polylines(centre_on(all_lines4, paper_centre))
    drawing.add_polylines(centre_on(all_lines5, paper_centre))

    sf = ShapeFiller(centre_on(all_lines5, paper_centre))
    fill = sf.get_paths(2*drawing.pen_type.pen_width / 5)
    drawing.add_polylines(fill, container=drawing.add_layer("2-gold"), stroke=svgwrite.rgb(255, 255, 0, '%'))

    shapes = centre_on(all_lines3, paper_centre)
    shapes.extend(centre_on(all_lines4, paper_centre))
    sf = ShapeFiller(shapes)
    fill = sf.get_paths(2*drawing.pen_type.pen_width / 5)
    drawing.add_polylines(fill, container=drawing.add_layer("3-cyan"), stroke=svgwrite.rgb(0, 255, 255, '%'))

def draw_bridge_card(d):    

    centre = Point(102.5, 148)
    angle = 0
    family = 'Arial'
    cards = "♠♥♦♣"
    
    # try 24? 18 is a little blobby on the black
    fontsizeCards = 36
    fontsizeLetters = 18
    
    ext = d.text_bound(cards, fontsizeCards, family)
    h = ext.height * 1.2
    w = ext.width / 4 * 1.2
    
    fill = True
    
    nr = 18 # 24 # 24
    nc = 20 # 26 # 1
    i = 0
    lines1 = []
    lines2 = []
    lines3 = []
    letters = [ \
        (2, 2, "H"),(2, 3, "A"),(2, 4, "P"),(2, 5, "P"),(2, 6, "Y"), \
        (4, 2, "B"),(4, 3, "I"),(4, 4, "R"),(4, 5, "T"),(4, 6, "H"),(4, 7, "D"),(4, 8, "A"),(4, 9, "Y"), \
        (6, 2, "T"),(6, 3, "I"),(6, 4, "M") \
        ]
    letters = []

    linesPre = []
    r = -8
    c = nc / 2 + 1
    xm = c - 0.5 * (nc-1)
    ym = r - 0.5 * (nr-1)
    letter = "♥"
    pos_square_centre = centre + Point(w * xm, h * ym)
    letter_ext = d.text_bound(letter, fontsizeCards, family)
    pos_square_text = pos_square_centre - Point(letter_ext.width/2, -letter_ext.height/2)
    text_paths = d.make_text(letter, pos_square_text, fontsize=fontsizeCards, family=family)    
    if fill:
        sf = ShapeFiller(text_paths)
        filled_text_paths = sf.get_paths(d.pen_type.pen_width / 5)
        for p in filled_text_paths:
            linesPre.append(p)
    else:
        linesPre.extend(text_paths)
    d.add_polylines(linesPre, container=d.add_layer("5-pre_2"), stroke=svgwrite.rgb(0, 0, 100, '%'))
        
    for r in range(0, nr):
        for c in range(0, nc):
            i += 1
            
            a = [x[2] for x in letters if x[0] == r and x[1] == c]
            if len(a) == 1:
                letter = a[0]
                lines = lines3
                fontsize = fontsizeLetters
            else:
                fontsize = fontsizeCards
                indic = random.random() - 0.5 < 0
                is_black = (r + c % 2) % 2 == 0
                if is_black:
                    letter = cards[0] if indic else cards[3]
                    lines = lines1
                else:
                    letter = cards[1] if indic else cards[2]
                    lines = lines2
                    
            xm = c - 0.5 * (nc-1)
            ym = r - 0.5 * (nr-1)
            pos_square_centre = centre + Point(w * xm, h * ym)
            letter_ext = d.text_bound(letter, fontsize, family)
            pos_square_text = pos_square_centre - Point(letter_ext.width/2, -letter_ext.height/2)
            text_paths = d.make_text(letter, pos_square_text, fontsize=fontsize, family=family)

            if fill:
                sf = ShapeFiller(text_paths)
                filled_text_paths = sf.get_paths(d.pen_type.pen_width / 5)
                for p in filled_text_paths:
                    lines.append(p)
            else:
                lines.extend(text_paths)
            
    d.add_polylines(lines1, container=d.add_layer("1-black"), stroke=svgwrite.rgb(0, 0, 0, '%'))
    d.add_polylines(lines2, container=d.add_layer("2-red"), stroke=svgwrite.rgb(100, 0, 0, '%'))
    d.add_polylines(lines3, container=d.add_layer("3-green"), stroke=svgwrite.rgb(0, 0, 100, '%'))
    
    bound_w = 150
    bound_h = 148
    bound_tl = centre - Point(bound_w, bound_h) / 2
    d.add_rect(bound_tl, bound_w, bound_h, container=d.add_layer("4-border"))
