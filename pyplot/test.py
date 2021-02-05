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
# seed random number generator
seed(10)

import math

from noise import pnoise1, pnoise2

from pyplot import CircleBlock, PenType, StandardDrawing
  
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

# coord is on [1, 1]
def z_func(norm_coord, seed):

    octaves = 2
    # 0 = perfectly smooth
    persistence = 0.5
    lacunarity = 6
    repeat = 1
    z = pnoise2(norm_coord[0]*repeat, norm_coord[1]*repeat,
                                        octaves=octaves,
                                        persistence=persistence,
                                        lacunarity=lacunarity,
                                        repeatx=repeat,
                                        repeaty=repeat,
                                        base=seed)
    return z
  
def plot_surface(drawing):

    # can render texture with z-function applied by preserving x, and doing y-out = y * cos(a) + z * sin(a) with a the viewing angle?  
    top_left = (130, 80)
    x_size = 70
    y_size = 20
    min_adj_y_for_x = {}
    seed = 200
    for y in range(0, y_size + 1, 2)[::-1]:
        points = []
        for x in range(0, x_size + 1):
            norm_coord = (x / x_size, y / y_size)
            z = z_func(norm_coord, seed) * 50
            a = math.pi * 3 /8
            y_adj = math.cos(a) * y + math.sin(a) * z
            min_adj_y = min_adj_y_for_x.get(x, 1000)
            if y_adj < min_adj_y:
                min_adj_y_for_x[x] = y_adj
            else:
                y_adj = min_adj_y
            points.append((top_left[0] + x, top_left[1] + y_adj))
        drawing.add_polyline(points)
  
def plot_perlin_drape_spiral(drawing, seed):  

    centre = (100, 70)
    r_base = 50
    circ = 2 * math.pi * r_base
    n = int(circ) + 1
    ni = 120
    target = n * ni
    iscale = r_base / ni * 2
    points = []
    for t in range(0, target):
        a = 2 * math.pi * (t / n)
        c = math.cos(a)
        s = math.sin(a)
        r_noise = z_func((a / (2 * math.pi), 0), seed)
        r_adj = r_base + r_noise * 150 * t / target
        pt = (centre[0] + r_adj * c, centre[1] + iscale * (t / n) + r_adj * s)
        points.append(pt)
    drawing.add_polyline(points)
  
def plot_perlin_spiral(drawing, centre, r_start, r_end, r_layer, seed, stroke=None, container=None):  

    circ = 2 * math.pi * r_end
    n = int(circ) * 2
    points = []
    layers = (r_end - r_start) / r_layer
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
        z = pnoise1(x,
            octaves=octaves,
            persistence=persistence,
            lacunarity=lacunarity,
            repeat=repeat,
            base=seed)
        
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

def draw_letter(dwg, letter, position, fontsize, angle=0, family='Arial'):

    g = dwg.g(style=f"font-size:{fontsize};font-family:{family};font-weight:normal;font-style:normal;stroke:black;fill:none") # stroke-width:1;
    
    x = position[0]
    y = position[1]
    f = dwg.text(letter, insert=(x, y)) # settings are valid for all text added to 'g'
    (w, h) = StandardDrawing.text_bound(letter, fontsize)
    cx = x + w/2
    cy = y - w/2
    g.add(dwg.text(letter, insert=(x, y), transform=f'rotate({angle}, {cx}, {cy})')) # settings are valid for all text added to 'g'
    dwg.add(g)

    (width1, foo) = StandardDrawing.text_bound("x", fontsize, family)
    (width2, foo) = StandardDrawing.text_bound(f"x{letter}x", fontsize, family)
    width = width2 - 2 * width1
    
    return (x + width, y)
    
def draw_text_by_letter(drawing, family='Arial'):
       
    fontsize = 10
    
    # family = 'CNC Vector' # good machine font
    # family = 'CutlingsGeometric' # spaces too big!
    # family = 'CutlingsGeometricRound' # spaces too big!
    # family = 'HersheyScript1smooth' # good "handwriting" font
    family = 'Stymie Hairline' # a bit cutsey, but ok
    
    ys = 40
    s = "all work and no play makes Jack a dull boy"
    (x, y) = (20, ys)
    for c in s:
        (x, y) = draw_letter(drawing.dwg, c, (x, y), fontsize, family=family)
            
    g = drawing.dwg.g(style=f"font-size:{fontsize};font-family:{family};font-weight:normal;font-style:normal;stroke:black;fill:none") # stroke-width:1;
    g.add(drawing.dwg.text(s, insert=(20, ys+20)))
    drawing.dwg.add(g)
            
    g = drawing.dwg.g(style=f"font-size:{fontsize};font-family:{family};font-weight:normal;font-style:normal;stroke:black;fill:none") # stroke-width:1;
    g.add(drawing.dwg.text("Jack ack Jack ack", insert=(20, ys+40)))
    drawing.dwg.add(g)

def r_z_func(norm_coord, seed):

    octaves = 2
    # 0 = perfectly smooth
    persistence = 0.5
    lacunarity = 6
    repeat = 1
    z = pnoise2(norm_coord[0]*repeat, norm_coord[1]*repeat,
                                        octaves=octaves,
                                        persistence=persistence,
                                        lacunarity=lacunarity,
                                        repeatx=repeat,
                                        repeaty=repeat,
                                        base=seed)
    return z

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
   
# Experimental. Can we get an even fill for large polygons?
# Ideally we would go for some sort of hatching/rasterization and make this
# fully generic. There is an issue with larger lines since the acceleration
# of GRBL results in gapping for ink. 
# One way out of this might be to have different speed limits for pen-up 
# pen-down and get fourxidraw.py to send the appropriate GRBL codes.   
def make_solid_poly(points, pen_width, inner_ratio=0):
    
    (cx, cy) = (0, 0)
    np = len(points)
    for point in points:
        cx += point[0]/np
        cy += point[1]/np
    # print(f"Centre={(cx, cy)}")
    max_dist = 0
    for point in points:
        dx = point[0] - cx
        dy = point[1] - cy
        dist = math.sqrt(dx*dx + dy*dy)
        max_dist = max(max_dist, dist)
    # print(f"max_dist={max_dist}")
    divs = int(max_dist * (1-inner_ratio) / (pen_width / 2)) + 1
    # divs = int(divs / 10)
    
    # we want to spiral OUTWARDS for a smooth fill
    solid_points = []
    # first go around the inside            
    if inner_ratio == 0:
        solid_points.append((cx, cy))
    else:
        for ip in range(0, np):
            sx = cx + (points[ip][0] - cx) * inner_ratio
            sy = cy + (points[ip][1] - cy) * inner_ratio
            solid_points.append((sx, sy))
    # now spiral out: 0 => 1, inner_ratio => divs
    for i in range(0, divs):
        mult_start = 1 + (inner_ratio - 1) * i / divs
        mult_end = 1 + (inner_ratio - 1) * (i+1) / divs
        for ip in range(0, np):
            mult = mult_start + (mult_end - mult_start) * ip / np
            mult = 1 - mult
            sx = cx + (points[ip][0] - cx) * mult
            sy = cy + (points[ip][1] - cy) * mult
            solid_points.append((sx, sy))
    # finally go around the outside
    for point in points:
        solid_points.append(point)
    solid_points.append(points[0])
    
    # print(f"total points: {len(solid_points)}")
    
    return solid_points

def test_solid_poly(drawing):
    points = [
        (40, 40), (42, 40), (44, 38), (46, 40),
        (48, 40), (48, 42), (50, 44), (48, 46),
        (48, 48), (46, 48), (44, 50), (42, 48),
        (40, 48), (40, 46), (38, 44), (40, 42)]
    for r in range(0, 8):
        for c in range(0, 8):
            points2 = [(p[0] + 12*r, p[1] + 12*c + 40) for p in points]
            solid_points2 = make_solid_poly(points2, drawing.pen_type.pen_width, inner_ratio = 0.8)
            drawing.add_polyline(solid_points2)

def test_triangle(drawing):
    points = [(40, 80), (65, 85), (50, 95)]
    solid_points2 = make_solid_poly(points, drawing.pen_type.pen_width)
    drawing.add_polyline(solid_points2)

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

d = StandardDrawing(pen_type = PenType.GellyRollOnBlack())
# d = StandardDrawing(pen_type = PenType.PigmaMicron05())

valentine(d)

'''
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
draw_text_by_letter(d)
random_rects(d)
plot_perlin_spirals(d)
d.add_spiral((60, 60), 30)
d.add_spiral((61.6666, 61.666), 30)
d.plot_spiral_text((100.75, 100.75), 60)
draw_riley(d)
draw_unknown_pleasures(d)
d.image_spiral_single(d.dwg, 'testCard_F.jpg', (100, 100), 40)
d.image_spiral_single(d.dwg, 'bear2.jpg', (100, 140), 20)
d.image_spiral_single(d.dwg, 'burroughs.jpg', (100, 100), 80, r_factor_func=r_z_func)
d.image_spiral_cmyk('testCard_F.jpg', (100, 120), 40)
plot_surface(d)
plot_perlin_drape_spiral(d, 6)
plot_perlin_drape_spiral(d, 8)
'''

d.dwg.save()
