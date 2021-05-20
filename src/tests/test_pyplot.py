import math
import pytest

from pyplot import CircleBlock, PenType, Point, StandardDrawing, ShapeFiller

def test_rotate_sense():

    # we have increaing y is down, increasing x is right
    # we want rotation to be +ve = clockwise
    # so in quarter turns about (0,0) we should get (1,0) -> (0,1) -> (-1,0) -> (0,-1) -> (1,0)
    r0 = (1,0)
    c = (0,0)
    angle = math.pi / 2
    r1 = StandardDrawing.rotate_about(r0, c, angle)
    r2 = StandardDrawing.rotate_about(r1, c, angle)
    r3 = StandardDrawing.rotate_about(r2, c, angle)
    r4 = StandardDrawing.rotate_about(r3, c, angle)
    
    assert r1[0] == pytest.approx(0)
    assert r1[1] == pytest.approx(1)
    assert r2[0] == pytest.approx(-1)
    assert r2[1] == pytest.approx(0)
    assert r3[0] == pytest.approx(0)
    assert r3[1] == pytest.approx(-1)
    assert r4[0] == pytest.approx(1)
    assert r4[1] == pytest.approx(0)

def test_circle_sense():

    # we have increasing y is down, increasing x is right
    # we want rotation to be +ve = clockwise
    d = StandardDrawing(pen_type = PenType.GellyRollMetallicOnBlack())
    c = d.make_circle((0,0), 1, n=4)
    assert(len(c) == 4)
    assert(c[0][0] == pytest.approx(0))
    assert(c[0][1] == pytest.approx(-1))
    assert(c[1][0] == pytest.approx(1))
    assert(c[1][1] == pytest.approx(0))
    assert(c[2][0] == pytest.approx(0))
    assert(c[2][1] == pytest.approx(1))
    assert(c[3][0] == pytest.approx(-1))
    assert(c[3][1] == pytest.approx(0))    
    
def get_text_scale_factor(text, fontsize, family):

    d = StandardDrawing()
    ext = d.text_bound(text, fontsize, family)
    
    tot_cw = 0
    for c in text:
        (w, _) = d.text_bound_letter(c, fontsize, family)
        tot_cw += w
        
    return ext.width/tot_cw
    
def test_text_bound_letter_matches_text_bound():

    # verify that if we plot letter-by-letter, we can match plotting the whole text at once
    families = ['CNC Vector', 'CutlingsGeometric', 'CutlingsGeometricRound', 'HersheyScript1smooth', 'Stymie Hairline']
    fontsizes = [6, 12, 60]
    texts = ["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz", "x                        x"]
    for family in families:
        for fontsize in fontsizes:
            for text in texts:
                s = get_text_scale_factor(text, fontsize, family)
                assert(abs(s - 1.0) < 0.015)
    
def test_inside_square():

    shape = [Point(1, 1), Point(1, 3), Point(3, 3), Point(3, 1)]
    shapes = [shape]
    sf = ShapeFiller(shapes)

    assert(not sf.is_inside(Point(2, 3)))

    # inside is inside
    assert(sf.is_inside(Point(2, 2)))
    
    # perimeter is outside
    assert(not sf.is_inside(Point(1, 1)))
    assert(not sf.is_inside(Point(1, 2)))
    assert(not sf.is_inside(Point(1, 3)))
    assert(not sf.is_inside(Point(2, 3)))
    assert(not sf.is_inside(Point(3, 3)))
    assert(not sf.is_inside(Point(3, 2)))
    assert(not sf.is_inside(Point(3, 1)))
    assert(not sf.is_inside(Point(2, 1)))
    
    # outside stuff is outside
    assert(not sf.is_inside(Point(0, 0)))
    assert(not sf.is_inside(Point(0, 2)))
    assert(not sf.is_inside(Point(0, 4)))
    assert(not sf.is_inside(Point(2, 4)))
    assert(not sf.is_inside(Point(4, 4)))
    assert(not sf.is_inside(Point(4, 2)))
    assert(not sf.is_inside(Point(4, 0)))
    assert(not sf.is_inside(Point(2, 0)))

def test_inside_diamond():

    shape = [Point(2, 1), Point(3, 2), Point(2, 3), Point(1, 2)]
    shapes = [shape]
    sf = ShapeFiller(shapes)

    # inside is inside
    assert(sf.is_inside(Point(2, 2)))
    
    # perimeter is outside
    assert(not sf.is_inside(Point(2, 1)))
    assert(not sf.is_inside(Point(3, 2)))
    assert(not sf.is_inside(Point(2, 4)))
    assert(not sf.is_inside(Point(1, 2)))
    
    # outside stuff is outside
    assert(not sf.is_inside(Point(0, 0)))
    assert(not sf.is_inside(Point(0, 4)))
    assert(not sf.is_inside(Point(4, 4)))
    assert(not sf.is_inside(Point(4, 0)))

def test_split_edges_square():

    shape = [Point(1, 1), Point(1, 3), Point(3, 3), Point(3, 1)]
    shapes = [shape]
    sf = ShapeFiller(shapes)

    assert(sf.split_edge_endpoints(Point(0,1), Point(4,1)) == [Point(1,1), Point(3,1), Point(4,1)])
    assert(sf.split_edge_endpoints(Point(0,2), Point(4,2)) == [Point(1,2), Point(3,2), Point(4,2)])
    assert(sf.split_edge_endpoints(Point(0,3), Point(4,3)) == [Point(1,3), Point(3,3), Point(4,3)])

    assert(sf.split_edge_endpoints(Point(0,0), Point(4,0)) == [Point(4,0)])
    assert(sf.split_edge_endpoints(Point(0,4), Point(4,4)) == [Point(4,4)])

def test_split_edges_diamond():

    shape = [Point(8, 4), Point(12, 12), Point(8, 20), Point(4, 12)]
    shapes = [shape]
    sf = ShapeFiller(shapes)

    assert(sf.split_edge_endpoints(Point(0,0),  Point(16,0))  == [Point(16,0)])
    assert(sf.split_edge_endpoints(Point(0,4),  Point(16,4))  == [Point(8,4),  Point(16,4)])
    assert(sf.split_edge_endpoints(Point(0,6),  Point(16,6))  == [Point(7,6),  Point(9,6),   Point(16,6)])
    assert(sf.split_edge_endpoints(Point(0,8),  Point(16,8))  == [Point(6,8),  Point(10,8),  Point(16,8)])
    assert(sf.split_edge_endpoints(Point(0,12), Point(16,12)) == [Point(4,12), Point(12,12), Point(16,12)])
    assert(sf.split_edge_endpoints(Point(0,16), Point(16,16)) == [Point(6,16), Point(10,16), Point(16,16)])
    assert(sf.split_edge_endpoints(Point(0,18), Point(16,18)) == [Point(7,18), Point(9,18),  Point(16,18)])
    assert(sf.split_edge_endpoints(Point(0,20), Point(16,20)) == [Point(8,20), Point(16,20)])
    assert(sf.split_edge_endpoints(Point(0,24), Point(16,24)) == [Point(16,24)])

def test_sort_polylines_zigzag():

    # Expect same order
    line1 = [Point(0, 0), Point(10, 0)]
    line2 = [Point(10, 1), Point(0, 1)]
    line3 = [Point(0, 2), Point(10, 2)]
    sorted = StandardDrawing.sort_polylines([line1, line2, line3])
    assert(sorted[0] == line1)
    assert(sorted[1] == line2)
    assert(sorted[2] == line3)

def test_sort_polylines_order():

    # Expect reordering as well as line3 reversed
    line1 = [Point(0, 0), Point(10, 0)]
    line2 = [Point(0, 2), Point(10, 2)]
    line3 = [Point(0, 1), Point(10, 1)]
    sorted = StandardDrawing.sort_polylines([line1, line2, line3])
    assert(sorted[0] == line1)
    assert(sorted[1] == line3[::-1])
    assert(sorted[2] == line2)

def test_point():
    
    pt = Point(100,50)
    pt2 = pt * 3
    assert(pt2.x == 300)
    assert(pt2.y == 150)

    pt3 = Point(1,2)
    pt4 = pt + pt3
    assert(pt4.x == 101)
    assert(pt4.y == 52)

    pt5 = Point.From((42, 43))
    assert(pt5.x == 42)
    assert(pt5.y == 43)
    
    pt6 = Point.From(pt5)
    assert(pt6.x == 42)
    assert(pt6.y == 43)
    
    pt7 = pt - pt3
    assert(pt7.x == 99)
    assert(pt7.y == 48)

def test_point_tuple():

    pt = Point(100, 50)
    
    (x, y) = pt

def test_point_dist():

    pt1 = Point(0, 1)
    assert(1 == pt1.dist())
    
    pt2 = Point(1, 0)
    assert(1 == pt2.dist())
    
    pt3 = Point(3, 4)
    assert(5 == pt3.dist())
    
def test_clip():

    disp = (0,5)
    shape1 = [Point(10, 10), Point(20, 10), Point(20, 20), Point(10, 20)]
    
    # all inside: clip everything
    shape2 = [Point(11, 11), Point(19, 11), Point(19, 19), Point(11, 19)]
    sf = ShapeFiller([shape1])
    polylines = sf.clip([shape2], union=True)
    assert(len(polylines) == 0)

    def clip_displaced_square(sf, disp):
        shape2 = [(x[0] + disp[0], x[1] + disp[1]) for x in shape1]
        shape2.append(shape2[0])
        return sf.clip([shape2], union=True)

    # on boundary - no clipping
    polylines = clip_displaced_square(sf, (0,0))
    assert(len(polylines) == 1)
    assert(len(polylines[0]) == 5)
    assert(polylines[0][0] == (10,10))
    assert(polylines[0][1] == (20,10))
    assert(polylines[0][2] == (20,20))
    assert(polylines[0][3] == (10,20))
    assert(polylines[0][4] == (10,10))

    # (15,15) - (25,15) - (25,25) - (15,25) - (15,15)
    polylines = clip_displaced_square(sf, (5,5))
    assert(len(polylines) == 1)
    assert(len(polylines[0]) == 5)
    print(polylines)
    assert(polylines[0][0] == (20,15))
    assert(polylines[0][1] == (25,15))
    assert(polylines[0][2] == (25,25))
    assert(polylines[0][3] == (15,25))
    assert(polylines[0][4] == (15,20))

    # (5,15) - (15,15) - (15,25) - (5,25) - (5,15)
    polylines = clip_displaced_square(sf, (-5,5))
    assert(len(polylines) ==2)
    assert(len(polylines[0]) == 2)
    assert(len(polylines[1]) == 4)
    assert(polylines[0][0] == (5,15))
    assert(polylines[0][1] == (10,15))
    assert(polylines[1][0] == (15,20))
    assert(polylines[1][1] == (15,25))
    assert(polylines[1][2] == (5,25))
    assert(polylines[1][3] == (5,15))

    # (5,5) - (15,5) - (15,15) - (5,15) - (5,5)
    polylines = clip_displaced_square(sf, (-5,-5))
    assert(len(polylines) ==2)
    assert(len(polylines[0]) == 3)
    assert(len(polylines[1]) == 3)
    assert(polylines[0][0] == (5,5))
    assert(polylines[0][1] == (15,5))
    assert(polylines[0][2] == (15,10))
    assert(polylines[1][0] == (10,15))
    assert(polylines[1][1] == (5,15))
    assert(polylines[1][2] == (5,5))

    # (15,5) - (25,5) - (25,15) - (15,15) - (15,5)
    polylines = clip_displaced_square(sf, (5,-5))
    assert(len(polylines) ==2)
    assert(len(polylines[0]) == 4)
    assert(len(polylines[1]) == 2)
    assert(polylines[0][0] == (15,5))
    assert(polylines[0][1] == (25,5))
    assert(polylines[0][2] == (25,15))
    assert(polylines[0][3] == (20,15))
    assert(polylines[1][0] == (15,10))
    assert(polylines[1][1] == (15,5))

def test_sort():

    n = 100
    unsorted = [ [Point(0, i), Point(10, i)] for i in range(0, n) ]
    sorted = StandardDrawing.sort_polylines_new(unsorted)
    print("hi")
    print(sorted)
    assert(False)
