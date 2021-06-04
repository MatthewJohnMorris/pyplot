import csv
import math
import numpy.matlib 
import numpy as np 
import time

from pyplot import Point, ShapeFiller, StandardDrawing

class Transform3D:

    def __init__(self, cameraToWorld, canvasWidth, canvasHeight, imageWidth, imageHeight):
        self.cameraToWorld = cameraToWorld
        # First transform the 3D point from world space to camera space. 
        self.worldToCamera = np.linalg.inv(cameraToWorld)
        self.canvasWidth = canvasWidth
        self.canvasHeight = canvasHeight
        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        
    def project(self, pWorld):
        # Allow lists (of lists of...) points
        if type(pWorld) == list:
            return [self.project(x) for x in pWorld]
            
        pCamera = numpy.matmul(pWorld, self.worldToCamera)
        # Coordinates of the point on the canvas. Use perspective projection.
        screen_x = pCamera[0] / -pCamera[2]
        screen_y = pCamera[1] / -pCamera[2]
        # If the x- or y-coordinate absolute value is greater than the canvas width 
        # or height respectively, the point is not visible
        if (abs(screen_x) > self.canvasWidth or abs(screen_y) > self.canvasHeight):
            return None 
        # Normalize. Coordinates will be in the range [0,1]
        ndc_x = (screen_x + self.canvasWidth / 2) / self.canvasWidth 
        ndc_y = (screen_y + self.canvasHeight / 2) / self.canvasHeight 
        # Finally convert to pixel coordinates. Don't forget to invert the y coordinate
        raster_x = (ndc_x * self.imageWidth) 
        raster_y = ((1 - ndc_y) * self.imageHeight)
        camera_z = -pCamera[2]

        return (raster_x, raster_y, camera_z)
    
    @staticmethod
    def convertToPolylines(all_faces):
    
        # Backface culling
        faces_forward = [face for face in all_faces if Transform3D.isForward(face)]

        # Distance averaging and sorting
        sorted_faces = Transform3D.sortByDistance(faces_forward)
        print(f"Found {len(sorted_faces)} faces")
        
        # Clipping
        return Transform3D.clip(sorted_faces)
    
    @staticmethod
    def clip(sorted_faces):
        
        tStart = time.perf_counter()
    
        all_shapes = []
        all_polylines = []
        
        for face in sorted_faces:
            # First face
            if len(all_shapes) == 0:
                all_polylines.append(face)
                shape = face[0:-1]
                all_shapes.append(shape)
                sf = ShapeFiller([shape])
                continue
                
            # 4% just from this!
            print(f".", end='', flush=True)
            
            # Only 50% of the time spent here?
            clipped = sf.clip([face], union=True)

            # Only do anything if the shape has something to display
            if len(clipped) == 0:
                continue
            all_polylines.extend(clipped)
            shape = face[0:-1]
            all_shapes.append(shape)
            sf.add_shape(shape)
                    
        tEnd = time.perf_counter()
        print(f"clip-tot={tEnd - tStart:.2f}s")
        print(f"len(all_polylines)={len(all_polylines)}")
        print(f"len(shapes)={len(all_shapes)}")
                    
        return all_polylines
    
    @staticmethod
    def sortByDistance(faces):
        faces_with_z = []
        for face in faces:
            avg_z = sum(pt[2] for pt in face) / len(face)
            faces_with_z.append((face, avg_z))
        sorted_faces_with_z = sorted(faces_with_z, key=lambda x: x[1])
        return[face_with_z[0] for face_with_z in sorted_faces_with_z]
    
    @staticmethod
    def isForward(face):
        x0 = face[0][0]
        y0 = face[0][1]
        x1 = face[1][0]
        y1 = face[1][1]
        x2 = face[2][0]
        y2 = face[2][1]
        x01 = x1 - x0
        y01 = y1 - y0
        x12 = x2 - x1
        y12 = y2 - y1
        norm = x01 * y12 - x12 * y01
        return norm > 0
    
    @staticmethod
    def rotX(points, a):
        x_rot = [(1, 0, 0, 0), (0, math.cos(a), math.sin(a), 0), (0, -math.sin(a), math.cos(a), 0), (0, 0, 0, 1)]
        # Allow lists (of lists of...) points
        if type(points) == list:
            return [Transform3D.rotX(x, a) for x in points]
        return numpy.matmul(points, x_rot)
        
    @staticmethod
    def rotY(points, a):
        y_rot = [(math.cos(a), 0, math.sin(a), 0), (0, 1, 0, 0), (-math.sin(a), 0, math.cos(a), 0), (0, 0, 0, 1)]
        # Allow lists (of lists of...) points
        if type(points) == list:
            return [Transform3D.rotY(x, a) for x in points]
        return numpy.matmul(points, y_rot)
        
    @staticmethod
    def rotZ(points, a):
        z_rot = [(math.cos(a), math.sin(a), 0, 0), (-math.sin(a), math.cos(a), 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
        # Allow lists (of lists of...) points
        if type(points) == list:
            return [Transform3D.rotZ(x, a) for x in points]
        return numpy.matmul(points, z_rot)

def computePixelCoordinates( 
    pWorld, 
    cameraToWorld, 
    canvasWidth, 
    canvasHeight, 
    imageWidth, 
    imageHeight):
    
    # First transform the 3D point from world space to camera space. 
    # It is of course inefficient to compute the inverse of the cameraToWorld
    # matrix in this function. It should be done outside the function, only once
    # and the worldToCamera should be passed to the function instead. 
    # We are only compute the inverse of this matrix in this function ...
    worldToCamera = np.linalg.inv(cameraToWorld)
    print(worldToCamera)
    # print(cameraToWorld)
    #print(worldToCamera)
    #print(pWorld)
    pCamera = numpy.matmul(worldToCamera, pWorld)
    pCamera = numpy.matmul(pWorld, worldToCamera)
    print(f"{pWorld} -> {pCamera}")
    #print(pCamera)
    # Coordinates of the point on the canvas. Use perspective projection.
    screen_x = pCamera[0] / -pCamera[2]
    screen_y = pCamera[1] / -pCamera[2]
    # If the x- or y-coordinate absolute value is greater than the canvas width 
    # or height respectively, the point is not visible
    print(f"screen: {screen_x}, {screen_x}")
    if (abs(screen_x) > canvasWidth or abs(screen_y) > canvasHeight):
        return None 
    # Normalize. Coordinates will be in the range [0,1]
    ndc_x = (screen_x + canvasWidth / 2) / canvasWidth 
    ndc_y = (screen_y + canvasHeight / 2) / canvasHeight 
    print(f"ndc: {ndc_x}, {ndc_y}")
    # Finally convert to pixel coordinates. Don't forget to invert the y coordinate
    raster_x = (ndc_x * imageWidth) 
    raster_y = ((1 - ndc_y) * imageHeight)

    return (raster_x, raster_y)
 
 
def cube_faces(proj_points):

    polylines = []
    polylines.append([proj_points[0], proj_points[1], proj_points[2], proj_points[3], proj_points[0]])
    polylines.append([proj_points[1], proj_points[0], proj_points[4], proj_points[5], proj_points[1]])
    polylines.append([proj_points[2], proj_points[1], proj_points[5], proj_points[6], proj_points[2]])
    polylines.append([proj_points[3], proj_points[2], proj_points[6], proj_points[7], proj_points[3]])
    polylines.append([proj_points[0], proj_points[3], proj_points[7], proj_points[4], proj_points[0]])
    polylines.append([proj_points[7], proj_points[6], proj_points[5], proj_points[4], proj_points[7]])
    return polylines

def draw_3d(d):

    cameraToWorld = numpy.identity(4)
    cameraToWorld[3][2] = 10
    t = Transform3D(cameraToWorld, canvasWidth=2, canvasHeight=2, imageWidth=100, imageHeight=100)
        
    h = 1
    s = 0.3
    base_points = [(s, s, s, h), (s, -s, s, h), (-s, -s, s, h), (-s, s, s, h), (s, s, -s, h), (s, -s, -s, h), (-s, -s, -s, h), (-s, s, -s, h)]

    a = math.pi / 11 + 1
    n = 800
    all_faces = []
    for i in range(0,n): # [110]: # range(0, n):
    
        world_points = [p for p in base_points]
        zc = (i - n/2)/14
        xc = 6
        yc = 0
        world_points = [(p[0]+xc, p[1]+yc, p[2]+zc, p[3]) for p in world_points]
        world_points = Transform3D.rotZ(world_points, a)
        world_points = Transform3D.rotX(world_points, math.pi * 0.5)
        
        proj_points = t.project(world_points)
        any_none = False
        for x in proj_points:
            if x is None:
                any_none = True
                break
        if not any_none:
            # 20, 105
            proj_points = [(x[0]+20, x[1]+70, x[2]) for x in proj_points]
            polylines = cube_faces(proj_points)

            for face in polylines:
                all_faces.append(face)
                
        a += 0.2 # math.pi / 7

    all_polylines = Transform3D.convertToPolylines(all_faces)
                
    print(f"Adding polylines")
    d.add_polylines(all_polylines)

def calc_norm(face3d):

    p0 = face3d[0]
    p1 = face3d[1]
    p2 = face3d[2]
    v01 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[3])
    v12 = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[3])
    xp = (v01[1]*v12[2]-v01[2]*v12[1], v01[2]*v12[0]-v01[0]*v12[2], v01[0]*v12[1]-v01[1]*v12[0])
    xp_size = math.sqrt(xp[0]*xp[0] + xp[1]*xp[1] + xp[2]*xp[2])
    xpn = (xp[0] / xp_size, xp[1] / xp_size, xp[2] / xp_size)
    return xpn

def cube_open_faces(proj_points):

    polylines = []
    polylines.append([proj_points[0], proj_points[1], proj_points[2], proj_points[3]])
    polylines.append([proj_points[0], proj_points[4], proj_points[5], proj_points[1]])
    polylines.append([proj_points[6], proj_points[2], proj_points[1], proj_points[5]])
    polylines.append([proj_points[6], proj_points[7], proj_points[3], proj_points[2]])
    polylines.append([proj_points[0], proj_points[3], proj_points[7], proj_points[4]])
    polylines.append([proj_points[6], proj_points[5], proj_points[4], proj_points[7]])
    return polylines

def get_face_draw_lines(t, face3d):

    proj_face_lines = []
    line_count = 10
    s0 = face3d[0]
    e0 = face3d[1]
    s1 = face3d[3]
    e1 = face3d[2]
    face_lines = []
    for j in range(0, line_count):
        p = (j+0.5) / line_count
        q = 1-p
        sp = (s0[0]*p + s1[0]*(1-p), s0[1]*p + s1[1]*(1-p), s0[2]*p + s1[2]*(1-p), 1.0)
        ep = (e0[0]*p + e1[0]*(1-p), e0[1]*p + e1[1]*(1-p), e0[2]*p + e1[2]*(1-p), 1.0)
        face_lines.append([sp, ep])
    for face_line in face_lines:
        proj_face_line = t.project(face_line)
        proj_face_lines.append(proj_face_line)
    return proj_face_lines

def scale_to_unit_square(paths):

    min_x = paths[0][0].x
    max_x = paths[0][0].x
    min_y = paths[0][0].y
    max_y = paths[0][0].y
    for text_path in paths:
        for pt in text_path:
            min_x = min(min_x, pt.x)
            max_x = max(max_x, pt.x)
            min_y = min(min_y, pt.y)
            max_y = max(max_y, pt.y)
    extent_x = max_x - min_x
    extent_y = max_y - min_y
    extent_max = max(extent_x, extent_y)
    cx = (max_x + min_x) * 0.5
    cy = (max_y + min_y) * 0.5
    scale_dist = 0.8 / extent_max
    # extent_max maps to 0.8, centred on (cx, cy)
    map_pt = lambda pt: Point(0.5 + (pt.x - cx) * scale_dist, 0.5 + (pt.y - cy) * scale_dist)
    return [[map_pt(pt) for pt in path] for path in paths]

def get_face_draw_text(d, t, face3d, text, family=None):

    proj_face_lines = []
    line_count = 10
    origin = face3d[0]
    endx = face3d[1]
    endy = face3d[3]
    diffx = (endx[0] - origin[0], endx[1] - origin[1], endx[2] - origin[2])
    diffy = (endy[0] - origin[0], endy[1] - origin[1], endy[2] - origin[2])
    line1 = []
    line2 = []
    line3 = []
    # surround = [Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)]
    surround = [Point(0, 0.05), Point(0, 0.95), Point(0.05, 1), Point(0.95, 1), Point(1, 0.95), Point(1, 0.05), Point(0.95, 0), Point(0.05, 0), Point(0, 0.05)]
    n = 200

    mapped_text_paths = []
    if text != " ":
        text_paths = d.make_text(text, Point(0, 0), 12, family=family)
        for text_path in text_paths:
            text_path.append(text_path[0])
        mapped_text_paths = scale_to_unit_square(text_paths)
    
    for i in range(0, n+1):
        a = math.pi * 2 * i / n
        line1.append(Point(1 + math.cos(a), 1 + math.sin(a)) * 0.5)
        line2.append(Point(1.333 + math.cos(a), 1.333 + math.sin(a)) * 0.375)
        line3.append(Point(2 + math.cos(a), 2 + math.sin(a)) * 0.25)
    # lines = [surround, line1, line3] # , line3]
    
    lines = mapped_text_paths
    # lines.append(surround)
    face_lines = [[(origin[0] + diffx[0] * p.x + diffy[0] * p.y, origin[1] + diffx[1] * p.x + diffy[1] * p.y, origin[2] + diffx[2] * p.x + diffy[2] * p.y, 1.0) for p in line] for line in lines]
    for face_line in face_lines:
        proj_face_line = t.project(face_line)
        proj_face_lines.append(proj_face_line)
    return proj_face_lines

def get_face_draw_edge(t, face3d):

    proj_face_lines = []
    line_count = 10
    origin = face3d[0]
    endx = face3d[1]
    endy = face3d[3]
    diffx = (endx[0] - origin[0], endx[1] - origin[1], endx[2] - origin[2])
    diffy = (endy[0] - origin[0], endy[1] - origin[1], endy[2] - origin[2])
    line1 = []
    line2 = []
    line3 = []
    # surround = [Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)]
    surround = [Point(0, 0.05), Point(0, 0.95), Point(0.05, 1), Point(0.95, 1), Point(1, 0.95), Point(1, 0.05), Point(0.95, 0), Point(0.05, 0), Point(0, 0.05)]
    lines = [surround]
    # lines.append(surround)
    face_lines = [[(origin[0] + diffx[0] * p.x + diffy[0] * p.y, origin[1] + diffx[1] * p.x + diffy[1] * p.y, origin[2] + diffx[2] * p.x + diffy[2] * p.y, 1.0) for p in line] for line in lines]
    for face_line in face_lines:
        proj_face_line = t.project(face_line)
        proj_face_lines.append(proj_face_line)
    return proj_face_lines

def draw_3d_shade(d):

    cameraToWorld = numpy.identity(4)
    cameraToWorld[3][2] = 10
    t = Transform3D(cameraToWorld, canvasWidth=2, canvasHeight=2, imageWidth=100, imageHeight=100)
        
    h = 1
    s = 0.3
    base_points = [(s, s, s, h), (s, -s, s, h), (-s, -s, s, h), (-s, s, s, h), (s, s, -s, h), (s, -s, -s, h), (-s, -s, -s, h), (-s, s, -s, h)]

    a = math.pi / 3

    letters = [x for x in "`¬!£$%&*()_+={:<>?@}~[;,./'#]"]
    letters = [x for x in "^_`abcdefghi"]
    ix_letter = 0

    for c in range(0, 9):
        for r in range(0, 6):
            scale = 0.75
            dx = 0 + 25 * r
            dy = 0 + 25 * c
            a += math.pi / 30

            letter = letters[ix_letter]
            ix_letter += 1
            if ix_letter == len(letters):
                ix_letter = 0
            # letter = "a"
    
            all_faces = []
            
            world_points = [p for p in base_points]
            zc = 0
            xc = 0
            yc = 0
            world_points = [(p[0]+xc, p[1]+yc, p[2]+zc, p[3]) for p in world_points]
            world_points = Transform3D.rotZ(world_points, a)
            world_points = Transform3D.rotX(world_points, a)
            world_points = [(p[0], p[1], p[2]+8, p[3]) for p in world_points]

            faces3d = cube_open_faces(world_points)

            # should order by distance, nearest first
            # need to progressively clip this based upon the overall face projection
            # pass in the face drawing as a method?
            
            for face3d in faces3d:
                proj_face_points = t.project(face3d)
                # StandardDrawing.log(proj_face_points)
                if Transform3D.isForward(proj_face_points):
                    if letter != " ":
                        proj_face_lines = get_face_draw_text(d, t, face3d, letter, family='Wingdings')
                        proj_face_lines = [[(x[0]*scale+dx, x[1]*scale+dy) for x in proj_face_line] for proj_face_line in proj_face_lines]
                        sf = ShapeFiller(proj_face_lines)
                        paths = sf.get_paths(d.pen_type.pen_width / 5 * 2)
                        d.add_polylines(paths)
                    
                    proj_face_lines = get_face_draw_edge(t, face3d)
                    proj_face_lines = [[(x[0]*scale+dx, x[1]*scale+dy) for x in proj_face_line] for proj_face_line in proj_face_lines]
                    d.add_polylines(proj_face_lines)
                        
def draw_unknown_pleasures(drawing):

    min_y = {}
    data = []
    # File from https://github.com/igorol/unknown_pleasures_plot/blob/master/pulsar.csv
    with open('pulsar.csv') as csvfile:
        reader = csv.reader(csvfile)
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
    data = data[::-1]
    nrows = len(data)
    nitems = len(data[0])
    # print(f'We have {nrows} rows, each of which has {nitems} data items')
    y_min = 20
    y_max = 200
    x_min = 20
    x_max = 150
    y_scale = 0.28
    min_ys = {}
    for i in range(0, nrows):
        y_base = y_max + (y_min - y_max) * i / (nrows - 1)
        rowdata = data[i]
        path = []
        for j in range(0, nitems):
            x = x_min + (x_max - x_min) * j / (nitems - 1)
            min_y = min_ys.get(x, 10000.0)
            y = y_base - float(rowdata[j]) * y_scale
            if y < min_y:
                min_ys[x] = y
            else:
                y = min_y
            path.append((x, y))
        drawing.add_polyline(path)
        drawing.add_polyline(path)


