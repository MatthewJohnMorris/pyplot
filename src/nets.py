import math
import random

from pyplot import Point

def warp_inward(point, centre, edge):

    diff = point - centre
    dist = diff.dist()
    if dist >= edge:
        return point
    r = dist/edge
    mult = 1 + 0.3 * math.exp(1-r) - 0.3* math.exp(0)
    return centre + diff / (mult*mult)

def warp_outward(point, centre, edge):

    diff = point - centre
    dist = diff.dist()
    if dist >= edge:
        return point
    r = dist/edge
    mult = 1 + 0.3 * math.exp(1-r) - 0.3* math.exp(0)
    return centre + diff * (mult*mult)

def draw_net(d):

    paper_centre = Point(102.5, 148)
    paper_size = Point(192, 250)
    polylines = []
    
    n = 75
    size = 2
    points = [[Point(0,0) for _ in range(0, n+1)] for _ in range(0, n+1)]
    for i in range(0, n+1):
        for j in range(0, n+1):
            points[i][j] = paper_centre + Point(i-n/2,j-n/2)* size

    for i in range(0, n+1):
        for j in range(0, n+1):
            a = random.random() * 2 * math.pi
            points[i][j] = points[i][j] + Point(math.cos(a), math.sin(a)) * size * 0.1 * 0
            
    for i in range(0, n+1):
        for j in range(0, n+1):
            points[i][j] = warp_inward(points[i][j], paper_centre, n/2*size/3)
            points[i][j] = warp_inward(points[i][j], paper_centre + Point(+1,+1) * n*size/4, n/2*size/3)
            points[i][j] = warp_inward(points[i][j], paper_centre + Point(-1,-1) * n*size/4, n/2*size/3)
            points[i][j] = warp_inward(points[i][j], paper_centre + Point(+1,-1) * n*size/4, n/2*size/3)
            points[i][j] = warp_inward(points[i][j], paper_centre + Point(-1,+1) * n*size/4, n/2*size/3)
            points[i][j] = warp_outward(points[i][j], paper_centre, n/2*size)
            points[i][j] = warp_outward(points[i][j], paper_centre, n/2*size/3)
            
    for i in range(0, n+1):
        polyline = []
        for j in range(0, n+1):
            polyline.append(points[i][j])
        polylines.append(polyline)
    for j in range(0, n+1):
        polyline = []
        for i in range(0, n+1):
            polyline.append(points[i][j])
        polylines.append(polyline)
            
            
    d.add_polylines(polylines)
