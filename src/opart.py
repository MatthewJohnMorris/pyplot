import math
import random

import svgwrite

from pyplot import CircleBlock, Point, ShapeFiller

def draw_riley_blaze(drawing):    

    nslice = 40    
    
    polylines = []
    
    centre = Point(102.5, 148)
    
    scale = 1.8
    
    for i in range(0, nslice):    
        b = CircleBlock(centre, 50*scale, 0, centre + Point(5, 5)*scale, 38*scale, 0.06, 2 * nslice, i * 2)
        path = drawing.fill_in_paths(b.path_gen_f)
        polylines.append(path)
        
        b = CircleBlock(centre + Point(5, 5)*scale, 38*scale, 0.06, centre + Point(-6, 2)*scale, 22*scale, -0.04, 2 * nslice, i * 2 + 1)
        path = drawing.fill_in_paths(b.path_gen_f)
        polylines.append(path)
        
        b = CircleBlock(centre + Point(-6, 2)*scale, 22*scale, -0.04, centre, 13*scale, 0.01, 2 * nslice, i * 2)
        path = drawing.fill_in_paths(b.path_gen_f)
        polylines.append(path)

    drawing.add_polylines(polylines)

def draw_riley_backoff_test(drawing):    

    nslice = 40    
    
    polylines = []
    
    centre = Point(22.5, 18)
    
    scale = 1
    
    for i in [3,4]: # range(3, 10): # 0, nslice):    
        b = CircleBlock(centre + Point(5, 5)*scale, 38*scale, 0.06, centre + Point(-6, 2)*scale, 22*scale, -0.04, 2 * nslice, i * 2 + 1)
        path = drawing.fill_in_paths(b.path_gen_f)
        drawing.add_polyline(path[::-1])

def draw_riley_movement_in_squares(drawing):    

    paper_centre = Point(102.5, 148)
    size = 90
    sq_size = 14
    n = 12
    top_y = paper_centre[1] - (n/2) * sq_size
    left_x = paper_centre[0] - (n/2) * sq_size
    right_x = paper_centre[0] + (n/2) * sq_size
    for r in range(0, n):
        y = top_y + sq_size * r
        x = left_x
        print(x,y)
        ix_x = 0
        a = 0
        x_width = sq_size
        while x < right_x:
            c = math.cos(a)
            x_factor = 0.06 + 0.94 * abs(math.pow(abs(c), 2.5))
            new_x = x + sq_size * x_factor
            if new_x > right_x:
                new_x = right_x
            print(x, y, new_x, x_factor)
            if (ix_x + r) % 2 == 1:
                shape = [(x, y), (new_x, y), (new_x, y + sq_size), (x, y + sq_size)]
                sf = ShapeFiller([shape])
                paths = sf.get_paths(drawing.pen_type.pen_width * 0.4)
                drawing.add_polylines(paths)
            x = new_x
            ix_x += 1
            a += math.pi / 29.6

def draw_xor_circles_othello(drawing):

    paper_centre = Point(102.5, 148)
    n = 20
    size = 6
    all_paths = []
    layer1 = drawing.add_layer("1-cyan")
    layer1_paths = []
    for r in range(0, n+1):
        x = paper_centre.x + (r - n/2)*size
        # print(x)
        for c in range(0, n+1):
            shapes = []
            y = paper_centre.y + (c - n/2)*size
            shapes.append(drawing.make_circle(Point(x,y), size/2))
            if(random.random() > 0.5):
                sf = ShapeFiller(shapes)
                paths = sf.get_paths(drawing.pen_type.pen_width * 0.4)
                layer1_paths.extend(paths)
                square = drawing.make_square(Point(x - size/2, y - size/2), size)
                shapes.append(square)
                
            sf = ShapeFiller(shapes)
            paths = sf.get_paths(drawing.pen_type.pen_width * 0.4)
            all_paths.extend(paths)
    
    drawing.add_polylines(all_paths)
    drawing.add_polylines(layer1_paths, container=layer1, stroke=svgwrite.rgb(0, 255, 255, '%'))

def spiral_moire(drawing):

    centre = Point(102.5, 148)
    scale = 80
    factor = 2
    
    side = 2
    h = side * 0.5 * math.sqrt(3)
    
    drawing.add_spiral(centre + Point(0, 0), scale, r_per_circle = (factor*1.00) * drawing.pen_type.pen_width)
    
    centre2 = centre + Point(0,5)
    all_polylines = [drawing.make_spiral(centre2, scale*1.09, r_per_circle = (factor*1.09) * drawing.pen_type.pen_width)]

    '''
    shapes = []
    for i in range(0,6):
        a = math.pi * 2 * i / 6
        shapes = []
        shapes.append(drawing.make_circle(centre + Point(math.cos(a), math.sin(a)) * scale * (2/3), scale * (1/3), n=100))
        sf = ShapeFiller(shapes)
        polylines = sf.clip(all_polylines, union=True, inverse=True)
        #for p in polylines:
        #    drawing.add_polyline(p)
        drawing.add_polylines(polylines)
        # drawing.add_polylines(shapes)
    shapes = []
    shapes.append(drawing.make_circle(centre, scale * (1/3), n=100))
    sf = ShapeFiller(shapes)
    polylines = sf.clip(all_polylines, union=True, inverse=True)
    drawing.add_polylines(polylines)
    '''

    shapes = []
    sgap = 9
    size = sgap
    while size < scale*2: # math.sqrt(2):
        shapes.append(drawing.make_square(centre - Point(size/2, size/2), size))
        size += sgap
    sf = ShapeFiller(shapes)
    polylines = sf.clip(all_polylines, inverse=True)
    shapes2 = [drawing.make_circle(centre, scale, n=100)]
    sf2 = ShapeFiller(shapes2)
    polylines = sf2.clip(polylines, inverse=True)
    drawing.add_polylines(polylines)
        
    # drawing.add_spiral(centre + Point(+side/2, h/3), scale, r_per_circle = (factor/1.05) * drawing.pen_type.pen_width)
    # drawing.add_spiral(centre + Point(0, -2*h/3), scale, r_per_circle = (factor/1.05) * drawing.pen_type.pen_width)
    # drawing.add_spiral(centre + Point(-disp, +disp), scale, r_per_circle = (factor/1.08) * drawing.pen_type.pen_width)
