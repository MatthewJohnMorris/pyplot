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
