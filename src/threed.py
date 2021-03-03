import numpy.matlib 
import numpy as np 

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
 