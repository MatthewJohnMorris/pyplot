import math

import svgwrite

from pyplot import Point, ShapeFiller

def draw_big_a(d):

    paper_centre = Point(102.5, 148)
    fontsize = 96*8*0.5
    family="Arial"
    text = "ﷺ"
    ext = d.text_bound(text, fontsize=fontsize, family=family)
    text_place = Point(paper_centre.x - ext.width/2, paper_centre.y + ext.height/2)
    letter_paths = d.make_text(text, text_place, fontsize=fontsize, family=family)
    sf = ShapeFiller(letter_paths)
    paths = []
    for path in sf.get_paths(0.4*d.pen_type.pen_width, angle=math.pi/2): # math.pi/2):
        paths.append(path)
    
    d.add_polylines(paths, container=d.add_layer("1"), stroke=svgwrite.rgb(30, 100, 30, '%'))
    
    closed_letter_paths = []
    for letter_path in letter_paths:
        x = [_ for _ in letter_path]
        x.append(x[0])
        closed_letter_paths.append(x)
    
    d.add_polylines(closed_letter_paths, container=d.add_layer("0"))

def draw_word_square(d):

    d.add_polylines(d.make_word_square((20, 20), 96, 'Caslon Antique', ["SATOR","AREPO","TENET","OPERA","ROTAS"], angle=0))

def test_text_sizes(d):
    family='HersheyScript1smooth'
    fontsize=8
    d.add_text(f"{family}: {d.pen_type.name}", (20, 20), fontsize=fontsize, family=family)
    for fontsize in range(4, 13):
        d.add_text(f"{fontsize}pt: abcdefg", (20, 20 + 20 * (fontsize-3)), fontsize=fontsize, family=family)
       
def test_text_and_shape(d):

    letter_paths = d.make_text("TEST", (20, 80), 96, family="Arial")
    circle = d.make_circle((50, 70), 15)
    letter_paths.append(circle)
    sf = ShapeFiller(letter_paths)
    for path in sf.get_paths(4*d.pen_type.pen_width / 5, angle=math.pi/2):
        d.add_polyline(path)
       
def draw_text_by_letter_and_whole_for_comparison(drawing, family='Arial', s=None):
       
    fontsize = 20
    
    # family = 'CNC Vector' # good machine font
    # family = 'CutlingsGeometric' # spaces too big!
    # family = 'CutlingsGeometricRound' # spaces too big!
    # family = 'HersheyScript1smooth' # good "handwriting" font
    # family = 'Stymie Hairline' # a bit cutsey, but ok
    
    ys = 80
    s = "all work and no play makes Jack a dull boy" if s is None else s
    (x, y) = (20, ys)
    for c in s:
        drawing.add_text(c, (x, y), fontsize, family=family)
        (w, h) = drawing.text_bound_letter(c, fontsize, family=family)
        (x, y) = (x + w, y)

    drawing.add_text(s, (20, ys+20), fontsize, family=family)

def test_boxed_text(d):

    family='CutlingsGeometricRound'
    family='HersheyScript1smooth'
    family='CNC Vector'
    
    family='CNC Vector'
    position = (20, 40)
    for i in range(0, 10):
        fontsize = 12 + i
        ext = d.add_text(f"WAKEFIELD: {fontsize}pt", position, fontsize=fontsize, family=family)
        d.add_rect((position[0] - 2, position[1] + ext.y_bearing - 2), ext.width + 4, ext.height + 4)
        d.add_rect((position[0] - 2.2, position[1] + ext.y_bearing - 2.2), ext.width + 4.4, ext.height + 4.4)
        position = (position[0], position[1] + ext.height + 10)

    family='HersheyScript1smooth'
    position = (120, 40)
    for i in range(0, 10):
        fontsize = 12 + i
        ext = d.add_text(f"WAKEFIELD: {fontsize}pt", position, fontsize=fontsize, family=family)
        d.add_rect((position[0] - 2, position[1] + ext.y_bearing - 2), ext.width + 4, ext.height + 4)
        d.add_rect((position[0] - 2.2, position[1] + ext.y_bearing - 2.2), ext.width + 4.4, ext.height + 4.4)
        position = (position[0], position[1] + ext.height + 10)

