import math
import random

import svgwrite

from pyplot import Point, ShapeFiller, StandardDrawing

def draw_shape_clips(d):

    all_polylines = []
    shapes = []
    for i in range(0, 40):
        x = 20 + random.random() * 25
        y = 20 + random.random() * 25
        size = 2.5 + 30 * random.random()
        shape = d.make_square(Point(x, y), size)
        a = random.random()*math.pi*2
        shape = [StandardDrawing.rotate_about(pt, (x+size/2, y+size/2), a) for pt in shape]
        shape_polyline = [x for x in shape]
        shape_polyline.append(shape_polyline[0])
        # print(shape_polyline)
        if i == 0:
            all_polylines.append(shape_polyline)
        else:
            # print(f"shapes={shapes}")
            sf = ShapeFiller(shapes)
            clipped_polylines = sf.clip([shape_polyline], union=True)
            #print(polyline)
            #print(polylines)
            all_polylines.extend(clipped_polylines)
        #print(all_polylines[-1])
        shapes.append(shape)
    d.add_polylines(all_polylines)

def draw_shape_clips2(d):

    paper_centre = Point(102.5, 148)
    paper_size = Point(192, 276)
    all_polylines = []
    shapes = []
    size = 10
    for i in range(0, 1000):
        cx = paper_centre.x + (random.random()-0.5) * (paper_size.x - size - 20)
        cy = paper_centre.y + (random.random()-0.5) * (paper_size.y - size - 20)
        shape = d.make_square(Point(cx-size/2, cy-size/2), size)
        a = random.random()*math.pi*2
        shape = [StandardDrawing.rotate_about(pt, (cx, cy), a) for pt in shape]
        shape_polyline = [x for x in shape]
        shape_polyline.append(shape_polyline[0])
        if len(shapes) == 0:
            all_polylines.append(shape_polyline)
            shapes.append(shape)
        else:
            sf = ShapeFiller(shapes)
            clipped_polylines = sf.clip([shape_polyline], union=True)
            if(len(clipped_polylines) > 0):
                # print(shape_polyline)
                # print(clipped_polylines)
                all_polylines.extend(clipped_polylines)
                shapes.append(shape)
    d.add_polylines(all_polylines)

def draw_shape_clips3(d):

    # Try developing a shade fill class that we can put in here
    # Can use for more general area fill art
    
    paper_centre = Point(102.5, 148)
    paper_size = Point(192, 276)
    all_shape_polylines = []
    all_fill_polyline_lists = []
    shapes = []
    max_size = 30
    for i in range(0, 50):
        cx = paper_centre.x + (random.random()-0.5) * (paper_size.x - (max_size + 20))
        cy = paper_centre.y + (random.random()-0.5) * (paper_size.y - (max_size + 20))
        
        r = random.random()
        size = max_size * (0.5 + 0.5 * r)
        r = random.random()
        if r < 0.333:
            tl = Point(cx-size/2, cy-size/2)
            line = [Point(1,0), Point(2,0), Point(2,1), Point(3,1), Point(3,2), Point(2,2), Point(2,3), Point(1,3), Point(1,2), Point(0,2), Point(0,1), Point(1,1)]
            shape = [tl + pt*(size/3) for pt in line]
        elif r < 0.666:
            shape = d.make_square(Point(cx-size/2, cy-size/2), size)
        else:
            tl = Point(cx-size/2, cy-size/2)
            line = [Point(0,0), Point(3,0), Point(1.5,3*math.sqrt(3)/2)]
            shape = [tl + pt*(size/3) for pt in line]
            
        fill_lines = []
        r = random.random()
        if r < 10.5:
            sf = ShapeFiller([shape])
            w = d.pen_type.pen_width * 0.8
            y = cy-size/2 + w
            fill_lines = []
            while y < cy+size/2:
                fill_lines.append([Point(cx-size/2, y), Point(cx+size/2, y)])
                y += w
            fill_lines = sf.clip(fill_lines, inverse=True)
        
        a = random.random()*math.pi*2
        fill_lines = [[StandardDrawing.rotate_about(pt, (cx, cy), a) for pt in line] for line in fill_lines]
        shape = [StandardDrawing.rotate_about(pt, (cx, cy), a) for pt in shape]
        shape_polyline = [x for x in shape]
        shape_polyline.append(shape_polyline[0])
        if len(shapes) == 0:
            all_shape_polylines.extend([shape_polyline])
            shapes.append(shape)
            clipped_fill_polylines = [[fill_line] for fill_line in fill_lines]
        else:
            sf = ShapeFiller(shapes)
            clipped_shape_polylines = sf.clip([shape_polyline], union=True)
            all_shape_polylines.extend(clipped_shape_polylines)
            
            # A list of polylines (= list of points)
            clipped_fill_polylines = [sf.clip([fill_line], union=True) for fill_line in fill_lines]
            shapes.append(shape)

        ix = 0
        for clipped_fill_polyline in clipped_fill_polylines:
            if(len(clipped_fill_polyline) > 0):
                all_fill_polyline_lists.append(clipped_fill_polyline)
            ix += 1
                
                
    d.add_polylines(all_shape_polylines)
    sub_lists = [[], [], [], []]
    mins = paper_centre - paper_size / 2
    maxs = paper_centre + paper_size / 2
    for polyline_list in all_fill_polyline_lists:
        pts = [pt for polyline in polyline_list for pt in polyline]
        avg = Point(sum(pt.x for pt in pts), sum(pt.y for pt in pts)) / len(pts)
        cx = min(1, max(0, (avg.x - mins.x)/(maxs.x - mins.x)))
        cy = min(1, max(0, (avg.y - mins.x)/(maxs.y - mins.y)))
        r0 = cx
        r1 = 1-cx
        r2 = cy
        r3 = 1-cy
        rtot = r0 + r1 + r2 + r3 #  + 2
        r = random.random()
        if r < r0/rtot:
            sub_lists[0].extend(polyline_list)
        elif r < (r0+r1)/rtot:
            sub_lists[1].extend(polyline_list)
        elif r < (r0+r1+r2)/rtot:
            sub_lists[2].extend(polyline_list)
        elif r < (r0+r1+r2+r3)/rtot:
            sub_lists[3].extend(polyline_list)
            
    #d.add_polylines(sub_lists[0], container=d.add_layer("1-xxx"), stroke=svgwrite.rgb(100, 100, 50, '%'))
    #d.add_polylines(sub_lists[1], container=d.add_layer("2-xxx"), stroke=svgwrite.rgb(100, 50, 100, '%'))
    #d.add_polylines(sub_lists[2], container=d.add_layer("3-xxx"), stroke=svgwrite.rgb(100, 0, 0, '%'))
    #d.add_polylines(sub_lists[3], container=d.add_layer("4-xxx"), stroke=svgwrite.rgb(50, 50, 100, '%'))
    d.add_polylines(sub_lists[0], container=d.add_layer("1-xxx"), stroke=svgwrite.rgb(50, 50, 100, '%'))
    d.add_polylines(sub_lists[1], container=d.add_layer("2-xxx"), stroke=svgwrite.rgb(50, 100, 50, '%'))
    d.add_polylines(sub_lists[2], container=d.add_layer("3-xxx"), stroke=svgwrite.rgb(50, 100, 100, '%'))
    d.add_polylines(sub_lists[3], container=d.add_layer("4-xxx"), stroke=svgwrite.rgb(0, 50, 50, '%'))

