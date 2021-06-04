import math

from pyplot import Point, ShapeFiller

# Use this for a bunch of test areas on pen quality
def line_quality_test(drawing):

    i_layer = 1
    pos0 = Point(20, 20)
    
    for x in range(0, 105, 50):
        for y in range(0, 205, 25):
            pos = pos0 + Point(x,y)
            points = []
            for i in range(0, 20, 2):
                points.append(pos + Point(0, i))
                points.append(pos + Point(18,i))
                points.append(pos + Point(18,i+1))
                points.append(pos + Point(0,i+1))
            points.append(pos + Point(0,20))
            points.append(pos + Point(19,20))
            points.append(pos + Point(19,0))
            for i in range(0, 20, 2):
                points.append(pos + Point(20+i, 0))
                points.append(pos + Point(20+i, 20))
                points.append(pos + Point(21+i, 20))
                points.append(pos + Point(21+i, 0))
            drawing.add_polyline(points, container=drawing.add_layer(f'{i_layer}-layer'))
            i_layer += 1

def speed_limit_test(d):
    mult = 0.4
    bases = [Point(20, 20), Point(120,20), Point(20, 70), Point(120, 70), Point(20, 120), Point(120, 120), Point(20, 170), Point(120, 170)]
    ix_layer = 1
    for base in bases:
        layer = d.add_layer(str(ix_layer))
        for j in range(0, 5):
            x = base.x + 10 * j
            y = base.y
            for i in range(0, 10):
                x += d.pen_type.pen_width * mult
                d.add_polyline([(x, y), (x, y + 5 * (j+1))], container=layer)
        ix_layer += 1

def fill_test(d):

    points = []
    for j in range(0, 8):
        layer = d.add_layer(f'{j+1}-layer')
        for i in range(2, 11):
            tl = (20+20*j,20+20*i)
            sq = d.make_rect(tl, 18, 18)
            sf = ShapeFiller([sq])
            for path in sf.get_paths(i*d.pen_type.pen_width / 10):
                d.add_polyline(path, container=layer)

def complex_fill(d):

    points = []
    centre = (150,50)
    sq = d.make_rect(centre, 20, 20)
    points = d.make_rotated_polyline(sq, centre, 13)
    sf = ShapeFiller(points)
    for path in sf.get_paths(4*d.pen_type.pen_width / 5, angle=math.pi/2):
        d.add_polyline(path)

def test_drawing_extent(d):

    # x: 20 to 180 -> 160 gap, 5 
    # y: 20 to 260 -> 240 gap, 7
    dotsize = 1
    sqsize = 3
    # y 10 restored
    centres = [ (8,10), (8,286), (197,286), (197,10)]
    d.add_polygon(centres)
    # true centre = (102.5, 148)?
    # round to (102, 148)

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

def test_bounds(d):

    paper_centre = Point(102.5, 148)
    paper_size = Point(192, 270)
    topleft = paper_centre - paper_size / 2
    polyline = [topleft, topleft + Point(0, paper_size.y), topleft + paper_size, topleft + Point(paper_size.x, 0), topleft]
    d.add_polyline(polyline)
