# necessary python modules
# * noise (for perlin stuff)
# * opencv-python
# * pycairo (for text)
# * svgwrite

import cv2
import csv

import svgwrite
from svgwrite.extensions import Inkscape

from random import random, seed
# seed random number generator
seed(10)

import math

class BWConverters:

    @staticmethod
    def AverageIntensity(r, g, b):

        RGB_SCALE = 255
        
        rc = r / RGB_SCALE
        gc = g / RGB_SCALE
        bc = b / RGB_SCALE
        # white = no wiggle (0), black = maximum wiggle (1)
        return (rc + gc + bc) / 3

    @staticmethod
    def InverseAverageIntensity(r, g, b):

        return 1- BWConverters.AverageIntensity(r, g, b)

class CMYKConverters:

    @staticmethod
    def Error(r, g, b):

        raise Exception("Cannot convert RGB for this pen type")

    @staticmethod
    def PigmaMicron(r, g, b):

        # Use with Sakura Pigma Micron coloured pens, here the colours to use are:
        # * C = Blue (not Royal Blue)
        # * M = Rose
        # * Y = Yellow
        # The pens are not true CMY, but if we downweigh the "C" and "Y", we get a pretty good colour balance.
        # This mix has been arrived at by eye, doing test plots with R, G, B, C, M, Y and 50% grey.

        RGB_SCALE = 255

        # rgb [0,255] -> cmy [0,1]
        # white = no wiggle (0), black = maximum wiggle (1)
        
        if (r, g, b) == (0, 0, 0):
            # black
            return (1, 1, 1)
            
        rc = r / RGB_SCALE
        gc = g / RGB_SCALE
        bc = b / RGB_SCALE
        k = 0.0 # we don't use black as this we are calculating for "wiggle" plots: here, using black doesn't make sense
        c = (1 - rc - k) / (1 - k) * 0.5
        m = (1 - gc - k) / (1 - k)
        y = (1 - bc - k) / (1 - k) * 0.8

        return (c, m, y, k)

    @staticmethod
    def Unadjusted(r, g, b):

        RGB_SCALE = 255

        # rgb [0,255] -> cmy [0,1]
        # white = no wiggle (0), black = maximum wiggle (1)
        
        if (r, g, b) == (0, 0, 0):
            # black
            return (1, 1, 1)
            
        rc = r / RGB_SCALE
        gc = g / RGB_SCALE
        bc = b / RGB_SCALE
        k = 0.0 # we don't use black as this we are calculating for "wiggle" plots: here, using black doesn't make sense
        c = (1 - rc - k) / (1 - k)
        m = (1 - gc - k) / (1 - k)
        y = (1 - bc - k) / (1 - k)

        return (c, m, y, k)

class PenType:

    def __init__(self, name, is_black, pen_width, stroke_width, bw_converter, rgb_converter):
        self.name = name
        self.is_black = is_black
        self.pen_width = pen_width
        self.stroke_width = stroke_width
        self.bw_converter = bw_converter
        self.rgb_converter = rgb_converter

    @staticmethod
    def GellyRollOnBlack():
        return PenType('GellyRollOnBlack', True, 0.6, '0.45px', BWConverters.InverseAverageIntensity, CMYKConverters.Error)
        
    @staticmethod
    def PigmaMicron05():
        return PenType('PigmaMicron05', False, 0.45, '0.33px', BWConverters.AverageIntensity, CMYKConverters.PigmaMicron)
        
    @staticmethod
    def StaedtlerPigment05():
        return PenType('StaedtlerPigment05', False, 0.5, '0.36px', BWConverters.AverageIntensity, CMYKConverters.Unadjusted)

class StandardDrawing:

    def __init__(self, file='test.svg', pen_type=None):
        self.dwg = svgwrite.Drawing(file, size=('210mm', '297mm'), viewBox="0 0 210 297") # height='210mm', width='297mm') # , viewBox="0 0 210 297")
        self.strokeBlack = svgwrite.rgb(0, 0, 0, '%')
        self.strokeWhite = svgwrite.rgb(255, 255, 255, '%')
        self.inkscape = Inkscape(self.dwg)
        self.pen_type = PenType.PigmaMicron05() if pen_type is None else pen_type
        if self.pen_type.is_black:
            layer = self.add_layer("x-background")
            layer.add(self.dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='rgb(0,0,0)'))

    def default_container(self, container):
        return self.dwg if container is None else container
    
    def default_stroke(self, stroke):
        if not stroke is None:
            return stroke
        if self.pen_type.is_black:
            return self.strokeWhite
        return self.strokeBlack
        
    def add_polyline(self, points, stroke=None, container=None):
        container = self.default_container(container)
        stroke = self.default_stroke(stroke)
        container.add(self.dwg.polyline(points, stroke=stroke, stroke_width=self.pen_type.stroke_width, fill='none'))
        
    def add_layer(self, label):
        layer = self.inkscape.layer(label=label)
        self.dwg.add(layer)
        return layer

    def add_polygon(self, points, stroke=None, container=None):
        stroke = self.default_stroke(stroke)
        container = self.default_container(container)
        polygon = self.dwg.polygon(points, stroke=stroke, stroke_width=self.pen_type.stroke_width, fill='none')
        container.add(polygon)

    def make_square(self, x, y, size):
        points = []
        points.append((x, y))
        points.append((x + size, y))
        points.append((x + size, y + size))
        points.append((x, y + size))
        return points

    def add_square(self, x, y, size, stroke=None, container=None):    
        points = self.make_square(x, y, size)
        self.add_polygon(points, stroke, container)

    def make_rect(self, top_left, x_size, y_size):
        points = []
        points.append(top_left)
        points.append((top_left[0] + x_size, top_left[1]))
        points.append((top_left[0] + x_size, top_left[1] + y_size))
        points.append((top_left[0], top_left[1] + y_size))
        return points

    def add_rect(self, top_left, x_size, y_size, stroke=None, container=None):    
        points = self.make_rect(top_left, x_size, y_size)
        self.add_polygon(points, stroke, container)
        
    def add_line(self, line_start, line_end, stroke=None, container=None):
        stroke = self.default_stroke(stroke)
        container = self.default_container(container)
        container.add(self.dwg.line(line_start, line_end, stroke=stroke, stroke_width=self.pen_type.stroke_width)) 
        
    def get_circle_point(self, middle, radius, theta):
        s = math.sin(theta)
        c = math.cos(theta)
        return (middle[0] + radius * s, middle[1] + radius * c)

    def make_circle(self, middle, r, n, stroke=None):
        stroke = self.default_stroke(stroke)
        points = []
        for i in range(0, n + 1):    
            angle = 2 * math.pi * i / n
            p = self.get_circle_point(middle, r, angle)
            points.append( p )
        return points

    def add_circle(self, middle, r, n, stroke=None, container=None):
        points = self.make_circle(middle, r, n, stroke)
        self.add_polygon(points, stroke=stroke, container=container)

    def make_dot(self, centre, radius, r_start=None, xy_func=None):

        pen_width = self.pen_type.pen_width

        points = []
        a = 0 # starting angle
        r_per_circle = pen_width / 2 # half pen width
        do_inner_circle = False
        r = r_per_circle / 3 # initial radius
        if not r_start is None:
            r = r_start
            do_inner_circle = True
        c_size = pen_width # constant distance travelled: something like the nib width is probably best

        xy_default_func = (lambda r,a: (r * math.cos(a), r * math.sin(a)))
        xy_func = xy_default_func if xy_func is None else xy_func

        # scaling - what's the biggest distance when r = 1?
        a_test = 0
        max_d = 0
        while a_test < math.pi * 2:
            xy = xy_func(1,a_test)
            d = math.sqrt(xy[0]*xy[0] + xy[1]*xy[1])
            max_d = max(max_d, d)
            a_test += c_size / r

        # first circle if doing inner
        if do_inner_circle:
            while a < math.pi * 2:
                a += c_size / r
                xy = xy_func(r,a)
                x = centre[0] + xy[0]
                y = centre[1] + xy[1]
                points.append((x, y))
        else:
            points.append(centre)
        
        # draw until we've hit the desired size
        while r <= radius:
        
            # Archimedian spiral with constant length of path
            r_floored = max(r, 0.5)
            a_inc = c_size / r_floored
            a += a_inc
            r += r_per_circle * a_inc / (2 * math.pi)
            
            # output location
            s = math.sin(a)
            c = math.cos(a)
            xy = xy_func(r,a)
            x = centre[0] + xy[0]
            y = centre[1] + xy[1]
            
            points.append((x, y))
            
        # now go one more time around
        a_last = 0
        while a_last < math.pi * 2:
        
            a_last += c_size / radius
            xy = xy_func(r,a + a_last)
            x = centre[0] + xy[0]
            y = centre[1] + xy[1]
            points.append((x, y))
            
        return points
                
    def add_dot(self, centre, radius, stroke=None, container=None, r_start=None, xy_func=None):
        
        points = self.make_dot(centre, radius, r_start, xy_func)
        self.add_polyline(points, stroke=stroke, container=container)
            
    def make_square(self, topleft, size, start_size=None):
    
        pen_width = self.pen_type.pen_width
        points = []
        
        curr_size = pen_width / 4 if start_size is None else start_size
        
        centre = (topleft[0] + size/2, topleft[1] + size/2)
        while curr_size < size:
            points.append((centre[0] - curr_size/2, centre[1] - curr_size/2))
            points.append((centre[0] - curr_size/2, centre[1] + curr_size/2))
            points.append((centre[0] + curr_size/2, centre[1] + curr_size/2))
            points.append((centre[0] + curr_size/2, centre[1] - curr_size/2))
            curr_size += pen_width / 2
        points.append((centre[0] - size/2, centre[1] - size/2))
        points.append((centre[0] - size/2, centre[1] + size/2))
        points.append((centre[0] + size/2, centre[1] + size/2))
        points.append((centre[0] + size/2, centre[1] - size/2))
        return points

    def add_square(self, topleft, size, start_size=None, stroke=None, container=None):
    
        points = self.make_square(topleft, size, start_size)
        self.add_polyline(points, stroke=stroke, container=container)

    @staticmethod
    def text_bound(text, fontsize=14, family='Arial'):
        try:
            import cairo
        except Exception:
            return len(text) * fontsize
        surface = cairo.SVGSurface('undefined.svg', 1280, 200)
        cr = cairo.Context(surface)
        cr.select_font_face(family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(fontsize)
        xbearing, ybearing, width, height, xadvance, yadvance = cr.text_extents(text)
        return (width, height)

    def add_spiral_letter(self, letter, fontsize, spiral_centre, radius, angle=0, family='Arial', stroke=None, container=None):

        container = self.dwg if container is None else container
        stroke = self.default_stroke(stroke)
        g = self.dwg.g(style=f"font-size:{fontsize};font-family:{family};font-weight:normal;font-style:normal;stroke:black;fill:none") # stroke-width:1;
        
        # unadjusted y is at bottom left (high y, low x)

        space_letter = letter if letter != " " else "ll"
        (w1, h1) = StandardDrawing.text_bound(f"X{space_letter}X", fontsize, family)
        (w2, h2) = StandardDrawing.text_bound(f"XX", fontsize, family)
        (w3, h3) = StandardDrawing.text_bound(letter, fontsize, family)
        w = w1 - w2
        h = h3
        
        s = math.sin(angle * math.pi / 180)
        c = math.cos(angle * math.pi / 180)
        x_letter = spiral_centre[0] # + radius * s # - w/2 * c
        y_letter = spiral_centre[1] - radius # - radius * c # + w/2 * s
        #x_rotc = spiral_centre[0] + radius * s + w/2 * c
        #y_rotc = spiral_centre[1] - radius * c - w/2 * s
        g.add(self.dwg.text(letter, insert=(x_letter, y_letter), transform=f'rotate({angle}, {spiral_centre[0]}, {spiral_centre[1]})', stroke=stroke)) # settings are valid for all text added to 'g'
        
        self.dwg.add(g)
        
        return (w, h)
    
    def make_spiral(self, centre, scale, r_per_circle=None, r_initial=None, direction=1):

        points = []
        r = 0 if r_initial is None else r_initial # initial radius
        a = 0 # starting angle
        r_per_circle = 2 * self.pen_type.pen_width if r_per_circle is None else r_per_circle # gap between spiral paths: 1 is tightest
        c_size = 0.5 # constant distance travelled: something like the nib width is probably best
        
        # draw until we've hit the desired size
        while r <= scale:
        
            # Archimedian spiral with constant length of path
            r_floored = max(r, 0.5)
            a_inc = c_size / r_floored
            a += a_inc * direction
            r += r_per_circle * a_inc / (2 * math.pi)
            
            # output location
            s = math.sin(a)
            c = math.cos(a)
            x = centre[0] + r * c
            y = centre[1] + r * s
            
            points.append((x, y))
            
        return points
 
    def add_spiral(self, centre, scale, r_per_circle=None, r_initial=None, container=None, stroke=None, direction=1):

        points = self.make_spiral(centre, scale, r_per_circle, r_initial, direction)
        self.add_polyline(points, stroke, container)

    @staticmethod
    def add_wiggle(points, new_point, line_mult):    

        prev = points[-1]
        half = (0.5 * (new_point[0] - prev[0]), 0.5 * (new_point[1] - prev[1]))
        p1 = (prev[0] + half[0] - (line_mult/2) * half[1], prev[1] + half[1] + (line_mult/2) * half[0])
        p2 = (prev[0] + half[0] + (line_mult/2) * half[1], prev[1] + half[1] - (line_mult/2) * half[0])
        points.append(p1)
        points.append(p2)
        points.append(new_point)

    def image_spiral_single(self, container, file, centre, scale, stroke = None, r_factor_func = None, colour = False, cmy_index=0):

        if colour:
            intensity_converter = lambda r, g, b: self.pen_type.rgb_converter(r, g, b)[cmy_index]
        else:
            intensity_converter = self.pen_type.bw_converter

        # image size
        # image = cv2.imread('burroughs.jpg')
        # image = cv2.imread('testCard_F.jpg')
        # image = cv2.imread('test_wheel.jpg')
        image = cv2.imread(file) #The function to read from an image into OpenCv is imread()
        (h,w,c) = image.shape
        # print(image[0,0])
        img_centre = (int(h/2), int(w/2))
        img_size = min(int(h/2), int(w/2))
     
        pen_width = self.pen_type.pen_width
        points = []
        points.append(centre)
        r = 0.5 # initial radius
        a = 0 # starting angle
        c_size = 0.5 # constant distance travelled: something like the nib width is probably best
        r_per_circle = 1.35 * (pen_width / 0.6) # 2 and a bit times pen width seems to work well - can expand to 3*

        # what to multiply [0,1] intensity by to see how far we "wiggle" - this is applied to half the distance travelled
        # we want wiggles to slightly overlap between rows
        # we have
        # * k = size of wiggle we want to apply (including both up and down bits)
        # * k = mult * (c_size / 2)
        # * r_per_circle = gap between lines
        # * w = width of pen
        # Then we want k+w to be slightly bigger than r_per_circle
        # Let's say we want black to overlap by 0.6 of the pen width - this seems to provide an overall black coverage reliably
        # (Testing for that was carried out with 3-to-4z pen width for Sakura 0.45mm and Staedtler 0.5mm)
        # * k = (r_per_cicle - width) + width * 0.6
        # * mult = (r_per_cicle - 0.4*width) * (2 / c_size)
        mult = (r_per_circle - 0.4*pen_width) * (2 / c_size)
        # print(f'r_per_circle={r_per_circle}')
        # print(f'pen_width={pen_width}')
        # print(f'c_size={c_size}')
        # print(f'mult={mult}')
        
        # spiral out until we've hit the desired size
        while r <= scale:
        
            r_factor = 1
            if not r_factor_func is None:
                a_norm = a / (2 * math.pi)
                r_norm = r / scale
                tri = 1.0 - 2 * abs(r_norm - 0.5)
                r_factor = 1 + r_factor_func((a_norm, r_norm), 42) * tri
            r_factor = 1
        
            # Archimedian spiral with constant length of path
            a_inc = c_size / r * r_factor
            a += a_inc
            r += r_per_circle * a_inc / (2 * math.pi)

            # output location
            s = math.sin(a)
            c = math.cos(a)
            x = centre[0] + r * c * r_factor
            y = centre[1] + r * s * r_factor

            # image location (note x/y swap)
            ix = int(img_centre[0] + img_size * (y - centre[1]) / scale)
            iy = int(img_centre[1] + img_size * (x - centre[0]) / scale)
            
            pt = image[ix, iy]
            
            # image is BGR - pass in RGB
            intense = intensity_converter(pt[2], pt[1], pt[0])
            if self.pen_type.is_black:
                intense = 1.0 - intense
                
            shade = intense * mult * r_factor

            # "wiggle" on our way from "prev" to "new" with a width propertional to the intensity
            new = (x, y)
            StandardDrawing.add_wiggle(points, new, shade)

        # print(f'# points = {len(points)}')
        # print(r)
        # print(image.shape)
            
        self.add_polyline(points, stroke, container=container)

        # cv2.imshow("OpenCV Image Reading", image)
        # cv2.waitKey(0) #is req  

    def image_spiral_cmyk(self, file, centre, scale):

        # C is layer 1
        # M is layer 2
        # Y is layer 3
        for cmy_index in [0, 1, 2]:
            layer = self.add_layer(f"{cmy_index + 1}-cmy-layer")
            stroke_rgb = [255, 255, 255]
            stroke_rgb[cmy_index] = 0
            self.image_spiral_single(layer, file, centre, scale, stroke=svgwrite.rgb(stroke_rgb[0], stroke_rgb[1], stroke_rgb[2], '%'), colour=True, cmy_index=cmy_index)
  
    def fill_in_paths(self, path_gen_func):

        pen_width = self.pen_type.pen_width
        
        path0 = path_gen_func(0.0)
        path1 = path_gen_func(1.0)
        max_dist = 0
        if len(path0) != len(path1):
            raise Exception(f'Path length mismatch: len0={len(path0)} len1={len(path1)}')
        n = len(path0)
        for i in range(0, n):
            p0 = path0[i]
            p1 = path1[i]
            xd = p0[0] - p1[0]
            yd = p0[1] - p1[1]
            dist = math.sqrt(xd*xd + yd*yd)
            max_dist = max(max_dist, dist)
        # print(f'max_dist = {max_dist}')
        # print(f'pen_width = {pen_width}')
        num_strokes = 1 + int(max_dist / (pen_width * .5))
        # print(f'num_strokes = {num_strokes}')
        path = []
        for i in range(0, num_strokes + 1):
            t = i / num_strokes
            path_t = path_gen_func(t)
            if i % 2 == 1:
                path_t = path_t[::-1]
            path.extend(path_t)
        return path

class CircleBlock:    

    def __init__(self, outer_centre, outer_r, outer_phase, inner_centre, inner_r, inner_phase, slice_count, slice_start):
        self.outer_centre = outer_centre
        self.outer_r = outer_r
        self.outer_phase = outer_phase
        self.inner_centre = inner_centre
        self.inner_r = inner_r
        self.inner_phase = inner_phase
        self.slice_count = slice_count
        self.slice_start = slice_start

    def path_gen_f(self, t):

        path = []
        base_angle = 2 * math.pi * (self.slice_start + t) / self.slice_count
        inner_angle = base_angle + 2 * math.pi * self.inner_phase
        outer_angle = base_angle + 2 * math.pi * self.outer_phase
        inner_p = (self.inner_centre[0] + self.inner_r * math.sin(inner_angle), self.inner_centre[1] + self.inner_r * math.cos(inner_angle))
        outer_p = (self.outer_centre[0] + self.outer_r * math.sin(outer_angle), self.outer_centre[1] + self.outer_r * math.cos(outer_angle))
        path.append(inner_p)
        path.append(outer_p)
        return path

