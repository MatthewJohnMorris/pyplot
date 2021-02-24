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

def bezier_split_at_t( p, t ):
    """
    See https://pomax.github.io/bezierinfo/#matrixsplit
    This reproduces the matrix multiplication set out there for cubics
    """

    u = 1-t
    tt = t*t
    tu = t*u
    uu = u*u
    ttt = t * tt
    ttu = t * tu
    tuu = tu * u
    uuu = uu * u
    
    p0 = p[0]
    p1 = p[1]
    p2 = p[2]
    p3 = p[3]
    
    a0 = p0
  # a0 = (                                p0[0],                                                         p0[1])
    a1 = (                t*p1[0] +     u*p0[0],                                           t*p1[1] +   u*p0[1])
    a2 = ( tt*p2[0] +  2*tu*p1[0] +    uu*p0[0],                            tt*p2[1] +  2*tu*p1[1] +  uu*p0[1])
    a3 = (ttt*p3[0] + 3*ttu*p2[0] + 3*tuu*p1[0] + uuu*p0[0], ttt*p3[1] + 3*ttu*p2[1] + 3*tuu*p1[1] + uuu*p0[1])
    b0 = a3
  # b0 = (ttt*p3[0] + 3*ttu*p2[0] + 3*tuu*p1[0] + uuu*p0[0], ttt*p3[1] + 3*ttu*p2[1] + 3*tuu*p1[1] + uuu*p0[1])
    b1 = ( tt*p3[0] +  2*tu*p2[0] +    uu*p1[0],              tt*p3[1] + 2*tu*p2[1] + uu*p1[1]                )
    b2 = (  t*p3[0] +     u*p2[0],                             t*p3[1] +    u*p2[1]                           )
  # b3 = (    p3[0],                                             p3[1]                                        )
    b3 = p3
    
    return [a0,a1,a2,a3],[b0,b1,b2,b3]

def bezier_subdivide( start, spline_array, flat ):
    """
    Break up a bezier curve into smaller curves, each of which
    is approximately a straight line within a given tolerance
    (the "smoothness" defined by [flat]).
    
    Rewritten from scratch as no idea what the axidraw stuff thought it was doing - it sort of
    worked but started showing distorion on very long splines. Maybe that's me being unable tobytes
    transcribe, but seemed best to get it right from the ground up.
    """

    i = 0
    while True:
        while True:
            if i >= len( spline_array ):
                # print(f"final array length={len(spline_array)}")
                return spline_array

            # The end of each element (elem[2]) is the start of the next. Use "start" as starting point when on the first spline.
            p0 = start if i == 0 else spline_array[i - 1][2]
            p1 = spline_array[i][0]
            p2 = spline_array[i][1]
            p3 = spline_array[i][2]
            b = ( p0, p1, p2, p3 )

            if bezier_max_dist( b ) > flat:
                break
            i += 1

        # b: [0] = start, [1] = contol_at_start, [2] = control_at_end, [3] = end
        one, two = bezier_split_at_t( b, 0.5 )
        spline_array[i] = [one[1], one[2], one[3]]
        spline_array[i+1:i+1] = [[two[1], two[3], two[3]]]
