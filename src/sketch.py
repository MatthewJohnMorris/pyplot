import cv2
import math
import random

from pyplot import Point,StandardDrawing

def get_image_intensity(image, x, y):

    (xsize_image,ysize_image,c) = image.shape
    x_int = int(x+0.5)
    y_int = int(y+0.5)
    if x_int < 0 or x_int >= xsize_image or y_int < 0 or y_int >= ysize_image:
        return 0
    return image[x_int, y_int][0] / 255

def get_image_intensity_int(image, x, y):

    return image[x, y][0] / 255

def get_image_intensity_fract(image, x, y):

    (xsize_image,ysize_image,c) = image.shape
    if x < 0 or x >= xsize_image-1 or y < 0 or y >= ysize_image-1:
        return 0
    fx = 1 - (x - int(x))
    fy = 1 - (y - int(y))
    x0 = int(x)
    x1 = x0 + 1
    y0 = int(y)
    y1 = y0 + 1
    i00 = get_image_intensity_int(image, x0, y0)
    i01 = get_image_intensity_int(image, x0, y1)
    i10 = get_image_intensity_int(image, x1, y0)
    i11 = get_image_intensity_int(image, x1, y1)
    blended_intensity = i00*fx*fy + i01*fx*(1-fy) + i10*(1-fx)*fy + i11*(1-fx)*(1-fy)
    return blended_intensity

def set_image_intensity(image, x, y, value):

    (xsize_image,ysize_image,c) = image.shape
    x_int = int(x+0.5)
    y_int = int(y+0.5)
    if x_int < 0 or x_int >= xsize_image or y_int < 0 or y_int >= ysize_image:
        return
    image[x_int, y_int][0] = value

def set_image_intensity_int(image, x, y, value):

    image[x, y][0] = value * 255

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
    layer2 = d.add_layer("2")

    image = cv2.imread('burroughs2.jpg') #The function to read from an image into OpenCv is imread()
    (image_xsize,iamge_ysize,c) = image.shape
    
    print(image.shape)
    
    x_extent = 100
    # mm per pixel
    scale = x_extent / iamge_ysize
    y_extent = scale * image_xsize
    offset = Point(20, 20)
    x_c = 15
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
                r_outer = (1-ratio_intensity) * side / 2
                while r_outer > 0:
                    line = d.make_circle(centre, r_outer)
                    line.append(line[0])
                    polylines.append(line)
                    r_outer -= d.pen_type.pen_width * 2
        
    print(len(polylines))
        
    for polyline in polylines:
        d.add_polyline([(p[0]+offset[0], p[1]+offset[1]) for p in polyline])

def image_sketch3_woolf(d):

    layer1 = d.add_layer("1")
    layer2 = d.add_layer("1")

    disk_image = cv2.imread('burroughs2.jpg') #The function to read from an image into OpenCv is imread()
    disk_image = cv2.imread('woolf.jpg') #The function to read from an image into OpenCv is imread()
    (xsize_image,ysize_image,c) = disk_image.shape
    
    StandardDrawing.log(disk_image.shape)
    StandardDrawing.log(f'PointCount={xsize_image*ysize_image}')

    ntrigs = 37 # 13 # 37 # 13 # 93 # 11 # 37
    n = 10000 # 8000
    drop_mult = 20
    path_div = 40
    
    ntrigs = 36 # 37 # 13 # 93 # 11 # 37
    n = 9000 # 8000
    drop_mult = 5
    path_div = 40
    
    x_extent = 150
    # mm per pixel
    scale = x_extent / ysize_image
    path_len = int(min(xsize_image, ysize_image)/ path_div)
    StandardDrawing.log(f'path_len={path_len}')
    # r = 6
    offset = (20, 20)
    
    mem_image = MemImage(disk_image)
    
    image = mem_image
    image = disk_image

    StandardDrawing.log("Invert drawing")
    for x_image in range(0, xsize_image):
        for y_image in range(0, ysize_image):
            a = image[x_image, y_image]
            image[x_image, y_image][0] = 255 - image[x_image, y_image][0]
    
    intensity = lambda x, y: get_image_intensity_fract(image, x, y)
    
    polylines = []
    angles = [i * 2 * math.pi / ntrigs for i in range(0, ntrigs)]
    trigs = [(math.cos(a), math.sin(a)) for a in angles]
    polyline = []
    pt = None
    expavg_ntries = 0
    
    # get starting point - max intensity
    StandardDrawing.log("Find starting point")
    start = None
    for x_image in range(0, xsize_image):
        for y_image in range(0, ysize_image):
            xy_intensity = intensity(x_image, y_image)
            if start is None:
                start = (x_image, y_image, xy_intensity)
            elif xy_intensity > start[2]:
                start = (x_image, y_image, xy_intensity)
    StandardDrawing.log(f"start={start}")

    drop = scale * d.pen_type.pen_width * 2 * drop_mult
    #print(x_extent)
    #print(ysize_image)
    #print(scale)
    #print(d.pen_type.pen_width)
    #print(scale * d.pen_type.pen_width)
    #print(drop)

    StandardDrawing.log("Drawing")
    pt = start
    percent = 0
    for i in range(0, n): # 10000): # 6000):
        i_percent = int(100*i/n)
        if i_percent > percent:
            percent = i_percent
            StandardDrawing.log(f"points={i} ({percent}%)")
            # raise Exception("blah")

        best_avg_intensity = -1
        max_trig = None
        for trig in trigs:
            total_intensity = 0
            for jj in range(1, path_len):
                k = intensity(pt[0]+jj*trig[0], pt[1]+jj*trig[1])
                # penalise crossing very light areas
                if k < 0.2:
                    k = -0.2
                total_intensity += k
            avg_intensity = total_intensity / path_len
            if avg_intensity > best_avg_intensity:
                best_avg_intensity = avg_intensity
                max_trig = trig
                
        #print(i, pt, best_avg_intensity, max_trig)
                
        # print(best_max_avg_intensity)
        if best_avg_intensity == 0.0:

            print(pt)
            for trig in trigs:
                total_intensity = 0
                for jj in range(1, path_len):
                    k = intensity(pt[0]+jj*trig[0], pt[1]+jj*trig[1])
                    total_intensity += k
                avg_intensity = total_intensity / path_len

            max_trig = trigs[int(random.random() * len(trigs))]
            #print("random", max_trig)
                
        # zero out in the image
        # set_image_intensity(image, pt[0], pt[1], 0)
        if len(polyline) == 0:
            polyline = [(offset[0]+pt[1]*scale, offset[1]+pt[0]*scale)]

        for j in range(0, path_len-1):
            pt_j = (pt[0]+j*max_trig[0], pt[1]+j*max_trig[1])

            x = pt_j[0]
            y = pt_j[1]
            fx = 1 - (x - int(x))
            fy = 1 - (y - int(y))
            x0 = int(x)
            y0 = int(y)
            if x0 < xsize_image and y0 < ysize_image:
                x1 = min(xsize_image-1, x0 + 1)
                y1 = min(ysize_image-1, y0 + 1)
                set_image_intensity_int(image, x0, y0, max(0, intensity(x0, y0) - drop * fx     * fy))
                set_image_intensity_int(image, x1, y0, max(0, intensity(x1, y0) - drop * fx     * (1-fy)))
                set_image_intensity_int(image, x0, y1, max(0, intensity(x0, y1) - drop * (1-fx) * fy))
                set_image_intensity_int(image, x1, y1, max(0, intensity(x1, y1) - drop * (1-fx) * (1-fy)))

        line_end = (pt[0]+path_len*max_trig[0], pt[1]+path_len*max_trig[1])
        #print(f"{pt}->{line_end} (unadj)")
        line_end = (max(0, line_end[0]), line_end[1])
        line_end = (min(xsize_image-1, line_end[0]), line_end[1])
        line_end = (line_end[0], max(0, line_end[1]))
        line_end = (line_end[0], min(ysize_image-1, line_end[1]))
        polyline.append((offset[0] + line_end[1]*scale, offset[1] + line_end[0]*scale))
        #print(f"{pt}->{line_end} (adj)")
        pt = line_end

                
        
    StandardDrawing.log(len(polyline))
    # print(polyline)
        
    d.add_polyline(polyline)

        
class MemImage:

    def __init__(self, disk_image):
        self.shape = disk_image.shape
        (xsize_image,ysize_image,c) = self.shape    
        self.a = []
        for x_image in range(0, xsize_image):
            x_array = []
            for y_image in range(0, ysize_image):
                x_array.append([disk_image[x_image, y_image][0]])
            self.a.append(x_array)
        
    def __getitem__(self, arg):
        (x,y) = arg
        return self.a[x][y]
        
def image_sketch3(d):

    layer1 = d.add_layer("1")
    layer2 = d.add_layer("1")

    disk_image = cv2.imread('burroughs2.jpg') #The function to read from an image into OpenCv is imread()
    disk_image = cv2.imread('woolf.jpg') #The function to read from an image into OpenCv is imread()
    
    disk_image = cv2.imread('kahlo.jpg') #The function to read from an image into OpenCv is imread()
    ntrigs = 37 # 13 # 37 # 13 # 93 # 11 # 37
    n = 10000 # 8000
    drop_mult = 20
    path_div = 40
    penalty = 0.1
    
    disk_image = cv2.imread('gove2.jpg') #The function to read from an image into OpenCv is imread()
    ntrigs = 37 # 13 # 37 # 13 # 93 # 11 # 37
    n = 12000 # 12000
    drop_mult = 30
    path_div = 70
    penalty = 0.1
    
    disk_image = cv2.imread('morrissey.jpg')
    ntrigs = 37 # 13 # 37 # 13 # 93 # 11 # 37
    n = 10000 # 12000
    drop_mult = 1
    path_div = 60
    penalty = 0.1
    
    disk_image = cv2.imread('morrissey.jpg')
    ntrigs = 37 # 13 # 37 # 13 # 93 # 11 # 37
    n = 7000 # 12000
    drop_mult = 0.5
    path_div = 30
    penalty = 0.1
    
    disk_image = cv2.imread('morrissey.jpg')
    ntrigs = 37 # 13 # 37 # 13 # 93 # 11 # 37
    n = 4350 # 12000
    drop_mult = 0.5
    path_div = 30
    penalty = 0.1

    disk_image = cv2.imread('mickey.jpg')
    ntrigs = 37 # 13 # 37 # 13 # 93 # 11 # 37
    n = 8050 # 12000
    drop_mult = 80
    path_div = 40
    penalty = 0.0
    
    disk_image = cv2.imread('768px-Margaret_Thatcher_(1983).jpg')
    ntrigs = 23 # 13 # 37 # 13 # 93 # 11 # 37
    n = 25000
    drop_mult = 1
    path_div = 30
    penalty = 0.0
    
    disk_image = cv2.imread('768px-Margaret_Thatcher_(1983).jpg')
    ntrigs = 23 # 13 # 37 # 13 # 93 # 11 # 37
    n = 137500 # 13000 # 12000 # 14000 # 16000 # 18000 # 20000 # 25000
    drop_mult = 5
    path_div = 30
    penalty = 0.0
    
    disk_image = cv2.imread('768px-Margaret_Thatcher_(1983).jpg')
    ntrigs = 23 # 13 # 37 # 13 # 93 # 11 # 37
    n = 18000 # 18000 # 20000 # 25000
    drop_mult = 3 # 1
    path_div = 30
    penalty = 0.0

    disk_image = cv2.imread('nixon.jpg')
    ntrigs = 23 # 13 # 37 # 13 # 93 # 11 # 37
    n = 10000 # 18000 # 20000 # 25000
    drop_mult = 160 # 1
    path_div = 30
    penalty = 0.0

    disk_image = cv2.imread('nixon.jpg')
    ntrigs = 23 # 13 # 37 # 13 # 93 # 11 # 37
    n = 4000 # 18000 # 20000 # 25000
    drop_mult = 160 # 1
    path_div = 8
    penalty = 0.0

    disk_image = cv2.imread('nixon.jpg')
    ntrigs = 23 # 13 # 37 # 13 # 93 # 11 # 37
    n = 24000 # 21000 # 24000 # 16000 # 20000 # 25000
    drop_mult = 160 # 1
    path_div = 60
    penalty = 0.0

    (xsize_image,ysize_image,c) = disk_image.shape
    StandardDrawing.log(disk_image.shape)
    StandardDrawing.log(f'PointCount={xsize_image*ysize_image}')
        
    x_extent = 150
    # mm per pixel
    scale = x_extent / ysize_image
    path_len = int(min(xsize_image, ysize_image)/ path_div)
    StandardDrawing.log(f'path_len={path_len}')
    # r = 6
    offset = (20, 20)
    
    mem_image = MemImage(disk_image)
    
    image = mem_image
    # image = disk_image

    StandardDrawing.log("Invert drawing")
    for x_image in range(0, xsize_image):
        for y_image in range(0, ysize_image):
            a = image[x_image, y_image]
            image[x_image, y_image][0] = 255 - image[x_image, y_image][0]
    
    intensity = lambda x, y: get_image_intensity_fract(image, x, y)
    
    polylines = []
    angles = [i * 2 * math.pi / ntrigs for i in range(0, ntrigs)]
    trigs = [(math.cos(a), math.sin(a)) for a in angles]
    polyline = []
    pt = None
    expavg_ntries = 0
    
    # get starting point - max intensity
    StandardDrawing.log("Find starting point")
    start = None
    for x_image in range(0, xsize_image):
        for y_image in range(0, ysize_image):
            xy_intensity = intensity(x_image, y_image)
            if start is None:
                start = (x_image, y_image, xy_intensity)
            elif xy_intensity > start[2]:
                start = (x_image, y_image, xy_intensity)
    StandardDrawing.log(f"start={start}")

    drop = scale * d.pen_type.pen_width * 2 * drop_mult
    #print(x_extent)
    #print(ysize_image)
    #print(scale)
    #print(d.pen_type.pen_width)
    #print(scale * d.pen_type.pen_width)
    #print(drop)

    StandardDrawing.log("Drawing")
    pt = start
    percent = 0
    for i in range(0, n): # 10000): # 6000):
        i_percent = int(100*i/n)
        if i_percent > percent:
            percent = i_percent
            StandardDrawing.log(f"points={i} ({percent}%)")
            # raise Exception("blah")

        best_avg_intensity = -1
        max_trig = None
        for trig in trigs:
            total_intensity = 0
            for jj in range(1, path_len):
                k = intensity(pt[0]+jj*trig[0], pt[1]+jj*trig[1])
                # penalise crossing very light areas
                if k < penalty:
                    k = -penalty
                total_intensity += k
            avg_intensity = total_intensity / path_len
            if avg_intensity > best_avg_intensity:
                best_avg_intensity = avg_intensity
                max_trig = trig
                
        #print(i, pt, best_avg_intensity, max_trig)
                
        # print(best_max_avg_intensity)
        if best_avg_intensity == 0.0:

            print(pt)
            for trig in trigs:
                total_intensity = 0
                for jj in range(1, path_len):
                    k = intensity(pt[0]+jj*trig[0], pt[1]+jj*trig[1])
                    total_intensity += k
                avg_intensity = total_intensity / path_len

            max_trig = trigs[int(random.random() * len(trigs))]
            #print("random", max_trig)
                
        # zero out in the image
        # set_image_intensity(image, pt[0], pt[1], 0)
        if len(polyline) == 0:
            polyline = [(offset[0]+pt[1]*scale, offset[1]+pt[0]*scale)]

        for j in range(0, path_len-1):
            pt_j = (pt[0]+j*max_trig[0], pt[1]+j*max_trig[1])

            x = pt_j[0]
            y = pt_j[1]
            fx = 1 - (x - int(x))
            fy = 1 - (y - int(y))
            x0 = int(x)
            y0 = int(y)
            if x0 < xsize_image and y0 < ysize_image:
                x1 = min(xsize_image-1, x0 + 1)
                y1 = min(ysize_image-1, y0 + 1)
                set_image_intensity_int(image, x0, y0, max(0, intensity(x0, y0) - drop * fx     * fy))
                set_image_intensity_int(image, x1, y0, max(0, intensity(x1, y0) - drop * fx     * (1-fy)))
                set_image_intensity_int(image, x0, y1, max(0, intensity(x0, y1) - drop * (1-fx) * fy))
                set_image_intensity_int(image, x1, y1, max(0, intensity(x1, y1) - drop * (1-fx) * (1-fy)))

        line_end = (pt[0]+path_len*max_trig[0], pt[1]+path_len*max_trig[1])
        #print(f"{pt}->{line_end} (unadj)")
        line_end = (max(0, line_end[0]), line_end[1])
        line_end = (min(xsize_image-1, line_end[0]), line_end[1])
        line_end = (line_end[0], max(0, line_end[1]))
        line_end = (line_end[0], min(ysize_image-1, line_end[1]))
        polyline.append((offset[0] + line_end[1]*scale, offset[1] + line_end[0]*scale))
        #print(f"{pt}->{line_end} (adj)")
        pt = line_end

                
        
    StandardDrawing.log(len(polyline))
    # print(polyline)
        
    d.add_polyline(polyline)

