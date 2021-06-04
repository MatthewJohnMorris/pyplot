import math

from pyplot import Point, ShapeFiller

def star_gen(drawing):

    centre = Point(102.5, 148)
    size = 80
    inner = 0 # 15
    points = [(size, 0), (size, 0.5), (size, 1), (size, 1.5)]
    n = 5
    ratio = 0.7
    for i in range(0, n):
        size = (size - inner) * ratio + inner
        ix = 0
        while(ix < len(points)):
            a = points[ix]
            b = points[ix+1] if ix+1 < len(points) else (points[0], 2)
            new_angle = (a[1] + b[1]) / 2
            new_elem = (size, new_angle)
            points.insert(ix+1, new_elem)
            ix += 2
    print(points)
    shape = []
    sizes = []
    for point in points:
        r = point[0]
        if r not in sizes:
            sizes.append(r)
        radians = math.pi * point[1]
        c = math.cos(radians)
        s = math.sin(radians)
        shape.append(Point(centre.x + r*c, centre.y + r*s))
    shapes = [shape]
    sizes = sorted(sizes)[::-1]
    shapes.extend([drawing.make_circle(centre, size) for size in sizes[4:]])
    # shapes.extend([drawing.make_circle(centre, size) for size in sizes[0:3]])
    # shapes.extend([drawing.make_circle(centre, size-1) for size in sizes[0:3]])
    # shapes.extend([drawing.make_circle(centre, size) for size in sizes])
    # shapes.extend([drawing.make_circle(centre, size-1) for size in sizes])
    
    r_inner = sizes[-1] - 1
    while r_inner > 0:
        shapes.append(drawing.make_circle(centre, r_inner))
        r_inner -= 1.1
    
    sf = ShapeFiller(shapes)
    paths = sf.get_paths(drawing.pen_type.pen_width * 0.4) # , angle=math.pi/2)
    
    drawing.add_polylines(paths)
    # drawing.add_polylines([drawing.make_circle(centre, size) for size in sizes[0:3]])

    for point in points:
        r = point[0]
        radians = math.pi * point[1]
        c = math.cos(radians)
        s = math.sin(radians)
        dot_r = r / 20
        centre_r = r + dot_r + 2
        circle_centre = Point(centre.x + centre_r*c, centre.y + centre_r*s)
        if r > 25:
            drawing.add_dot(circle_centre, dot_r)
            r2 = dot_r # points[0][0] / 20 * ratio * ratio * ratio
            if r < points[0][0]:
                centre2_r = points[0][0] + r2 + 2
                circle_centre2 = Point(centre.x + centre2_r*c, centre.y + centre2_r*s)
                drawing.add_dot(circle_centre2, r2)
            if r < points[0][0] * ratio:
                centre2_r = points[0][0] * ratio + r2 + 2
                circle_centre2 = Point(centre.x + centre2_r*c, centre.y + centre2_r*s)
                drawing.add_dot(circle_centre2, r2)
            if r < points[0][0] * ratio * ratio:
                centre2_r = points[0][0] * ratio * ratio + r2 + 2
                circle_centre2 = Point(centre.x + centre2_r*c, centre.y + centre2_r*s)
                drawing.add_dot(circle_centre2, r2)
    
