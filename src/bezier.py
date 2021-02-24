import math
    
def bezier_max_dist(bez):
    """See how far control points are from line"""

    (x0, y0) = bez[0]
    (x1, y1) = bez[1]
    (x2, y2) = bez[2]
    (x3, y3) = bez[3]
    (x03, y03) = (x3 - x0, y3 - y0)
    d03 = math.sqrt(x03*x03 + y03*y03)
    if d03 == 0:
        return 0
    d1 = abs(x03*(y0 - y1) - y03*(x0 - x1)) / d03
    d2 = abs(x03*(y0 - y2) - y03*(x0 - x2)) / d03
    return max(d1, d2)

def bezier_split_at_t2( b, t ):

    u = 1-t
    tt = t*t
    tu = t*u
    uu = u*u
    ttt = t * tt
    ttu = t * tu
    tuu = tu * u
    uuu = uu * u
    a0 = b[0]
    a1 = (t*b[1][0] + u*b[0][0], t*b[1][1] + u*b[0][1])
    a2 = (tt*b[2][0] + 2*tu*b[1][0] + uu*b[0][0], tt*b[2][1] + 2*tu*b[1][1] + uu*b[0][1])
    a3 = (ttt*b[3][0] + 3*ttu*b[2][0] + 3*tuu*b[1][0] + uuu*b[0][0], ttt*b[3][1] + 3*ttu*b[2][1] + 3*tuu*b[1][1] + uuu*b[0][1])
    b0 = a3
    b1 = (tt*b[3][0] + 2*tu*b[2][0] + uu*b[1][0], tt*b[3][1] + 2*tu*b[2][1] + uu*b[1][1])
    b2 = (t*b[3][0] + u*b[2][0], t*b[3][1] + u*b[2][1])
    b3 = b[3]
    return [a0,a1,a2,a3],[b0,b1,b2,b3]

def bezier_subdivide2( start, spline_array, flat ):
    """
    Break up a bezier curve into smaller curves, each of which
    is approximately a straight line within a given tolerance
    (the "smoothness" defined by [flat]).
    """

    i = 0
    while True:
        while True:
            if i >= len( spline_array ):
                # print(f"final array length={len(spline_array)}")
                return spline_array

            p0 = start if i == 0 else spline_array[i - 1][2]
            p1 = spline_array[i][0]
            p2 = spline_array[i][1]
            p3 = spline_array[i][2]
            b = ( p0, p1, p2, p3 )

            if bezier_max_dist( b ) > flat:
                break
            i += 1

        # each: [0] = start, [1] = contol_at_start, [2] = control_at_end, [3] = end
        one, two = bezier_split_at_t2( b, 0.5 )
        # a[i][0] = one[1] = p0 (unchanged)
        # a[i][1] = one[2]
        # a[i][2] = one[3]
        #    p[0] = two[0]
        #    p[1] = two[1]
        #    p[2] = two[2]
        spline_array[i][0] = one[1]
        spline_array[i][1] = one[2]
        spline_array[i][2] = one[3]
        spline_array[i+1:i+1] = [[two[1], two[3], two[3]]]
