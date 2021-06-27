import cv2
import math
import random

from pyplot import Point

def get_image_intensity(image, x, y):

    (xsize_image,ysize_image,c) = image.shape
    x_int = int(x+0.5)
    y_int = int(y+0.5)
    if x_int < 0 or x_int >= xsize_image or y_int < 0 or y_int >= ysize_image:
        return 0
    return image[x_int, y_int][0] / 255

def set_image_intensity(image, x, y, value):

    (xsize_image,ysize_image,c) = image.shape
    x_int = int(x+0.5)
    y_int = int(y+0.5)
    if x_int < 0 or x_int >= xsize_image or y_int < 0 or y_int >= ysize_image:
        return
    image[x_int, y_int][0] = value

def image_sketch(d):

    layer1 = d.add_layer("1")
    layer2 = d.add_layer("1")

    image = cv2.imread('burroughs2.jpg') #The function to read from an image into OpenCv is imread()
    (xsize_image,ysize_image,c) = image.shape
    
    print(image.shape)
    
    x_extent = 100
    # mm per pixel
    scale = x_extent / ysize_image
    r = x_extent / 20
    offset = (20, 20)
    
    intensity = lambda x, y: get_image_intensity(image, x, y)
    
    polylines = []
    n = 37
    angles = [i * 2 * math.pi / n for i in range(0, n)]
    trigs = [(math.cos(a), math.sin(a)) for a in angles]
    polyline = []
    pt = None
    expavg_ntries = 0
    for i in range(0, 30000):
        if i % 100 == 0:
            print(f"points={i} expavg_ntries={expavg_ntries:.2f}")

        ntries = 0
        while pt is None:
            ntries += 1
            x = random.random() * xsize_image
            y = random.random() * ysize_image
            pt1 = (x, y)
            k = intensity(pt1[0], pt1[1])
            if k >= 0.35:
                pt = pt1
            else:
                if 0.9 * expavg_ntries + 0.1 * ntries > 100:
                    break
                
        if pt is None:
            print("Breaking")
            break
        expavg_ntries = 0.9 * expavg_ntries + 0.1 * ntries
        
        r = 5 + int(random.random()*5)
        # r = 3 + int(random()*20) # this is too long - skips over black areas
        r = 10

        threshold = 0.10
        
        best_max_avg_intensity = -1
        max_trig = None
        max_best_j = 0
        for trig in trigs:
            total_intensity = 0
            max_avg_intensity = -1
            min_intensity = 1
            best_j = 0
            for j in range(1, r):
                k = intensity(pt[0]+j*trig[0], pt[1]+j*trig[1])
                if k < threshold:
                    break
                total_intensity += k
                j_avg_intensity = total_intensity / j
                if j_avg_intensity > max_avg_intensity:
                    best_j = j
                    max_avg_intensity = j_avg_intensity
                
            avg_intensity = total_intensity / r
            if max_avg_intensity > best_max_avg_intensity:
                best_max_avg_intensity = max_avg_intensity
                max_trig = trig
                max_best_j = best_j
                
        # zero out in the image
        # set_image_intensity(image, pt[0], pt[1], 0)
        if best_max_avg_intensity > threshold:
            if len(polyline) == 0:
                polyline = [(pt[1]*scale, pt[0]*scale)]

            for j in range(0, max_best_j):
                pt_j = (pt[0]+j*max_trig[0], pt[1]+j*max_trig[1])
                f0 = pt_j[0] - int(pt_j[0])
                f1 = pt_j[1] - int(pt_j[1])
                up0 = xsize_image - 1 if pt_j[0] == xsize_image else pt_j[0] + 1
                up1 = ysize_image - 1 if pt_j[1] == ysize_image else pt_j[1] + 1
                drop = 1
                set_image_intensity(image, pt_j[0], pt_j[1], max(0, intensity(pt_j[0], pt_j[1]) - drop * (1-f0) * (1-f1)))
                set_image_intensity(image, up0, pt_j[1], max(0, intensity(up0, pt_j[1]) - drop * f0 * (1-f1)))
                set_image_intensity(image, up0, up1, max(0, intensity(up0, up1) - drop * f0 * f1))
                set_image_intensity(image, pt_j[0], up1, max(0, intensity(pt_j[0], up1) - drop * (1-f0) * f1))

            line_end = (pt[0]+max_best_j*max_trig[0], pt[1]+max_best_j*max_trig[1])
            polyline.append((line_end[1]*scale, line_end[0]*scale))
            pt = line_end
        else:
            if len(polyline) > 0:
                polylines.append(polyline)
                polyline = []
            pt = None
        
    print(len(polylines))
        
    for polyline in polylines:
        d.add_polyline([(p[0]+offset[0], p[1]+offset[1]) for p in polyline])

def image_sketch2(d):

    layer1 = d.add_layer("1")
    layer2 = d.add_layer("1")

    image = cv2.imread('burroughs2.jpg') #The function to read from an image into OpenCv is imread()
    (image_xsize,iamge_ysize,c) = image.shape
    
    print(image.shape)
    
    x_extent = 100
    # mm per pixel
    scale = x_extent / iamge_ysize
    y_extent = scale * image_xsize
    offset = Point(20, 20)
    x_c = 60
    side = x_extent / x_c
    image_side = iamge_ysize / x_c
    y_c = int(y_extent * x_c / x_extent)
    
    intensity = lambda x, y: get_image_intensity(image, x, y)
    
    polylines = []
    
    for x_i in range(0, x_c):
        for y_i in range(0, y_c):
            image_tl = Point(y_i, x_i) * image_side
            n_intensity = 0
            tot_intensity = 0
            for image_x in range(int(image_tl.x), int(image_tl.x + image_side)):
                for image_y in range(int(image_tl.y), int(image_tl.y + image_side)):
                    n_intensity += 1
                    tot_intensity += intensity(image_x, image_y)
            ratio_intensity  = (tot_intensity / n_intensity)
            # print(image_tl, x_i, y_i, x_c, y_c, tot_intensity, n_intensity, ratio_intensity)
            tl = offset + Point(x_i, y_i) * side
            centre = tl + Point(1, 1) * side / 2
            if ratio_intensity > 0:
                r_outer = (1-ratio_intensity) * side
                r_start = r_outer - 0.2
                if r_start <= 0:
                    r_start = None
                polylines.append(d.make_dot(centre, r_outer, r_start=r_start))
        
    print(len(polylines))
        
    for polyline in polylines:
        d.add_polyline([(p[0]+offset[0], p[1]+offset[1]) for p in polyline])
