def interp_t(p1, p2, t):
    """Linearly interpolate between p1 and p2.

    t = 0.0 returns p1, t = 1.0 returns p2.

    :return: Interpolated point
    :rtype: tuple

    :param p1: First point as sequence of two floats
    :param p2: Second point as sequence of two floats
    :param t: Number between 0.0 and 1.0
    :type t: float
    """
    x1, y1 = p1
    x2, y2 = p2
    return x1 + t * (x2 - x1), y1 + t * (y2 - y1)

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