# necessary python modules
# * noise (for perlin stuff)
# * opencv-python
# * pycairo (for text)
# * svgwrite

import cv2

import csv

import svgwrite
from svgwrite.extensions import Inkscape

from random import random, seed
seed(10)

import math

from pyplot import CircleBlock, PenType, StandardDrawing, ShapeFiller
from perlin import PerlinNoise
from bezier import *
  
def draw_riley(drawing):    

    nslice = 40    
    
    for i in range(0, nslice):    
        b = CircleBlock((100, 100), 50, 0, (105, 105), 38, 0.06, 2 * nslice, i * 2)
        path = drawing.fill_in_paths(b.path_gen_f)
        drawing.add_polyline(path)
        
        b = CircleBlock((105, 105), 38, 0.06, (94, 102), 22, -0.04, 2 * nslice, i * 2 + 1)
        path = drawing.fill_in_paths(b.path_gen_f)
        drawing.add_polyline(path)
        
        b = CircleBlock((94, 102), 22, -0.04, (100, 100), 13, 0.01, 2 * nslice, i * 2)
        path = drawing.fill_in_paths(b.path_gen_f)
        drawing.add_polyline(path)

def draw_unknown_pleasures(drawing):

    min_y = {}
    data = []
    # File from https://github.com/igorol/unknown_pleasures_plot/blob/master/pulsar.csv
    with open('pulsar.csv') as csvfile:
        reader = csv.reader(csvfile)
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
    data = data[::-1]
    nrows = len(data)
    nitems = len(data[0])
    # print(f'We have {nrows} rows, each of which has {nitems} data items')
    y_min = 20
    y_max = 200
    x_min = 20
    x_max = 150
    y_scale = 0.28
    min_ys = {}
    for i in range(0, nrows):
        y_base = y_max + (y_min - y_max) * i / (nrows - 1)
        rowdata = data[i]
        path = []
        for j in range(0, nitems):
            x = x_min + (x_max - x_min) * j / (nitems - 1)
            min_y = min_ys.get(x, 10000.0)
            y = y_base - float(rowdata[j]) * y_scale
            if y < min_y:
                min_ys[x] = y
            else:
                y = min_y
            path.append((x, y))
        drawing.add_polyline(path)

def plot_perlin_drape_spiral(drawing, seed):  

    centre = (100, 70)
    r_base = 50
    circ = 2 * math.pi * r_base
    n = int(circ) + 1
    ni = 120
    target = n * ni
    iscale = r_base / ni * 2
    points = []
    p = PerlinNoise(seed=seed)
    
    for t in range(0, target):
        a = 2 * math.pi * (t / n)
        c = math.cos(a)
        s = math.sin(a)
        r_noise = p.calc2d((a / (2 * math.pi), 0))
        r_adj = r_base + r_noise * 150 * t / target
        pt = (centre[0] + r_adj * c, centre[1] + iscale * (t / n) + r_adj * s)
        points.append(pt)
    drawing.add_polyline(points)
  
def plot_perlin_spiral(drawing, centre, r_start, r_end, r_layer, seed, stroke=None, container=None):  

    circ = 2 * math.pi * r_end
    n = int(circ) * 2
    points = []
    layers = (r_end - r_start) / r_layer
    p = PerlinNoise(seed=seed)
    for t in range(0, int(n * layers)):
        a = 2 * math.pi * (t / n)
        c = math.cos(a)
        s = math.sin(a)
        
        octaves = 2
        # 0 = perfectly smooth
        persistence = 0.6
        lacunarity = 7
        repeat = 1
        x = a / (2 * math.pi)
        z = p.calc1d(x)
        
        r_now = r_start + (r_end - r_start) * t / (n * layers)
        r_adj = r_now + z * r_now * t / (n * layers)
        pt = (centre[0] + r_adj * c, centre[1] + r_adj * s)
        points.append(pt)
    drawing.add_polyline(points, stroke=stroke, container=container)

def plot_perlin_spirals(drawing):

    back_layer = drawing.add_layer('0-black')
    spiral_strokes = [svgwrite.rgb(255, 0, 0, '%'), svgwrite.rgb(0, 128, 0, '%'), svgwrite.rgb(0, 0, 255, '%')]
    spiral_layers = [drawing.add_layer('1-red'), drawing.add_layer('2-green'), drawing.add_layer('3-blue')]
    for i in range(0, 9):
        for j in range(0, 13):
            seed = 10 * i + j
            # for k in range(1, 7):
            #    plot_perlin_ring(drawing, (10*(i+1),10*(j+1)), k/2, seed)
            drawing.add_square((20*(i+1)-9,20*(j+1)-9),18,container=back_layer)
            drawing.add_square((20*(i+1)-9.2,20*(j+1)-9.2),18.4,container=back_layer)
            drawing.add_square((20*(i+1)-9.4,20*(j+1)-9.4),18.8,container=back_layer)
            for x in range(0, 2):
                i_layer = int(random() * 3)
                spiral_layer = spiral_layers[i_layer]
                spiral_stroke = spiral_strokes[i_layer]
                plot_perlin_spiral(drawing, (20*(i+1),20*(j+1)), 0.5, 6, 0.6, seed + i_layer, stroke=spiral_stroke, container=spiral_layer)
    
def random_rects(drawing):

    inner_tl = (100, 100)
    inner_ext = (50, 20)
    width = 0.4
    strokes = [svgwrite.rgb(101, 67, 33, '%'), svgwrite.rgb(128, 70, 0, '%'), svgwrite.rgb(255, 255, 0, '%'), svgwrite.rgb(255, 0, 0, '%')]
    layers = [drawing.add_layer('1-brown'), drawing.add_layer('2-orange'), drawing.add_layer('3-yellow'), drawing.add_layer('4-red')]
    for i in range(0, 100):
        i_tl = (inner_tl[0] - width*i, inner_tl[1] - width*i)
        i_ext = (inner_ext[0] + width*i*2, inner_ext[1] + width*i*2)
        i_layer = int(random() * 4)
        layer = layers[i_layer]
        stroke = strokes[i_layer]
        drawing.add_rect(i_tl, i_ext[0], i_ext[1], stroke=stroke, container=layer)

def multi_burroughs(drawing):
    layer1 = drawing.add_layer('1')
    drawing.image_spiral_single(layer1, 'burroughs.jpg', (100, 60), 30, svgwrite.rgb(255, 0, 0, '%'))
    layer2 = drawing.add_layer('2')
    drawing.image_spiral_single(layer2, 'burroughs.jpg', (100, 130), 30, svgwrite.rgb(255, 255, 0, '%'))
    layer3 = drawing.add_layer('3')
    drawing.image_spiral_single(layer3, 'burroughs.jpg', (100, 200), 30, svgwrite.rgb(0, 255, 0, '%'))

def text_smear(drawing):

    centre = (100,160)
    scale = 60
    text="testing, testing, one two three"
    d.plot_spiral_text(centre, scale, text=text, container=drawing.add_layer('1'), stroke=svgwrite.rgb(255, 0, 255, '%'), radial_adjust=-0.8)
    d.plot_spiral_text(centre, scale, text=text, container=drawing.add_layer('2'), stroke=svgwrite.rgb(255, 0, 0, '%'), radial_adjust=-0.4)
    d.plot_spiral_text(centre, scale, text=text, container=drawing.add_layer('3'), stroke=svgwrite.rgb(255, 255, 255, '%'), radial_adjust=-0.0)

def text_in_circle(drawing):

    centre = (100,160)
    radius = 30
    layer = drawing.add_layer('1')
    for angle in range(0, 360, 30):
        drawing.add_spiral_letter("X", 6, centre, radius, angle=angle, family='CNC Vector', container=layer)
    drawing.add_dot(centre, radius + 7.3, r_start = radius  + 5.8, stroke=svgwrite.rgb(255, 255, 0, '%'), container=layer)
    drawing.add_dot(centre, radius - 1.8, r_start = radius  - 3.3, stroke=svgwrite.rgb(255, 255, 0, '%'), container=layer)

def burroughs_medal(d):
    # print("medal")
    d.image_spiral_single(d.add_layer('2'), 'burroughs.jpg', (100, 160), 25)
    text_in_circle(d)

def test_dots(d):

    for r in range(0, 8):
        layer = d.add_layer(f'{r+1}')
        for c in range(0, 8):
            d.add_dot((44 + 12*c, 44 + 40 + 12*r), 1.5, container=layer)
            
def test_dots2(d):

    for r in range(0, 8):
        layer = d.add_layer(f'{r+1}')
        for c in range(0, 8):
            d.add_dot((10 + 4*c + 32 * 4, 10 + 4*r), 1.7, container=layer, r_start = 1.4)
            
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


def test_height(d):

    # x: 20 to 180 -> 160 gap, 5 
    # y: 20 to 260 -> 240 gap, 7
    dotsize = 1
    sqsize = 3
    for x in range(20, 200, 40):
        for y in range(20, 280, 40):
            d.add_dot((x, y), dotsize)

def test_shape_filler(d):

    '''
    yd = -45
    points = [
        [(50, 150+yd), (50, 160+yd), (60, 160+yd), (60, 150+yd)],
        [(53, 153+yd), (53, 157+yd), (57, 157+yd), (57, 153+yd)],
        ]
        '''

    centre = (50,50)
    star = []    
    n = 5
    for i in range(0, 2 * n):
        a = 2 * math.pi * i / (2*n)
        r = 7 + 11 * (i % 2)
        c = d.get_circle_point(centre, r, a)
        star.append(c)
    points = [star]
    # points = []
    points.append(d.make_circle(centre, 7, int(5*2*math.pi*2)))
    points.append(d.make_circle(centre, 9, int(9*2*math.pi*2)))
    points.append(d.make_circle(centre, 11, int(11*2*math.pi*2)))
    points.append(d.make_circle(centre, 18, int(18*2*math.pi*2)))
    points.append(d.make_circle(centre, 20, int(20*2*math.pi*2)))

    angle = 0.45*math.pi+(105/360)*2*math.pi
    # angle=0
    sf = ShapeFiller(points)
    for path in sf.get_paths(10*d.pen_type.pen_width / 5, angle=angle):
    # for path in sf.get_paths(3):
        d.add_polyline(path)

def complex_fill(d):

    points = []
    centre = (150,50)
    sq = d.make_rect(centre, 20, 20)
    points = d.make_rotated_polyline(sq, centre, 13)
    sf = ShapeFiller(points)
    for path in sf.get_paths(4*d.pen_type.pen_width / 5, angle=math.pi/2):
        d.add_polyline(path)

def fill_test(d):

    points = []
    for i in range(1, 11):
        tl = (80,20+20*i)
        sq = d.make_rect(tl, 18, 18)
        sf = ShapeFiller([sq])
        for path in sf.get_paths(i*d.pen_type.pen_width / 10):
            d.add_polyline(path)

def plot_surface(drawing):

    # can render texture with z-function applied by preserving x, and doing y-out = y * cos(a) + z * sin(a) with a the viewing angle?  
    top_left = (30, 30)
    x_size = 140
    y_size = 240
    p = PerlinNoise(scale=100)
    d.add_surface(top_left, x_size, y_size, p.calc2d)

def test_text_sze():
    family='HersheyScript1smooth'
    fontsize=8
    d.add_text(f"{family}: {d.pen_type.name}", (20, 20), fontsize=fontsize, family=family)
    for fontsize in range(4, 13):
        d.add_text(f"{fontsize}pt: abcdefg", (20, 20 + 20 * (fontsize-3)), fontsize=fontsize, family=family)

        
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

def speed_limit_test(d):
    mult = 0.4
    layer = d.add_layer("1")
    for j in range(0, 5):
        x = 20 + 10 * j
        y = 20
        for i in range(0, 10):
            x += d.pen_type.pen_width * mult
            d.add_polyline([(x, y), (x, y + 5 * (j+1))], container=layer)
    layer = d.add_layer("2")
    for j in range(0, 5):
        x = 120 + 10 * j
        y = 20
        for i in range(0, 10):
            x += d.pen_type.pen_width * mult
            d.add_polyline([(x, y), (x, y + 5 * (j+1))], container=layer)
    layer = d.add_layer("3")
    for j in range(0, 5):
        x = 20 + 10 * j
        y = 70
        for i in range(0, 10):
            x += d.pen_type.pen_width * mult
            d.add_polyline([(x, y), (x, y + 5 * (j+1))], container=layer)
    layer = d.add_layer("4")
    for j in range(0, 5):
        x = 120 + 10 * j
        y = 70
        for i in range(0, 10):
            x += d.pen_type.pen_width * mult
            d.add_polyline([(x, y), (x, y + 5 * (j+1))], container=layer)
    layer = d.add_layer("5")
    for j in range(0, 5):
        x = 20 + 10 * j
        y = 120
        for i in range(0, 10):
            x += d.pen_type.pen_width * mult
            d.add_polyline([(x, y), (x, y + 5 * (j+1))], container=layer)
    layer = d.add_layer("6")
    for j in range(0, 5):
        x = 120 + 10 * j
        y = 120
        for i in range(0, 10):
            x += d.pen_type.pen_width * mult
            d.add_polyline([(x, y), (x, y + 5 * (j+1))], container=layer)
    layer = d.add_layer("7")
    for j in range(0, 5):
        x = 20 + 10 * j
        y = 170
        for i in range(0, 10):
            x += d.pen_type.pen_width * mult
            d.add_polyline([(x, y), (x, y + 5 * (j+1))], container=layer)
    layer = d.add_layer("8")
    for j in range(0, 5):
        x = 120 + 10 * j
        y = 170
        for i in range(0, 10):
            x += d.pen_type.pen_width * mult
            d.add_polyline([(x, y), (x, y + 5 * (j+1))], container=layer)

def get_image_intensity(image, x, y):

    (xsize_image,ysize_image,c) = image.shape
    x_int = int(x+0.5)
    y_int = int(y+0.5)
    if x_int < 0 or x_int >= xsize_image or y_int < 0 or y_int >= ysize_image:
        return 0
    return image[x_int, y_int][0] / 255

def set_image_intensity(image, x, y, value):

    (xsize_image,ysize_image,c) = image.shape
    x_int = int(x+0.5)
    y_int = int(y+0.5)
    if x_int < 0 or x_int >= xsize_image or y_int < 0 or y_int >= ysize_image:
        return
    image[x_int, y_int][0] = value

def image_sketch(d):

    layer1 = d.add_layer("1")
    layer2 = d.add_layer("1")

    image = cv2.imread('burroughs2.jpg') #The function to read from an image into OpenCv is imread()
    (xsize_image,ysize_image,c) = image.shape
    
    print(image.shape)
    
    x_extent = 100
    # mm per pixel
    scale = x_extent / ysize_image
    r = x_extent / 20
    offset = (20, 20)
    
    intensity = lambda x, y: get_image_intensity(image, x, y)
    
    polylines = []
    n = 37
    angles = [i * 2 * math.pi / n for i in range(0, n)]
    trigs = [(math.cos(a), math.sin(a)) for a in angles]
    polyline = []
    pt = None
    expavg_ntries = 0
    for i in range(0, 30000):
        if i % 100 == 0:
            print(f"points={i} expavg_ntries={expavg_ntries:.2f}")

        ntries = 0
        while pt is None:
            ntries += 1
            x = random() * xsize_image
            y = random() * ysize_image
            pt1 = (x, y)
            k = intensity(pt1[0], pt1[1])
            if k >= 0.35:
                pt = pt1
            else:
                if 0.9 * expavg_ntries + 0.1 * ntries > 100:
                    break
                
        if pt is None:
            print("Breaking")
            break
        expavg_ntries = 0.9 * expavg_ntries + 0.1 * ntries
        
        r = 5 + int(random()*5)
        # r = 3 + int(random()*20) # this is too long - skips over black areas
        r = 10

        threshold = 0.10
        
        best_max_avg_intensity = -1
        max_trig = None
        max_best_j = 0
        for trig in trigs:
            total_intensity = 0
            max_avg_intensity = -1
            min_intensity = 1
            best_j = 0
            for j in range(1, r):
                k = intensity(pt[0]+j*trig[0], pt[1]+j*trig[1])
                if k < threshold:
                    break
                total_intensity += k
                j_avg_intensity = total_intensity / j
                if j_avg_intensity > max_avg_intensity:
                    best_j = j
                    max_avg_intensity = j_avg_intensity
                
            avg_intensity = total_intensity / r
            if max_avg_intensity > best_max_avg_intensity:
                best_max_avg_intensity = max_avg_intensity
                max_trig = trig
                max_best_j = best_j
                
        # zero out in the image
        # set_image_intensity(image, pt[0], pt[1], 0)
        if best_max_avg_intensity > threshold:
            if len(polyline) == 0:
                polyline = [(pt[1]*scale, pt[0]*scale)]

            for j in range(0, max_best_j):
                pt_j = (pt[0]+j*max_trig[0], pt[1]+j*max_trig[1])
                f0 = pt_j[0] - int(pt_j[0])
                f1 = pt_j[1] - int(pt_j[1])
                up0 = xsize_image - 1 if pt_j[0] == xsize_image else pt_j[0] + 1
                up1 = ysize_image - 1 if pt_j[1] == ysize_image else pt_j[1] + 1
                drop = 1
                set_image_intensity(image, pt_j[0], pt_j[1], max(0, intensity(pt_j[0], pt_j[1]) - drop * (1-f0) * (1-f1)))
                set_image_intensity(image, up0, pt_j[1], max(0, intensity(up0, pt_j[1]) - drop * f0 * (1-f1)))
                set_image_intensity(image, up0, up1, max(0, intensity(up0, up1) - drop * f0 * f1))
                set_image_intensity(image, pt_j[0], up1, max(0, intensity(pt_j[0], up1) - drop * (1-f0) * f1))

            line_end = (pt[0]+max_best_j*max_trig[0], pt[1]+max_best_j*max_trig[1])
            polyline.append((line_end[1]*scale, line_end[0]*scale))
            pt = line_end
        else:
            if len(polyline) > 0:
                polylines.append(polyline)
                polyline = []
            pt = None
        
    print(len(polylines))
        
    for polyline in polylines:
        d.add_polyline([(p[0]+offset[0], p[1]+offset[1]) for p in polyline])

def test_text_and_shape(d):

    letter_paths = d.make_text("TEST", (20, 80), 96, family="Arial")
    circle = d.make_circle((50, 70), 15)
    letter_paths.append(circle)
    sf = ShapeFiller(letter_paths)
    for path in sf.get_paths(4*d.pen_type.pen_width / 5, angle=math.pi/2):
        d.add_polyline(path)

def draw_unknown_pleasures_clip(drawing):

    min_y = {}
    data = []
    # File from https://github.com/igorol/unknown_pleasures_plot/blob/master/pulsar.csv
    with open('pulsar.csv') as csvfile:
        reader = csv.reader(csvfile)
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
    data = data[::-1]
    nrows = len(data)
    nitems = len(data[0])
    # print(f'We have {nrows} rows, each of which has {nitems} data items')
    y_min = 20
    y_max = 200
    x_min = 20
    x_max = 150
    y_scale = 0.28
    min_ys = {}
    
    polylines = []
    for i in range(0, nrows):
        y_base = y_max + (y_min - y_max) * i / (nrows - 1)
        rowdata = data[i]
        path = []
        for j in range(0, nitems):
            x = x_min + (x_max - x_min) * j / (nitems - 1)
            min_y = min_ys.get(x, 10000.0)
            y = y_base - float(rowdata[j]) * y_scale
            if y < min_y:
                min_ys[x] = y
            else:
                y = min_y
            path.append((x, y))
        polylines.append(path)
            
    shapes = [d.make_circle((100, 100), 50), d.make_circle((80, 110), 20)]
    sf = ShapeFiller(shapes)
    clipped_polylines = sf.clip(polylines)
         
    for polyline in clipped_polylines:
        drawing.add_polyline(polyline)



# Note - if you use GellyRollOnBlack you will have a black rectangle added (on a layer whose name starts with "x") so you
# can get some idea of what things will look like - SVG doesn't let you set a background colour. You should either delete this rectangle
# before plotting, or use the "Layers" tab to plot - by default everything is written to layer "0-default"
d = StandardDrawing(pen_type = PenType.GellyRollOnBlack())
# d = StandardDrawing(pen_type = PenType.PigmaMicron05())

draw_unknown_pleasures_clip(d)

'''
test_text_and_shape(d)
image_sketch(d)
speed_limit_test(d)
test_boxed_text(d)
draw_riley(d)
fill_test(d)
test_shape_filler(d)
valentine(d)
burroughs_medal(d)
test_height(d)
test_hearts(d)
test_dots(d)
test_dots2(d)
test_solid_poly(d)
test_triangle(d)
text_smear(d)
multi_burroughs(d)
draw_text_by_letter_and_whole_for_comparison(d, family='CNC Vector') # , s="a l l w o r k a n d n o p l a y m a k e s jackadullboy")
random_rects(d)
plot_perlin_spirals(d)
d.add_spiral((60, 60), 30)
d.add_spiral((61.6666, 61.666), 30)
d.add_spiral_text((100.75, 100.75), 60)
draw_unknown_pleasures(d)
d.image_spiral_single(d.dwg, 'testCard_F.jpg', (100, 100), 40)
d.image_spiral_single(d.dwg, 'bear2.jpg', (100, 140), 20)
d.image_spiral_single(d.dwg, 'burroughs.jpg', (100, 100), 80)
d.image_spiral_cmyk('testCard_F.jpg', (100, 120), 40)
plot_surface(d)
plot_perlin_drape_spiral(d, 6)
plot_perlin_drape_spiral(d, 8)
'''

d.dwg.save()