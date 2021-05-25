from random import random, seed
import math

from pyplot import Point, ShapeFiller, StandardDrawing

def make_hash_square(tl, side, gap, a):

    centre = tl + Point(1, 1) * side / 2
    r = side * math.sqrt(2)
    gap = 2
    disp = 0
    while disp > -r / 2:
        disp -= gap
    unclipped_lines = []
    while disp < r / 2:
        unclipped_lines.append([centre + Point(- r/2,   disp), centre + Point(r/2, + disp)])
        disp += gap
        
    unclipped_lines = [[StandardDrawing.rotate_about(x, centre, a) for x in line] for line in unclipped_lines]
    c = math.cos(a)
    
    shape = [tl, tl + Point(side, 0), tl + Point(side, side), tl + Point(0, side)]
    sf = ShapeFiller([shape])
    return sf.clip(unclipped_lines, inverse=True)

def draw_hash_squares(d, base, side, gap, nlines):

    for r in range(0, 5):
        for c in range(0, 2):
            tl = base + Point(r, c) * side
    
            n = 0
            for i in range(0, nlines):
                one_big_line = []
                lines = make_hash_square(tl, side, gap, math.pi * random())
                for line in lines:
                    n += 1
                    if n % 2 == 0:
                        line = line[::-1]
                    one_big_line.extend(line)
                d.add_polyline(one_big_line)

def draw_hash(d):

    side = 20
    gap = 2
    draw_hash_squares(d, Point(30, 30), side, gap, 1)
    draw_hash_squares(d, Point(30, 80), side, gap, 2)
    draw_hash_squares(d, Point(30, 130), side, gap, 3)
    draw_hash_squares(d, Point(30, 180), side, gap, 4)
    draw_hash_squares(d, Point(30, 230), side, gap, 5)
        
def make_hash_square2(tl, side, gap, a, factor):

    centre = tl + Point(1, 1) * side / 2
    r = side * math.sqrt(2)
    gap = 2
    disp = 0
    while disp > -r / 2:
        disp -= gap
    unclipped_lines = []
    while disp < r / 2:
        line = []
        x = -r/2
        indic = -1
        while x < r/2:
            line.append(centre + Point(x, disp + indic*gap*factor))
            indic *= -1
            x += gap
        unclipped_lines.append(line)
        disp += gap
        
    unclipped_lines = [[StandardDrawing.rotate_about(x, centre, a) for x in line] for line in unclipped_lines]
    c = math.cos(a)
    
    shape = [tl, tl + Point(side, 0), tl + Point(side, side), tl + Point(0, side)]
    sf = ShapeFiller([shape])
    return sf.clip(unclipped_lines, inverse=True)


def draw_hash_squares2(d, base, side, gap, factor):

    for r in range(0, 5):
        for c in range(0, 2):
            tl = base + Point(r, c) * side
    
            n = 0
            one_big_line = []
            lines = make_hash_square2(tl, side, gap, math.pi * random(), factor)
            for line in lines:
                n += 1
                if n % 2 == 0:
                    line = line[::-1]
                one_big_line.extend(line)
            # d.add_polyline(one_big_line)
            d.add_polylines(lines)

def draw_hash2(d):

    side = 20
    gap = 2
    draw_hash_squares2(d, Point(30, 30), side, gap, 0.5)
    draw_hash_squares2(d, Point(30, 80), side, gap, 0.75)
    draw_hash_squares2(d, Point(30, 130), side, gap, 1)
    draw_hash_squares2(d, Point(30, 180), side, gap, 1.25)
    draw_hash_squares2(d, Point(30, 230), side, gap, 1.5)

def make_hash_square3(tl, side, gap, a, pen_width, factor):

    centre = tl + Point(1, 1) * side / 2
    r = side * math.sqrt(2)
    gap = 2
    disp = 0
    while disp > -r / 2:
        disp -= gap
    unclipped_lines = []
    while disp < r / 2:
        line = []
        x = -r/2
        a1 = 0
        x_inc = pen_width
        a_inc = math.pi * 2 * (x_inc / gap) * factor
        while x < r/2:
            line.append(centre + Point(x, disp + gap*math.sin(a1)*factor))
            x += x_inc
            a1 += a_inc
        unclipped_lines.append(line)
        disp += gap
        
    unclipped_lines = [[StandardDrawing.rotate_about(x, centre, a) for x in line] for line in unclipped_lines]
    c = math.cos(a)
    
    shape = [tl, tl + Point(side, 0), tl + Point(side, side), tl + Point(0, side)]
    sf = ShapeFiller([shape])
    return sf.clip(unclipped_lines, inverse=True)


def draw_hash_squares3(d, base, side, gap, factor):

    for r in range(0, 5):
        for c in range(0, 2):
            tl = base + Point(r, c) * side
    
            n = 0
            one_big_line = []
            lines = make_hash_square3(tl, side, gap, math.pi * random(), d.pen_type.pen_width, factor)
            for line in lines:
                n += 1
                if n % 2 == 0:
                    line = line[::-1]
                one_big_line.extend(line)
            # d.add_polyline(one_big_line)
            d.add_polylines(lines)

def draw_hash3(d):

    side = 20
    gap = 2
    draw_hash_squares3(d, Point(30, 30), side, gap, 0.4)
    draw_hash_squares3(d, Point(30, 80), side, gap, 0.55)
    draw_hash_squares3(d, Point(30, 130), side, gap, 0.7)
    draw_hash_squares3(d, Point(30, 180), side, gap, 0.85)
    draw_hash_squares3(d, Point(30, 230), side, gap, 1.0)
