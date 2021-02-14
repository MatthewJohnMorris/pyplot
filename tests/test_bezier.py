import pytest

from pyplot.bezier import *

def test_split_at_t():

    bez = ((0,0), (0,0), (1,1), (1,1))
    
    bez0 = bezier_split_at_t(bez, 0)
    print(bez0)
