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
    d = StandardDrawing(pen_type = PenType.GellyRollOnBlack())
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

    shape = [(1, 1), (1, 3), (3, 3), (3, 1)]
    shapes = [shape]
    sf = ShapeFiller(shapes)

    assert(not sf.is_inside((2, 3)))

    # inside is inside
    assert(sf.is_inside((2, 2)))
    
    # perimeter is outside
    assert(not sf.is_inside((1, 1)))
    assert(not sf.is_inside((1, 2)))
    assert(not sf.is_inside((1, 3)))
    assert(not sf.is_inside((2, 3)))
    assert(not sf.is_inside((3, 3)))
    assert(not sf.is_inside((3, 2)))
    assert(not sf.is_inside((3, 1)))
    assert(not sf.is_inside((2, 1)))
    
    # outside stuff is outside
    assert(not sf.is_inside((0, 0)))
    assert(not sf.is_inside((0, 2)))
    assert(not sf.is_inside((0, 4)))
    assert(not sf.is_inside((2, 4)))
    assert(not sf.is_inside((4, 4)))
    assert(not sf.is_inside((4, 2)))
    assert(not sf.is_inside((4, 0)))
    assert(not sf.is_inside((2, 0)))

def test_inside_diamond():

    shape = [(2, 1), (3, 2), (2, 3), (1, 2)]
    shapes = [shape]
    sf = ShapeFiller(shapes)

    # inside is inside
    assert(sf.is_inside((2, 2)))
    
    # perimeter is outside
    assert(not sf.is_inside((2, 1)))
    assert(not sf.is_inside((3, 2)))
    assert(not sf.is_inside((2, 4)))
    assert(not sf.is_inside((1, 2)))
    
    # outside stuff is outside
    assert(not sf.is_inside((0, 0)))
    assert(not sf.is_inside((0, 4)))
    assert(not sf.is_inside((4, 4)))
    assert(not sf.is_inside((4, 0)))

def test_split_edges_square():

    shape = [(1, 1), (1, 3), (3, 3), (3, 1)]
    shapes = [shape]
    sf = ShapeFiller(shapes)

    assert(sf.split_edge_endpoints((0,1), (4,1)) == [(1,1), (3,1), (4,1)])
    assert(sf.split_edge_endpoints((0,2), (4,2)) == [(1,2), (3,2), (4,2)])
    assert(sf.split_edge_endpoints((0,3), (4,3)) == [(1,3), (3,3), (4,3)])

    assert(sf.split_edge_endpoints((0,0), (4,0)) == [(4,0)])
    assert(sf.split_edge_endpoints((0,4), (4,4)) == [(4,4)])

def test_split_edges_diamond():

    shape = [(8, 4), (12, 12), (8, 20), (4, 12)]
    shapes = [shape]
    sf = ShapeFiller(shapes)

    assert(sf.split_edge_endpoints((0,0),  (16,0))  == [(16,0)])
    assert(sf.split_edge_endpoints((0,4),  (16,4))  == [(8,4),  (16,4)])
    assert(sf.split_edge_endpoints((0,6),  (16,6))  == [(7,6),  (9,6),   (16,6)])
    assert(sf.split_edge_endpoints((0,8),  (16,8))  == [(6,8),  (10,8),  (16,8)])
    assert(sf.split_edge_endpoints((0,12), (16,12)) == [(4,12), (12,12), (16,12)])
    assert(sf.split_edge_endpoints((0,16), (16,16)) == [(6,16), (10,16), (16,16)])
    assert(sf.split_edge_endpoints((0,18), (16,18)) == [(7,18), (9,18),  (16,18)])
    assert(sf.split_edge_endpoints((0,20), (16,20)) == [(8,20), (16,20)])
    assert(sf.split_edge_endpoints((0,24), (16,24)) == [(16,24)])

def test_sort_polylines_zigzag():

    # Expect same order
    line1 = [(0, 0), (10, 0)]
    line2 = [(10, 1), (0, 1)]
    line3 = [(0, 2), (10, 2)]
    sorted = StandardDrawing.sort_polylines([line1, line2, line3])
    assert(sorted[0] == line1)
    assert(sorted[1] == line2)
    assert(sorted[2] == line3)

def test_sort_polylines_order():

    # Expect reordering as well as line3 reversed
    line1 = [(0, 0), (10, 0)]
    line2 = [(0, 2), (10, 2)]
    line3 = [(0, 1), (10, 1)]
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



