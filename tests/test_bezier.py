import pytest

from pyplot.bezier import *

def test_split_at_t_0():

    bez = ((0,0), (0,0), (2,2), (2,2))
    
    bez0 = bezier_split_at_t(bez, 0)
    assert(bez0[0][0] == (0,0))
    assert(bez0[0][1] == (0,0))
    assert(bez0[0][2] == (0,0))
    assert(bez0[0][3] == (0,0))
    assert(bez0[1][0] == (0,0))
    assert(bez0[1][1] == (0,0))
    assert(bez0[1][2] == (2,2))
    assert(bez0[1][3] == (2,2))
    
def test_split_at_t_1():

    bez = ((0,0), (0,0), (2,2), (2,2))
    
    bez1 = bezier_split_at_t(bez, 1)
    assert(bez1[0][0] == (0,0))
    assert(bez1[0][1] == (0,0))
    assert(bez1[0][2] == (2,2))
    assert(bez1[0][3] == (2,2))
    assert(bez1[1][0] == (2,2))
    assert(bez1[1][1] == (2,2))
    assert(bez1[1][2] == (2,2))
    assert(bez1[1][3] == (2,2))

def test_split_at_t_mid():

    bez = ((0,0), (0,0), (2,2), (2,2))
    
    bez_mid = bezier_split_at_t(bez, 0.5)
    assert(bez_mid[0][0] == (0,0))
    assert(bez_mid[0][1] == (0,0))
    assert(bez_mid[0][2] == (0.5,0.5))
    assert(bez_mid[0][3] == (1,1))
    assert(bez_mid[1][0] == (1,1))
    assert(bez_mid[1][1] == (1.5,1.5))
    assert(bez_mid[1][2] == (2,2))
    assert(bez_mid[1][3] == (2,2))
