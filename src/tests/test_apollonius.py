import pytest

from apollonius import ApollonianGasket

def test_simple():

    r = 0.05
    g = ApollonianGasket(r, r, r, (100, 100), 80)
    g.generate(4)
    
    (dx, dy) = (20 + 1/r, 20 + 1/r)
    
    for c in g.genCircles:
        print(c.m.real+dx, c.m.imag+dy, abs(c.r.real))
