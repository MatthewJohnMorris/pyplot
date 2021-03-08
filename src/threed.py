import math
import numpy.matlib 
import numpy as np 
import time

from pyplot import ShapeFiller

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
    
        shapes = []
        all_polylines = []
        
        for face in sorted_faces:
            if len(shapes) == 0:
                all_polylines.append(face)
                shapes.append(face[0:-1])
            else:
                # 4% just from this!
                print(f".", end='', flush=True)
                sf = ShapeFiller(shapes)
                
                # 50% of the time spent here?
                clipped = sf.clip([face], union=True)
                
                if len(clipped) > 0:
                    all_polylines.extend(clipped)
                    shapes.append(face[0:-1])
                    
        tEnd = time.perf_counter()
        print("clip-tot", tEnd - tStart)
        print(f"len(all_polylines)={len(all_polylines)}")
        print(f"len(shapes)={len(shapes)}")
                    
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
 