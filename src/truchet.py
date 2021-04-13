from random import random, seed
import math

from pyplot import Point, ShapeFiller

def createtiles_truchet(drawing, tile_size, nlines=None):  

    circumference = tile_size * math.pi * 2
    sections = circumference / drawing.pen_type.pen_width
    n = int(sections / 4)

    nlines = 5 if nlines is None else nlines

    tile_paths0 = []
    for i in range(0, nlines+1):
        path = [Point(tile_size * i / nlines, 0), Point(tile_size * i / nlines, tile_size)]
        tile_paths0.append(path)

    tiles_roundonly = createtiles_truchet_roundonly(drawing, tile_size, nlines)
    return [tile_paths0, tiles_roundonly[0]]

def createtiles_truchet_roundonly(drawing, tile_size, nlines=None):  

    circumference = tile_size * math.pi * 2
    sections = circumference / drawing.pen_type.pen_width
    n = int(sections / 4)
    
    nlines = 3 if nlines is None else nlines
        
    paths = [[] for i in range(0, nlines)]
    for i in range(0, n+1):
        a = math.pi * i / (2*n)
        for j in range(0, nlines):
            paths[j].append(Point(math.cos(a), math.sin(a)) * tile_size * (j+1)/nlines)
            
    clip_path = [x for x in paths[nlines-1]]
    clip_path.append(Point(0,0))
    sf = ShapeFiller([clip_path])

    paths2 = [[] for i in range(0, nlines)]
    for i in range(0, n+1):
        a = math.pi * i / (2*n)
        for j in range(0, nlines):
            paths2[j].append(Point(tile_size, tile_size) - Point(math.cos(a), math.sin(a)) * tile_size * (j+1)/nlines)
    paths2 = sf.clip(paths2)
    tile_paths1 = paths
    tile_paths1.extend(paths2)

    return [tile_paths1]
    
def createtiles_slash(frawing, tile_size):

    path = []
    path.append(Point(0,0))
    path.append(Point(tile_size, tile_size))
    return [[path]]
  
def createtiles_tri(drawing, tile_size):

    delta = drawing.pen_type.pen_width * 0.75
    diag = math.sqrt(2)
    shape = [Point(delta,delta), Point(delta,tile_size-delta), Point(tile_size-delta,delta)]
    sf = ShapeFiller([shape])
    tile = sf.get_paths(row_width = drawing.pen_type.pen_width * 0.4)
    
    return [tile]

def createtiles_semi(drawing, tile_size):  

    circumference = tile_size * math.pi * 2
    sections = circumference / drawing.pen_type.pen_width
    n = int(sections / 4)
        
    path0 = []
    path1 = []
    for i in range(0, n+1):
        a = math.pi * i / (2*n)
        path0.append(Point(math.cos(a), math.sin(a)) * tile_size / 2)
        path1.append(Point(tile_size, tile_size) - Point(math.cos(a), math.sin(a)) * tile_size / 2)
            
    return [[path0, path1]]

def createtiles_semi_track(drawing, tile_size):  

    circumference = tile_size * math.pi * 2
    sections = circumference / drawing.pen_type.pen_width
    n = int(sections / 4)
    track_size = tile_size / 4
        
    path00 = []
    path01 = []
    path10 = []
    path11 = []
    for i in range(0, n+1):
        a = math.pi * i / (2*n)
        path00.append(Point(math.cos(a), math.sin(a)) * (tile_size / 2 - track_size / 2))
        path01.append(Point(math.cos(a), math.sin(a)) * (tile_size / 2 + track_size / 2))
        path10.append(Point(tile_size, tile_size) - Point(math.cos(a), math.sin(a)) * (tile_size / 2 - track_size / 2))
        path11.append(Point(tile_size, tile_size) - Point(math.cos(a), math.sin(a)) * (tile_size / 2 + track_size / 2))
            
    return [[path00, path01, path10, path11]]  

def draw_truchet_for_tiles(drawing, tile_paths_func, container=None, stroke=None):

    paper_centre = Point(102.5, 148)
    paper_size = Point(192, 276) - Point(10, 10)
    tile_c = 20
    tile_size = paper_size.x / tile_c
    tile_r = int(paper_size.y / tile_size)
    tile_topleft_00 = paper_centre - Point(tile_c, tile_r) * (tile_size/2)
    polylines = []

    all_tile_paths = tile_paths_func(drawing, tile_size)
    
    for r in range(0, tile_r):
        for c in range(0, tile_c):
            tile_topleft = tile_topleft_00 + Point(c, r) * tile_size
            
            ix_random = int(random() * len(all_tile_paths))
            
            t = all_tile_paths[ix_random]
            
            r_rot = int(random()*4)
            c = 1
            s = 0
            if r_rot == 1:
                c = 0
                s = 1
            elif r_rot == 2:
                c = -1
                s = 0
            elif r_rot == 3:
                c = 0
                s = -1
            t1 = [[p - Point(tile_size, tile_size) / 2 for p in path] for path in t]
            t2 = [[Point(p.x * c + p.y * s, p.y * c - p.x * s) for p in path] for path in t1]
            t3 = [[p + Point(tile_size, tile_size) / 2 for p in path] for path in t2]
            tile_paths = [[tile_topleft + x for x in path] for path in t3]
                        
            polylines.extend(tile_paths)
            # drawing.add_square(tile_topleft, tile_size)
         
    print(f"draw_truchet: adding {len(polylines)} polylines")         
    drawing.add_polylines(polylines, prejoin=True, container=container, stroke=stroke)