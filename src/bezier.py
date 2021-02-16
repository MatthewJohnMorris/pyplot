import math

def interp_t(p1, p2, t):
    """Linearly interpolate between p1 and p2."""

    x1, y1 = p1
    x2, y2 = p2
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

def bezier_split_at_t(bez, t):
    """Split bezier at given time"""

    ((bx0, by0), (bx1, by1), (bx2, by2), (bx3, by3)) = bez
    m1 = interp_t((bx0, by0), (bx1, by1), t)
    m2 = interp_t((bx1, by1), (bx2, by2), t)
    m3 = interp_t((bx2, by2), (bx3, by3), t)
    m4 = interp_t(m1, m2, t)
    m5 = interp_t(m2, m3, t)
    m = interp_t(m4, m5, t)

    return ((bx0, by0), m1, m4, m), (m, m5, m3, (bx3, by3))
    
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

def bezier_subdivide( start, spline_array, flat ):
    """
    Break up a bezier curve into smaller curves, each of which
    is approximately a straight line within a given tolerance
    (the "smoothness" defined by [flat]).
    """

    # When we start splitting splines, the start spline of the split doesn't have its control points affected, just
    # its endpoints. So we we want to add in an initial spline that is already small enough to not require further
    # division, and which is also already pointing in the right direction.
    initial = spline_array[0]
    copy = [initial[0], initial[1], initial[2]]
    while True:
        b = ( start, copy[0], copy[1], copy[2] )
        # print(f'max_dist of "{b}" is {bezier_max_dist( b )} vs {flat}')
        if bezier_max_dist(b) <= flat:
            break
        one, two = bezier_split_at_t(b, 0.5)
        copy[0] = one[1]
        copy[1] = one[2]
        copy[2] = one[3]
    spline_array.insert(0, copy)

    i = 1
    while True:
        while True:
            if i >= len( spline_array ):
                # print(f"final array length={len(spline_array)}")
                return spline_array

            p0 = spline_array[i - 1][1]
            p1 = spline_array[i - 1][2]
            p2 = spline_array[i][0]
            p3 = spline_array[i][1]
            b = ( p0, p1, p2, p3 )

            if bezier_max_dist( b ) > flat:
                break
            i += 1

        # each: [0] = start, [1] = contol_at_start, [2] = control_at_end, [3] = end
        one, two = bezier_split_at_t( b, 0.5 )
        # a[i-1][1] = one[0] = p0 (unchanged)
        # a[i-1][2] = one[1]
        #      p[0] = one[2]
        #      p[1] = one[3]
        #      p[2] = two[1]
        # a[ i ][0] = two[2]
        # a[ i ][1] = two[3] = p3 (unchanged)
        spline_array[i-1][2] = one[1]
        spline_array[i][0] = two[2]
        spline_array[i:1] = [[one[2], one[3], two[1]]]

