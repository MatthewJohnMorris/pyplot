import math
import pytest

from pyplot.pyplot import CircleBlock, PenType, StandardDrawing, ShapeFiller

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
    
