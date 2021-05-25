import math
import svgwrite

from pyplot import Point

def add_spirograph(drawing, centre, r, s, scale, container=None, stroke=None):

    def gcd(a,b):
        """Compute the greatest common divisor of a and b"""
        while b > 0:
            a, b = b, a % b
        return a
        
    def lcm(a, b):
        """Compute the lowest common multiple of a and b"""
        return a * b / gcd(a, b)
        
    a = [0 for _ in r]
    a_inc = drawing.pen_type.pen_width / r[0]
    path = []
    # need enough incr so both have whole # of rotations
    x = [max(rx, 1) for rx in r]
    n1 = lcm(lcm(lcm(x[0], x[1]), x[2]), x[3]) / r[0]
    circ1 = math.pi * 2 / a_inc
    limit = int(n1 * circ1) + 10
    for i in range(0, limit):
        a[0] += s[0] * a_inc * r[0] / x[0]
        a[1] += s[1] * a_inc * r[0] / x[1]
        a[2] += s[2] * a_inc * r[0] / x[2]
        a[3] += s[3] * a_inc * r[0] / x[3]
        p = centre
        for j in range(0,4):
            pt = Point(math.cos(a[j]), math.sin(a[j]))
            mult = 0
            for k in range(j, 4):
                mult += r[k]*s[k]
            pt = pt * mult * s[j]
            p = p + pt * scale
        path.append(p)
            
    drawing.add_polyline(path, container=container, stroke=stroke)

def spirograph1(drawing):

    paper_centre = Point(102.5, 148)
    r = [80, 35, 8, 2]
    s = [1, -1, 1, -1]
    add_spirograph(drawing, paper_centre, r, s, scale=0.2)
    add_spirograph(drawing, paper_centre, r, s, scale=1)

def spirograph2(drawing):

    paper_centre = Point(102.5, 148)
    r = [80, 25, 2, 1]
    s = [1, -1, 1, -1]
    add_spirograph(drawing, paper_centre, r, s, scale=0.35)
    add_spirograph(drawing, paper_centre, r, s, scale=1)

def spirograph3(drawing):

    paper_centre = Point(102.5, 148)
    r = [70, 30, 13, 7]
    s = [1, -1, 1, -1]
    add_spirograph(drawing, paper_centre, r, s, scale=1)

def spirograph4(drawing):

    paper_centre = Point(102.5, 148)
    r = [70, 32, 1, 2]
    s = [1, -1, 1, -1]
    add_spirograph(drawing, paper_centre, r, s, scale=1)

def spirograph5(drawing):

    paper_centre = Point(102.5, 148)
    r = [70, 3, 2, 1]
    s = [1, -1, 1, -1]
    add_spirograph(drawing, paper_centre, r, s, scale=1, stroke=svgwrite.rgb(100, 0, 0, '%'), container=drawing.add_layer("1"))
    r = [60, 22, 3, 1]
    s = [1, -1, 1, -1]
    add_spirograph(drawing, paper_centre, r, s, scale=1, stroke=svgwrite.rgb(0, 0, 0, '%'), container=drawing.add_layer("2"))
    r = [13, 7, 1, 0]
    s = [1, -1, 1, -1]
    add_spirograph(drawing, paper_centre, r, s, scale=1, stroke=svgwrite.rgb(50, 0, 0, '%'), container=drawing.add_layer("3"))

def spirograph6(drawing):

    paper_centre = Point(102.5, 148)
    r = [70, 3, 2, 1]
    s = [1, -1, 1, -1]
    scale = 1
    for i in range(0, 20):
        add_spirograph(drawing, paper_centre, r, s, scale=scale, stroke=svgwrite.rgb(0, 0, 0, '%'), container=drawing.add_layer("1"))
        scale *= 0.9
    drawing.add_dot(paper_centre, 75, r_start=73, stroke=svgwrite.rgb(50, 0, 0, '%'), container=drawing.add_layer("2"))

def spirograph7(drawing):

    paper_centre = Point(102.5, 148)
    r = [48, 7, 18, 0]
    s = [1, 1, -1, 1]
    add_spirograph(drawing, paper_centre, r, s, scale=1)

def spirograph8(drawing):

    layers = [drawing.add_layer("1"), drawing.add_layer("2"), drawing.add_layer("3")]
    strokes = [svgwrite.rgb(100, 0, 0, '%'), svgwrite.rgb(0, 100, 0, '%'), svgwrite.rgb(0, 0, 100, '%')]

    paper_centre = Point(102.5, 148)
    rnd = 0
    for r1 in range(10, 71, 10):
        r = [r1, 2, 1, 2]
        s = [1, -1, 1, -1]

        add_spirograph(drawing, paper_centre, r, s, scale=0.85, container=layers[rnd], stroke=strokes[rnd])
        add_spirograph(drawing, paper_centre, r, s, scale=0.9, container=layers[rnd], stroke=strokes[rnd])
        add_spirograph(drawing, paper_centre, r, s, scale=0.95, container=layers[rnd], stroke=strokes[rnd])
        add_spirograph(drawing, paper_centre, r, s, scale=1, container=layers[rnd], stroke=strokes[rnd])
        add_spirograph(drawing, paper_centre, r, s, scale=1.05, container=layers[rnd], stroke=strokes[rnd])
        add_spirograph(drawing, paper_centre, r, s, scale=1.1, container=layers[rnd], stroke=strokes[rnd])
        add_spirograph(drawing, paper_centre, r, s, scale=1.15, container=layers[rnd], stroke=strokes[rnd])
        rnd = rnd + 1
        if rnd == 3:
            rnd = 0

def spirograph9(drawing):

    paper_centre = Point(102.5, 148)
    
    r = [40, 5, 13, 5]
    s = [1, 1, -1, 1]
    # add_spirograph(drawing, paper_centre, r, s, scale=1)

    r = [48, 5, 0, 0]
    s = [1, 1, 1, 1]
    # add_spirograph(drawing, paper_centre, r, s, scale=1)

    r = [25, 7, 1, 0]
    s = [1, -1, -1, 1]
    # add_spirograph(drawing, paper_centre, r, s, scale=1)

    r = [61, 3, 1, 1]
    s = [1, 1, -1, 1]
    # add_spirograph(drawing, paper_centre, r, s, scale=1)

def spirograph10(drawing):

    paper_centre = Point(102.5, 148)
    
    strokes = [svgwrite.rgb(100, 100, 0, '%'), svgwrite.rgb(0, 100, 100, '%'), svgwrite.rgb(100, 0, 100, '%')]
    layers = [drawing.add_layer("1"), drawing.add_layer("2"), drawing.add_layer("3")]
    n = 0
    for outer in range(10, 75):
        n += 1
        n = n % 3
        r = [outer, 3, 0, 0]
        s = [1, 1, -1, 1]
        add_spirograph(drawing, paper_centre, r, s, scale=1, stroke=strokes[n], container=layers[n])
