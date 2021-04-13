import pytest

from apollonius import *

def test_simple():

    c1, c2, c3 = Circle(0, 0, 1), Circle(4, 0, 1), Circle(2, 4, 2)
    
    cA = apollonius_solve(c1, c2, c3, 1, 1, 1)
    
    assert cA.x == 2.0
    assert cA.y == 2.1
    assert cA.r == 3.9
    
    cB = apollonius_solve(c1, c2, c3, -1, -1, -1)
    
    assert cB.x == pytest.approx(2.0)
    assert cB.y == pytest.approx(0.8333333333)
    assert cB.r == pytest.approx(1.1666666667)

