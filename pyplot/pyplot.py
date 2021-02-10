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
        # Note - if you use GellyRollOnBlack you will have a black rectangle added (on a layer whose name starts with "x") so you
        # can get some idea of what things will look like - SVG doesn't let you set a background colour. You should either delete this rectangle
        # before plotting, or use the "Layers" tab to plot - by default everything is written to layer "0-default"
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
        # Add this before any other layers
        if self.pen_type.is_black:
            layer = self.add_layer("x-background")
            layer.add(self.dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='rgb(0,0,0)'))
        self.default_layer = self.add_layer("0-default")

    def default_container(self, container):
        return self.default_layer if container is None else container
    
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
        return (middle[0] + radius * s, middle[1] - radius * c)

    # Default circle granularity: divide into parts no bigger than the width of the pen
    def default_circle_path_count(self, r):
        return int(2 * math.pi * r / self.pen_type.pen_width) + 1

    def make_circle(self, middle, r, n=None, stroke=None):
        n = self.default_circle_path_count(r) if n is None else n
        stroke = self.default_stroke(stroke)
        points = []
        for i in range(0, n):    
            angle = 2 * math.pi * i / n
            p = self.get_circle_point(middle, r, angle)
            points.append( p )
        return points

    def add_circle(self, middle, r, n=None, stroke=None, container=None):
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
        
    def make_surface(self, top_left, x_size, y_size, z_function):
    
        # can render texture with z-function applied by preserving x, and doing y-out = y * cos(a) + z * sin(a) with a the viewing angle?  
        projection_angle = math.pi * 3 /8
        min_adj_y_for_x = {}
        all_points = []
        for y in range(0, y_size + 1, 2)[::-1]:
            points = []
            for x in range(0, x_size + 1):
                norm_coord = (x / x_size, y / y_size)
                z = z_function(norm_coord)
                y_adj = math.cos(projection_angle) * y + math.sin(projection_angle) * z
                min_adj_y = min_adj_y_for_x.get(x, 1000)
                if y_adj < min_adj_y:
                    min_adj_y_for_x[x] = y_adj
                else:
                    y_adj = min_adj_y
                points.append((top_left[0] + x, top_left[1] + y_adj))
            all_points.append(points)
        return all_points

    def add_surface(self, top_left, x_size, y_size, z_func, stroke=None, container=None):
    
        all_points = self.make_surface(top_left, x_size, y_size, z_func)
        for points in all_points:
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

    @staticmethod
    def text_bound_letter(letter, fontsize, family):
        (w1, h1) = StandardDrawing.text_bound(f"X{letter}X", fontsize, family)
        (w2, h2) = StandardDrawing.text_bound(f"XX", fontsize, family)
        (w3, h3) = StandardDrawing.text_bound(letter, fontsize, family)
        w = w1 - w2
        return (w, h3)

    def draw_letter(self, letter, position, fontsize, angle=0, family='Arial', container=None, stroke=None):

        stroke = self.default_stroke(stroke)
        container = self.default_container(container)
        style=f"font-size:{fontsize};font-family:{family};font-weight:normal;font-style:normal;stroke:{stroke};fill:none"
        g = self.dwg.g(style=style)
        
        x = position[0]
        y = position[1]
        (w, h) = StandardDrawing.text_bound_letter(letter, fontsize, family)
        cx = x + w/2
        cy = y - w/2
        g.add(self.dwg.text(letter, insert=(x, y), transform=f'rotate({angle}, {cx}, {cy})')) # settings are valid for all text added to 'g'
        container.add(g)
        
        return (x + w, y)

    def draw_text(self, text, position, fontsize, family='Arial', container=None, stroke=None):

        stroke = self.default_stroke(stroke)
        container = self.default_container(container)
        style=f"font-size:{fontsize};font-family:{family};font-weight:normal;font-style:normal;stroke:{stroke};fill:none"
        g = self.dwg.g(style=style)
        g.add(self.dwg.text(text, insert=position))
        container.add(g)
        
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

    def image_spiral_single(self, container, file, centre, scale, stroke = None, r_factor_func = None, colour = False, cmy_index=0, x_scale=1):

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
            x = centre[0] + r * c * r_factor * x_scale
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

    def add_spiral_letter(self, letter, fontsize, spiral_centre, radius, angle=0, family='Arial', container=None, stroke=None):

        stroke = self.default_stroke(stroke)
        container = self.default_container(container)
        style=f"font-size:{fontsize};font-family:{family};font-weight:normal;font-style:normal;stroke:{stroke};fill:none"
        # print(style)
        g = self.dwg.g(style=style)
        
        # unadjusted y is at bottom left (high y, low x)

        (w,h) = StandardDrawing.text_bound_letter(letter, fontsize, family)
        
        s = math.sin(angle * math.pi / 180)
        c = math.cos(angle * math.pi / 180)
        x_letter = spiral_centre[0] # + radius * s # - w/2 * c
        y_letter = spiral_centre[1] - radius # - radius * c # + w/2 * s
        #x_rotc = spiral_centre[0] + radius * s + w/2 * c
        #y_rotc = spiral_centre[1] - radius * c - w/2 * s
        g.add(self.dwg.text(letter, insert=(x_letter, y_letter), transform=f'rotate({angle}, {spiral_centre[0]}, {spiral_centre[1]})', stroke=stroke)) # settings are valid for all text added to 'g'
        
        container.add(g)
        
        return (w, h)

    def plot_spiral_text(self, centre, scale, radial_adjust=0, repeat=False, text=None, container=None, fontsize=6):

        points = []
        points.append(centre)
        r = 0.5 # initial radius
        a = 0 # starting angle
        c_size = self.pen_type.pen_width # constant distance travelled: something like the nib width is probably best
        r_per_circle = fontsize
        
        i = 0
        # Let the spiral get going before we start plotting
        segments_to_next_letter = int(fontsize / c_size) + 1

        # Burroughs quote
        if text is None:
            text = "In the City Market is the Meet Café. Followers of obsolete, unthinkable trades doodling in Etruscan, addicts of drugs not yet synthesized, pushers of souped-up harmine, junk reduced to pure habit offering precarious vegetable serenity, liquids to induce Latah, Tithonian longevity serums, black marketeers of World War III, excusers of telepathic sensitivity, osteopaths of the spirit, investigators of infractions denounced by bland paranoid chess players, servers of fragmentary warrants taken down in hebephrenic shorthand charging unspeakable mutilations of the spirit, bureaucrats of spectral departments, officials of unconstituted police states, a Lesbian dwarf who has perfected operation Bang-utot, the lung erection that strangles a sleeping enemy, sellers of orgone tanks and relaxing machines, brokers of exquisite dreams and memories..."

        # draw until we've hit the desired size
        j = 0
        while r <= scale:
        
            # Archimedian spiral with constant length of path
            a_inc = c_size / r
            a += a_inc
            r += r_per_circle * a_inc / (2 * math.pi)
            
            # output location
            s = math.sin(a)
            c = math.cos(a)
            x = centre[0] + r * c
            y = centre[1] + r * s
            
            i += 1
            if i == segments_to_next_letter:
                pos = j % len(text)
                letter = text[pos]
                j += 1
                if j == len(text) and not repeat:
                    return
                # add_spiral_letter works in degrees rather than radians
                degrees = a / (2*math.pi) * 360 + 90
                family = 'CNC Vector' # good machine font
                # family = 'CutlingsGeometric' # spaces too big!
                # family = 'CutlingsGeometricRound' # spaces too big!
                # family = 'HersheyScript1smooth' # good "handwriting" font
                # family = 'Stymie Hairline' # a bit cutsey, but ok
                r_use = r + radial_adjust
                (w, h) = self.add_spiral_letter(letter, fontsize, centre, r_use, degrees, family=family, container=container)
                
                # FUDGE FACTOR TO SPREAD THINGS OUT A LITTLE, GIVEN ROTATION
                fudge_factor = 1.2
                
                segments_to_next_letter = int(w * fudge_factor / c_size)
                i = 0

    @staticmethod
    def rotate_about(point, centre, a):

        c = math.cos(a)
        s = math.sin(a)
        dx = point[0] - centre[0]
        dy = point[1] - centre[1]
        x = c * dx - s * dy
        y = c * dy + s * dx
        return (centre[0] + x, centre[1] + y)

    def make_rotated_polyline(self, points, centre, n, phase_add=0):
    
        all_points = []
        for ih in range(0, n):
            a = 2 * math.pi * (ih + phase_add) / n
            rot_points = [StandardDrawing.rotate_about(x, centre, a) for x in points]
            all_points.append(rot_points)
        return all_points
      
    def add_rotated_polyline(self, points, centre, n, phase_add=0, stroke=None, container=None):

        a = self.make_rotated_polyline(points, centre, n, phase_add)
        for rot_points in a:
            self.add_polyline(rot_points, stroke=stroke, container=container)
      
    @staticmethod
    def scale_x(points, factor):
    
        min_x = min(p[0] for p in points)
        max_x = min(p[0] for p in points)
        mid_x = (min_x + max_x) / 2
        return [(mid_x + (p[0] - mid_x) * factor, p[1]) for p in points]
      
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

class ShapeFiller:

    def __init__(self, shapes):
        self.unrotated_shapes = shapes

    # "Clever" plotting of crossings
    # Aims to keep as many connected regions going as possible - think it's pretty much optimal from that standpoint
    # Could try to reorder to get optimal TSP type path between sections but won't really make much difference to time
    def get_paths(self, row_width, angle=0):
    
        shapes = []
        for unrotated_shape in self.unrotated_shapes:
            shapes.append([StandardDrawing.rotate_about(x, (0,0), angle) for x in unrotated_shape])
    
        # scan all y-lines in range and get the crossing points
        y_min = min([min([p[1] for p in shape]) for shape in shapes])
        y_max = max([max([p[1] for p in shape]) for shape in shapes])
        y = y_min
        all_crossings = []
        while y <= y_max:
            all_crossings.append((y, ShapeFiller.get_crossings(shapes, y)))
            y += row_width
        n_scans = len(all_crossings)
            
        # sanity check - we should never have an odd number of crossings for any scan line
        for crossings in all_crossings:
            if len(crossings[1]) % 2 != 0:
                raise Exception(f'y-value {crossings[0]} has odd number of crossings: {len(crossings[1])}')

        # each pair of crossings is a line at our current y-level
        # how many connected sections can we keep on the go at once - this is the maximum number
        # of separate plotted regions for any scan line
        max_num_crossings = max([len(crossings[1]) for crossings in all_crossings])
        num_paths = int(max_num_crossings / 2)
        # print(f'num_paths={num_paths}')        

        # these are the points we will actually plot
        # it's a list of polylines
        all_paths = []
 
        path_states = [{'path': [], 'c_prev': None, 'connected': False} for i in range(0, num_paths)]
        
        # Take one scan line at a time, trying to connect up as many regions to the prevous scan line
        # as possible at each step.
        for ix_scan in range(0, n_scans):

            # This scan line's crossings
            crossings = all_crossings[ix_scan]
            y_for_scan = crossings[0]

            # print(f'crossings: {len(crossings[1])}')
            # print(f'crossings: {crossings[1]}')

            # To start with, no paths have been connected
            for ix_path in range(0, num_paths):
                path_states[ix_path]['connected'] = False

            # For each path in this scan line, try to hook up with the previous scan line
            for ix_path in range(0, num_paths):
            
                # Skip if we don't have anything in this section for this scan line
                if len(crossings[1]) < 2 * (ix_path + 1):
                    continue

                # Get the start and end of our crossing segment
                # Each crossing has x, ix_shape and indexes into the shape ix_s, ix_e
                c_s = crossings[1][2 * ix_path]
                c_e = crossings[1][2 * ix_path + 1]
                
                # Try to hook up with a preceding, unconnected path
                # If we can hook up, then we "claim" that path, swapping it into our index and marking it as connected
                # and appending our path to it
                for ix_prev_path in range(0, num_paths):
                    prev_path_state = path_states[ix_prev_path]
                    # This path is already connected so is not available for further connections at this scan line
                    if prev_path_state['connected']:
                        continue
                    # This path didn't have anything in the previous scan line so we can't connect to it
                    if prev_path_state['c_prev'] == None:
                        continue
                    # Try to connect to the previous scan line - can we reach either of our two crossing points by
                    # going around the shape that the previous line ended on, without y decreasing?
                    c_prev = prev_path_state['c_prev']
                    connection = ""
                    if ShapeFiller.is_on_continuation_of(shapes, c_s, c_prev):
                        # We can reach c_s by continuing around the shape from c_prev
                        connection = "s"
                    elif ShapeFiller.is_on_continuation_of(shapes, c_e, c_prev):
                        # We can reach c_e by continuing around the shape from c_prev
                        connection = "e"
                    # Successful connection
                    if connection != "":
                        # swap the section we've connected to, to move it over to our index
                        tmp = path_states[ix_path]
                        path_states[ix_path] = path_states[ix_prev_path]
                        path_states[ix_prev_path] = tmp
                        path_state = path_states[ix_path]
                        # mark as connected - this means another section won't be able to hook up
                        # I *think* that it's not possible to get mutiple hookups but am not 100% sure of this
                        # if it is impossible, perhaps we should instead throw an exception on multiple connections
                        path_state['connected'] = True
                        # add points in correct order - connected point first so we zigzag nicely
                        p_start = c_s if connection == "s" else c_e
                        p_end = c_e if connection == "s" else c_s
                        path_points = path_state['path']
                        path_points.append((p_start['x'], y_for_scan))
                        path_points.append((p_end['x'], y_for_scan))
                        # keep track of which pointt we ended with for this scan line and section
                        path_state['c_prev'] = p_end
                        # we've found a connection so no need to look at other sections for previous scan line
                        break

            # for ix_path in range(0, num_paths):
            #     path_state = path_states[ix_path]
            #     print(f'path[{ix_path}]: connected={path_state["connected"]}')

            # Deal with unconnected paths - here we want to flush anything not yet written
            # and start again (if there is anything on this scan line to start with)
            for ix_path in range(0, num_paths):

                # Skip if connected
                path_state = path_states[ix_path]
                if path_state['connected']:
                    continue

                # Flush any existing set
                if len(path_state['path']) > 0:
                    # print(f'path[{ix_path}]: flushing path {path_state["path"]}')
                    all_paths.append([x for x in path_state['path']])
                    path_state['path'] = []

                # If there's nothing for path #ix_path on this scan line, then mark that fact and continue
                if len(crossings[1]) < 2 * (ix_path + 1):
                    path_state['c_prev'] = None
                    continue
                    
                # Otherwise add points
                # print(f'path[{ix_path}]: starting new path')
                c_s = crossings[1][2 * ix_path]
                c_e = crossings[1][2 * ix_path + 1]
                path_state['path'].append((c_s['x'], y_for_scan))
                path_state['path'].append((c_e['x'], y_for_scan))
                path_state['c_prev'] = c_e

        # Flush all remaining sets (ongoing connected sections)
        for ix_path in range(0, num_paths):
            path_state = path_states[ix_path]
            if len(path_state['path']) > 0:
                all_paths.append(path_state['path'])

        # append closed loop for each shape = tidies things up at the boundaries
        for shape in shapes:
            a = [s for s in shape]
            a.append(a[0])
            all_paths.append(a)
            
        # now reverse the rotation
        returned_paths = []
        for rotated_path in all_paths:
            returned_paths.append([StandardDrawing.rotate_about(x, (0,0), -angle) for x in rotated_path])
            
        return returned_paths
        
    @staticmethod
    def is_on_continuation_of(shapes, c, c_prev):
        # "Can we reach c by continuing around the shape c_prev is on, without decreaing our y-value?"
        # 
        # Each crossing has x, shape, ix_s, ix_e
        # shape = index of shape : shape[shape][ix_vertex] is then [0, 1] for x, y
        # ix_s = vertex at one end of shape edge being crossed
        # ix_e = vertex at other end of shape edge being crossed
        # We traverse the shape starting at c_prev in non-decreating y-direction. If we hit c then there's a match
        
        # Must be the same shape!
        if c['shape'] != c_prev['shape']:
            return False
          
        # What we are trying to find
        curr_edge = [c['ix_s'], c['ix_e']]
        ix_shape = c_prev['shape']
        shape = shapes[ix_shape]
        # print(f"Searching for {curr_edge}: {shape[curr_edge[0]]}->{shape[curr_edge[1]]}")

        # Where we're starting from
        prev_ix1 = c_prev['ix_s']
        prev_ix2 = c_prev['ix_e']
        # print(f"Previous is {[prev_ix1, prev_ix2]}: {shape[prev_ix1]}->{shape[prev_ix2]}")
        if prev_ix1 in curr_edge and prev_ix2 in curr_edge:
            # print("Search: on same edge")
            return True
        
        # We're not on the same edge as c_prev. But are we on a subsequent one? Figure out which direction
        # to start looking in - need y to be increasing. Note that y cannot be the same on both ends because
        # we don't do crossings for such edges in get_crossings()
        prev_p1 = shape[prev_ix1]
        prev_p2 = shape[prev_ix2]
        y1 = prev_p1[1]
        y2 = prev_p2[1]
        if y1 == y2:
            raise Exception(f"We should not have a constant-Y edge with a crossing. ix_shape={ix_shape}, c_prev={prev_p1},{prev_pw})")
        inc = -1 if y1 > y2 else +1
        ix_start = prev_ix1 if y1 > y2 else prev_ix2

        # Search around the shape. We should terminate before we get back to the start, since y has to start
        # coming back down at some point.
        ix = ix_start
        y_curr = max(y1, y2)
        while True:
            ix_next = (ix + inc) % len(shape)
            # print(f"Search: {[ix, ix_next]} {shape[ix]}->{shape[ix_next]}")
            if ix_next == ix_start:
                raise Exception(f"We have gone all around a shape, which should be impossible. ix_shape={ix_shape}, c_prev={prev_p1},{prev_pw})")
            y_next = shape[ix_next][1]
            # y has started decreasing - give up
            if y_next < y_curr:
                # print("Search: not found")
                return False
            # we have reached our edge
            if ix in curr_edge and ix_next in curr_edge:
                # print("Search: found")
                return True
            # keep looking
            y_curr = y_next
            ix = ix_next

    # For a given y-value, get all the crossings with all shapes. There should be an even number of such crossings as we assume
    # the shapes are polygons. 
    # 
    # There is some subtlety involved in deciding what a crossing actually is:
    # * edges with a constant y-value don't yield crossings - we only consider edges where y is changing along the line
    # * if an edge is a "true" crossing, e.g. the point of crossing isn't at one end or the other, we always include it
    # * if an edge crosses at the start, we always include it
    # * if an edge crosses at the end, we only include it if the y-value is a peak or a trough at the crossing point
    # 
    # So if we have y at 50, and vectices A=(10, 40), B=(20, 50), C=(30, 40) there is a crossing for AB and for AC
    # But if we have y at 50, and vectices A=(10, 40), B=(20, 50), C=(30, 60) there is only a crossing for BC, we don't count AC
    # And if we have y at 50, and vectices A=(10, 50), B=(20, 50), C=(30, 50) there no crossiung for either, since both segments are constant in Y
    @staticmethod
    def get_crossings(shapes, y):
        hits = []
        for ix_shape in range(0, len(shapes)):
            shape = shapes[ix_shape]
            n_points = len(shape)
            for ix_s in range(0, n_points):
                ix_e = 0 if ix_s == n_points - 1 else ix_s + 1
                p_s = shape[ix_s]
                p_e = shape[ix_e]
                y_s = p_s[1]
                y_e = p_e[1]
                # print(f"shape:{ix_shape},ix_s:{ix_s}: ({p_s[0]},{p_s[1]})->({p_e[0]},{p_e[1]})")
                
                # We want to be a bit careful about *what* crossings we add!
                if y_e == y and y_s == y:
                    # We are wholly along the y-line - we ignore segments like this
                    hits = hits
                elif y_e == y:
                    # We are starting at the y-line - we always include a crossing in this case
                    hits.append({ 'x': p_e[0], 'shape': ix_shape, 'ix_s': ix_s, 'ix_e': ix_e  })
                elif y_s == y:
                    # We are ENDING at the y-line - here we need to be careful.
                    # 
                    # We may be crossing the y-line, or rebounding at it (a "corner"). If we are crossing then we 
                    # don't want to add a crossing record here as there will already be one for the case of the
                    # next segment starting at the y-line. Wo we need to figure out whether we're crossing the y-line,
                    # or forming a corner at it.
                    # 
                    # We look for the previous segment of the shape (ignoring all segments that are wholly along y) that started on y.
                    # There has to be one that is distinct from this segment as we know that this segment can't start at y, so if 
                    # nowhere else we will loop round and hit the segment after this one. We then see whether the y-line is being
                    # approached from the same direction both before and after it is hit: if so, then it's a corner (and we DO want
                    # to add this segment, else it's a crossing (and we DON'T want to add this segment).
                    ix_before_s = ix_s
                    while shape[ix_before_s][1] == y:
                        ix_before_s = n_points - 1 if ix_before_s == 0 else ix_before_s - 1
                    y_prev = shape[ix_before_s][1]
                    sign_prev = -1 if y_prev < y else +1
                    sign_next = -1 if y_e < y else +1
                    if sign_prev == sign_next:
                        hits.append({ 'x': p_s[0], 'shape': ix_shape, 'ix_s': ix_s, 'ix_e': ix_e  })
                elif (y_s < y and y_e > y) or (y_s > y and y_e < y):
                    # We are crossing the y-line - these segments always get added as a crossing point
                    x_s = p_s[0]
                    x_e = p_e[0]
                    x = x_s + (x_e - x_s) * (y - y_s) / (y_e - y_s)
                    hits.append({ 'x': x, 'shape': ix_shape, 'ix_s': ix_s, 'ix_e': ix_e  })
                        
        # sort by x-value - this helps when we are using a naive strategy for plotting
        # doubt if it makes any real difference for the more intelligent connection strategy we are now using by dfault.
        hits = sorted(hits, key=lambda hit: hit['x'])
        
        return hits
    
class EdgeHit:

    def __init__(self, x, ix_shape, ix_s, ix_e):
        self.x = x
        self.ix_shape
        self.ix_s = ix_s
        self.ix_e = ix_e


