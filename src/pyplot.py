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
import time

from bezier import *

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
    # Fills
    # * Moonlight: 0.2*width (0.12mm), and max GRBL speed of 1000
    # * Metallic: 0.4*width (0.24mm), and max GRBL speed of 2000
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
        return PenType('StaedtlerPigment05', False, 0.5, '0.35px', BWConverters.AverageIntensity, CMYKConverters.Unadjusted)

class StandardDrawing:

    def __init__(self, file='test.svg', pen_type=None):
    
        # Using viewBox="0 0 210 297" means we are plotting in mm so 25.4 units to the inch
        # Native SVG units are in PX - 96 to the inch
        # So the adjustment is 25.4/96 between the two
        # We need to use this when we are specifying measurements in other units - currently the only place we are doing this is text, where 
        # we are working in points - we multiply by the scale factor to plot this at the right size for our viewbox.
        self.dwg = svgwrite.Drawing(file, size=('210mm', '297mm'), viewBox="0 0 210 297") # height='210mm', width='297mm') # , viewBox="0 0 210 297")
        self.scale = 25.4/96
        
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

    @staticmethod
    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def default_fontsize(self, fontsize):
        if fontsize is None:
            return "8"
        return fontsize
        
    def add_polyline(self, points, stroke=None, container=None):
        container = self.default_container(container)
        stroke = self.default_stroke(stroke)
        container.add(self.dwg.polyline(points, stroke=stroke, stroke_width=self.pen_type.stroke_width, fill='none'))
        
    def add_polylines(self, polylines, stroke=None, container=None):
        polylines = StandardDrawing.sort_polylines(polylines)
        container = self.default_container(container)
        stroke = self.default_stroke(stroke)
        for polyline in polylines:
            container.add(self.dwg.polyline(polyline, stroke=stroke, stroke_width=self.pen_type.stroke_width, fill='none'))
        
    def add_layer(self, label):
        layer = self.inkscape.layer(label=label)
        self.dwg.add(layer)
        return layer

    def add_polygon(self, points, stroke=None, container=None):
        stroke = self.default_stroke(stroke)
        container = self.default_container(container)
        polygon = self.dwg.polygon(points, stroke=stroke, stroke_width=self.pen_type.stroke_width, fill='none')
        container.add(polygon)
        
    def add_polygons(self, a, stroke=None, container=None):
        stroke = self.default_stroke(stroke)
        container = self.default_container(container)
        for x in a:
            polygon = self.dwg.polygon(x, stroke=stroke, stroke_width=self.pen_type.stroke_width, fill='none')
            container.add(polygon)

    def make_square(self, pt, size):
        points = []
        points.append(pt)
        points.append((pt.x + size, pt.y))
        points.append((pt.x + size, pt.y + size))
        points.append((pt.x, pt.y + size))
        return points

    def add_square(self, pt_input, size, start_size=None, stroke=None, container=None):    
    
        pt = Point.From(pt_input)
        
        if start_size is None:
            points = self.make_square(pt, size)
            self.add_polygon(points, stroke, container)
            return
          
        diff = (size - start_size) / 2
        diff_pt = pt + Point(diff, diff)
        sf = ShapeFiller([self.make_square(diff_pt, start_size), self.make_square(pt, size)])
        paths = sf.get_paths(self.pen_type.pen_width * 0.2)
        self.add_polylines(paths, stroke, container)

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
        
    def get_circle_point(self, middle, radius, theta, x_scale=None):
        x_radius = radius if x_scale is None else radius * x_scale
        s = math.sin(theta)
        c = math.cos(theta)
        return (middle[0] + x_radius * s, middle[1] - radius * c)

    # Default circle granularity: divide into parts no bigger than the width of the pen
    def default_circle_path_count(self, r):
        return int(2 * math.pi * r / self.pen_type.pen_width) + 1

    def make_circle(self, middle, r, n=None, stroke=None, x_scale=None):
        n = self.default_circle_path_count(r) if n is None else n
        stroke = self.default_stroke(stroke)
        points = []
        for i in range(0, n):    
            angle = 2 * math.pi * i / n
            p = self.get_circle_point(middle, r, angle, x_scale)
            points.append( p )
        return points

    def add_circle(self, middle, r, n=None, stroke=None, container=None):
        points = self.make_circle(middle, r, n, stroke)
        self.add_polygon(points, stroke=stroke, container=container)

    def make_dot(self, centre, radius, r_start=None, xy_func=None):

        pen_width = self.pen_type.pen_width

        points = []
        a = 0 # starting angle
        r_per_circle = pen_width * 0.2 # 1/5 pen width
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
                    
    def make_surface(self, top_left, x_size, y_size, z_function, projection_angle=None):

        top_left = Point.From(top_left)
        
        # can render texture with z-function applied by preserving x, and doing y-out = y * cos(a) + z * sin(a) with a the viewing angle?  
        projection_angle = math.pi * 3 /8 if projection_angle is None else projection_angle
        min_adj_y_for_x = {}
        all_points = []
        for y in range(0, y_size + 1, 5)[::-1]:
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
                points.append(top_left + Point(x, y_adj))
            all_points.append(points)
        return all_points

    def add_surface(self, top_left, x_size, y_size, z_func, stroke=None, container=None):
    
        all_points = self.make_surface(top_left, x_size, y_size, z_func)
        for points in all_points:
            self.add_polyline(points, stroke=stroke, container=container)

    def text_bound(self, text, fontsize=14, family='Arial'):

        # Don't import cairo unless we need it (for text placement that needs to size letters)
        import cairo
        
        surface = cairo.SVGSurface('undefined.svg', 210*72/2.54, 290*72/2.54)
        surface.set_document_unit(cairo.SVGUnit.PT)
        cr = cairo.Context(surface)
        cr.select_font_face(family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        
        # Adjust the font size we actually use based on our overall scaling factor
        cr.set_font_size(fontsize * self.scale)
        
        # cr.text_path(text)   
        # path = cr.copy_path()
        # print(path)
        
        return cr.text_extents(text)

    def text_bound_letter(self, letter, fontsize, family):
    
        ext1 = self.text_bound(f"X{letter}X", fontsize, family)
        ext2 = self.text_bound(f"XX", fontsize, family)
        ext3 = self.text_bound(letter, fontsize, family)
        w = ext1.width - ext2.width
        return (w, ext3.height)
        return (w, ext3.height)
        
    # Why not use svg's drawing.text()? There are two main advantages to writing out the paths
    # * No longer need to use Object->Path to print things out in Inkscape
    # * Far more potential options for warping/manipulating the shape of letters, and using paths to bound fills
    def make_text(self, text, base_position, fontsize, family='Arial', transform=None):

        base_position = Point.From(base_position)
        fontsize = self.default_fontsize(fontsize)
        transform = (lambda x: x) if transform is None else transform

        # Don't import cairo unless we need it (for text placement that needs to size letters)
        import cairo
        
        surface = cairo.SVGSurface('undefined.svg', 210*72/2.54, 290*72/2.54)
        surface.set_document_unit(cairo.SVGUnit.PT)
        cr = cairo.Context(surface)
        cr.select_font_face(family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        
        # Adjust the font size we actually use based on our overall scaling factor
        cr.set_font_size(fontsize * self.scale)
        cr.text_path(text)   
        path = cr.copy_path()

        # Assemble a svgwrite path from our Cario path
        
        svgpath = svgwrite.path.Path()
        all_polylines = []
        curr_polyline = []
        prev_relative_position = None
        pending_splines = []
        #for type, points in path:
        #    print(type,points)
        for type, points in path:
            if type != cairo.PATH_CURVE_TO:
                if len(pending_splines) > 0:
                    # convert any pending splines to small enough subsections that we can plot them as stright lines
                    # tolerance is (control point dist / line dist)
                    a = bezier_subdivide(prev_relative_position, pending_splines, 0.01)
                    for small_spline in a:
                        x, y = small_spline[2]
                        pt = Point(x,y)
                        prev_relative_position = pt
                        curr_polyline.append(base_position + pt)
                    pending_splines = []
                    
            if type == cairo.PATH_MOVE_TO:
                if len(curr_polyline) > 0:
                    raise Exception(f"Found PATH_MOVE_TO but not at start of path")
                x, y = transform(points)
                pt = Point(x,y)
                prev_relative_position = pt
                curr_polyline.append(base_position + pt)

            elif type == cairo.PATH_LINE_TO:
                if len(curr_polyline) == 0:
                    raise Exception(f"Found PATH_LINE_TO but no prior MOVE_TO in path")
                x, y = transform(points)
                pt = Point(x,y)
                prev_relative_position = pt
                curr_polyline.append(base_position + pt)

            elif type == cairo.PATH_CURVE_TO:
                if len(curr_polyline) == 0:
                    raise Exception(f"Found PATH_LINE_TO but no prior MOVE_TO in path")
                x1, y1, x2, y2, x3, y3 = points
                pending_splines.append([transform((x1,y1)), transform((x2,y2)), transform((x3,y3))])

            elif type == cairo.PATH_CLOSE_PATH:
                all_polylines.append(curr_polyline)
                curr_polyline = []
                prev_relative_position = None
                pending_splines = []
    
        return all_polylines
         
    # Why not use svg's drawing.text()? There are two main advantages to writing out the paths
    # * No longer need to use Object->Path to print things out in Inkscape
    # * Far more potential options for warping/manipulating the shape of letters, and using paths to bound fills
    def add_text(self, text, position, fontsize, family='Arial', container=None, stroke=None, transform=None):

        stroke = self.default_stroke(stroke)
        container = self.default_container(container)
        fontsize = self.default_fontsize(fontsize)
        
        all_polylines = self.make_text(text, position, fontsize, family, transform)
                
        # Add into the container
        for polyline in all_polylines:
            container.add(self.dwg.polygon(polyline, stroke=stroke, stroke_width=self.pen_type.stroke_width, fill='none'))

        return self.text_bound(text, fontsize, family)

    def make_spiral_letter(self, letter, fontsize, spiral_centre, radius, angle=0, family='Arial'):
        
        spiral_centre = Point.From(spiral_centre)
        
        # unadjusted y is at bottom left (high y, low x)

        (w,h) = self.text_bound_letter(letter, fontsize, family)
        
        letter_position = (spiral_centre.x, spiral_centre.y - radius)
        
        # transform is applied to letter BEFORE we translate by letter_position
        # e.g. it's relative to (0,0)
        transform = lambda x: StandardDrawing.rotate_about(x, (0, radius), angle)
        
        all_polylines = self.make_text(letter, letter_position, fontsize, family=family, transform=transform)
        
        return ((w, h), all_polylines)

    def add_spiral_letter(self, letter, fontsize, spiral_centre, radius, angle=0, family='Arial', container=None, stroke=None):
    
        stroke = self.default_stroke(stroke)
        container = self.default_container(container)

        ((w, h), all_polylines) = self.make_spiral_letter(letter, fontsize, spiral_centre, radius, angle=angle, family=family)
        
        for polyline in all_polylines:
            container.add(self.dwg.polygon(polyline, stroke=stroke, stroke_width=self.pen_type.stroke_width, fill='none'))
        
        return (w, h)

    def make_spiral_text(self, centre, scale, radial_adjust=0, repeat=False, text=None, fontsize=6, family='CNC Vector'):

        centre = Point.From(centre)
        
        points = []
        points.append(centre)
        r = 0.5 # initial radius
        a = 0 # starting angle
        c_size = self.pen_type.pen_width # constant distance travelled: something like the nib width is probably best
        r_per_circle = fontsize * self.scale
        
        i = 0
        # Let the spiral get going before we start plotting
        segments_to_next_letter = int(fontsize / c_size) + 1

        # Burroughs quote
        if text is None:
            text = "In the City Market is the Meet Café. Followers of obsolete, unthinkable trades doodling in Etruscan, addicts of drugs not yet synthesized, pushers of souped-up harmine, junk reduced to pure habit offering precarious vegetable serenity, liquids to induce Latah, Tithonian longevity serums, black marketeers of World War III, excusers of telepathic sensitivity, osteopaths of the spirit, investigators of infractions denounced by bland paranoid chess players, servers of fragmentary warrants taken down in hebephrenic shorthand charging unspeakable mutilations of the spirit, bureaucrats of spectral departments, officials of unconstituted police states, a Lesbian dwarf who has perfected operation Bang-utot, the lung erection that strangles a sleeping enemy, sellers of orgone tanks and relaxing machines, brokers of exquisite dreams and memories..."

        all_polylines = []

        # draw until we've hit the desired size
        j = 0
        while r <= scale:
            # print(r, scale)
        
            # Archimedian spiral with constant length of path
            a_inc = c_size / r
            a += a_inc
            r += r_per_circle * a_inc / (2 * math.pi)
            
            i += 1
            if i == segments_to_next_letter:
                pos = j % len(text)
                letter = text[pos]
                # family = 'CNC Vector' # good machine font
                # family = 'CutlingsGeometric' # spaces too big!
                # family = 'CutlingsGeometricRound' # spaces too big!
                # family = 'HersheyScript1smooth' # good "handwriting" font
                # family = 'Stymie Hairline' # a bit cutsey, but ok
                r_use = r + radial_adjust
                ((w, h), polylines) = self.make_spiral_letter(letter, fontsize, centre, r_use, a + math.pi/2, family=family)
                for polyline in polylines:
                    all_polylines.append(polyline)
                
                # FUDGE FACTOR TO SPREAD THINGS OUT A LITTLE, GIVEN ROTATION
                fudge_factor = 1.2
                
                segments_to_next_letter = int(w * fudge_factor / c_size + 0.5)
                i = 0
                
                j += 1
                if j == len(text) and not repeat:
                    return all_polylines
                    
        return all_polylines
        
    def add_spiral_text(self, centre, scale, radial_adjust=0, repeat=False, text=None, fontsize=24, family='CNC Vector', container=None, stroke=None):

        stroke = self.default_stroke(stroke)
        container = self.default_container(container)

        polylines = self.make_spiral_text(centre, scale, radial_adjust, repeat, text, fontsize, family)
        for polyline in polylines:
            container.add(self.dwg.polygon(polyline, stroke=stroke, stroke_width=self.pen_type.stroke_width, fill='none'))
 
    def make_spiral(self, centre, scale, r_per_circle=None, r_initial=None, direction=1):

        centre = Point.From(centre)
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
            pt = centre + Point(c, s) * r
            
            points.append(pt)
            
        return points

    def add_spiral(self, centre, scale, r_per_circle=None, r_initial=None, container=None, stroke=None, direction=1):

        points = self.make_spiral(centre, scale, r_per_circle, r_initial, direction)
        self.add_polyline(points, stroke, container)

    @staticmethod
    def add_wiggle(points, new_point, line_mult):    

        prev = points[-1]
        half = (new_point - prev) * 0.5
        mid = prev + half
        size = line_mult / 2
        half_r = Point(-half.y, half.x) * size
        p1 = mid + half_r
        p2 = mid - half_r
        points.append(p1)
        points.append(p2)
        points.append(new_point)

    def make_image_spiral_single(self, file, centre, scale, r_factor_func = None, colour = False, cmy_index=0, x_scale=1):

        centre = Point.From(centre)

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
        img_centre = Point(int(h/2), int(w/2))
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
            new_point = centre + Point(c * x_scale, s) * (r * r_factor)

            # image location (note x/y swap)
            ix = int(img_centre[0] + img_size * (new_point.y - centre[1]) / scale)
            iy = int(img_centre[1] + img_size * (new_point.x - centre[0]) / scale)
            
            pt = image[ix, iy]
            
            # image is BGR - pass in RGB
            intense = intensity_converter(pt[2], pt[1], pt[0])
            if self.pen_type.is_black:
                intense = 1.0 - intense
                
            shade = intense * mult * r_factor

            # "wiggle" on our way from "prev" to "new" with a width propertional to the intensity
            StandardDrawing.add_wiggle(points, new_point, shade)

        return points

    def image_spiral_single(self, container, file, centre, scale, stroke = None, r_factor_func = None, colour = False, cmy_index=0, x_scale=1):

        points = self.make_image_spiral_single(file, centre, scale, r_factor_func, colour, cmy_index, x_scale)
    
        self.add_polyline(points, stroke=stroke, container=container)

    def image_spiral_cmyk(self, file, centre, scale):

        # C is layer 1
        # M is layer 2
        # Y is layer 3
        for cmy_index in [0, 1, 2]:
            layer = self.add_layer(f"{cmy_index + 1}-cmy-layer")
            stroke_rgb = [255, 255, 255]
            stroke_rgb[cmy_index] = 0
            self.image_spiral_single(layer, file, centre, scale, stroke=svgwrite.rgb(stroke_rgb[0], stroke_rgb[1], stroke_rgb[2], '%'), colour=True, cmy_index=cmy_index)

    @staticmethod
    def rotate_about(point, centre, a):

        point = Point.From(point)
        centre = Point.From(centre)
        c = math.cos(a)
        s = math.sin(a)
        diff = point - centre
        dx = point[0] - centre[0]
        dy = point[1] - centre[1]
        rot_diff = Point(c * diff.x - s * diff.y, c * diff.y + s * diff.x)
        return centre + rot_diff

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
      
    def fill_in_paths(self, path_gen_func, width_mult=0.4):

        pen_width = self.pen_type.pen_width
        
        path0 = path_gen_func(0.0)
        path1 = path_gen_func(1.0)
        path0.extend(path1[::-1])
        
        angle = 0
        
        all_paths = []
        sf = ShapeFiller([path0])
        for path in sf.get_paths(self.pen_type.pen_width * width_mult, angle=angle):
            all_paths.extend(path)
        return all_paths

    def make_word_square(self, position, fontsize, family, square, angle=None):

        all_polylines = []
        
        n = len(square)
        max_width = 0
        max_height = 0
        for letter in square[0]:
            ext = self.text_bound(letter, fontsize, family)
            max_width = max(max_width, ext.width)
            max_height = max(max_height, ext.height)
        max_text_side = max(max_width, max_height)
        square_size = max_text_side + 2
        use_position = Point(position[0], position[1] + square_size)
        for r in range(0, len(square)):
            for c in range(0, len(square[r])):
                letter = square[r][c]
                ext = self.text_bound(letter, fontsize, family)
                pos_square_centre = use_position + Point((c+0.5) * square_size, (r+0.5) * square_size)
                pos_square_text = pos_square_centre - Point(ext.width/2, ext.height/2)
                text_paths = self.make_text(letter, pos_square_text, fontsize=fontsize, family=family)
                sf = ShapeFiller(text_paths)
                filled_text_paths = sf.get_paths(self.pen_type.pen_width / 5)
                for p in filled_text_paths:
                    all_polylines.append(p)
                    
        width = fontsize / 24 * 2
        topleft = use_position + Point(ext.x_bearing, ext.y_bearing)
        shape1 = self.make_square(topleft - Point(width/4, width/4), len(square)*square_size + width/2)
        shape2 = self.make_square(topleft - Point(width/2, width/2), len(square)*square_size + width)
        sf = ShapeFiller([shape1, shape2])
        paths = sf.get_paths(self.pen_type.pen_width / 5 * 2)
        all_polylines.extend(paths)
        
        centre = use_position + Point(1, 1) * n * square_size/2
        
        angle = 0 if angle is None else angle
        rot_polylines = []
        for path in all_polylines:
            rot_path = [StandardDrawing.rotate_about(x, centre, angle) for x in path]
            rot_polylines.append(rot_path)
        
        return rot_polylines

    @staticmethod
    def make_thick_line(line_start, new_points, total_thickness_start, total_thickness_end, row_width):

        line_end = new_points[-1]
        thickness_start = total_thickness_start / 2
        thickness_end = total_thickness_end / 2
        
        thick_line_points = []

        # Get distances, and normalised (length-1) vectors at right angles to our line segments
        total_dist = 0
        total_dists = []
        norm_rs = []
        prev = line_start
        for pt in new_points:
            diff = pt - prev
            diff_r = Point(diff.y, -diff.x)
            dist_diff = diff_r.dist()
            norm_diff_r = diff_r / dist_diff
            norm_rs.append(norm_diff_r)
            total_dist += dist_diff
            total_dists.append(total_dist)
        norm_r_start = norm_rs[0]
        norm_r_end = norm_rs[-1]
            
        # Get fractional distances of endpoints
        # This is used to interpolate between thickness_start and thickness_end
        fract_dists = [dist / total_dist for dist in total_dists]

        # Add lines around the central line
        max_thickness = max(thickness_start, thickness_end)
        thickness_adj = 0
        while (max_thickness - thickness_adj) > 0.1:

            # Get adjusted range (floored at zero)
            adj_thickness_start = max(0, thickness_start - thickness_adj)
            adj_thickness_end = max(0, thickness_end - thickness_adj)
            
            # Get thicknesses at endpoints - theoretically loglinear interp might make most sense but save that for when/if we
            # plot something where this makes a visible difference
            thicknesses = [adj_thickness_start + (adj_thickness_end - adj_thickness_start) * fract_dist for fract_dist in fract_dists]
            
            # Combine our points, right-angle-vectors and thicknesses
            points_norms_and_thicknesses = [x for x in zip(new_points, norm_rs, thicknesses)]
        
            # Start off to the side of the starting point
            thick_line_points.append(line_start + norm_r_start * adj_thickness_start)
            # Draw a line to the end, along the same side
            thing1 = [pt + norm_r * thickness for (pt, norm_r, thickness) in points_norms_and_thicknesses]
            thick_line_points.extend(thing1)
            # Draw a line back to the start along the opposite side
            thing2 = [pt - norm_r * thickness for (pt, norm_r, thickness) in points_norms_and_thicknesses]
            thick_line_points.extend(thing2[::-1])
            thick_line_points.append(line_start - norm_r_start * adj_thickness_start)

            # Reduce thickness - something adjusted by pen width would probably be best here
            thickness_adj += row_width
        
        # Add the central line
        thick_line_points.append(line_start)
        thick_line_points.extend([x for x in new_points])
        
        return thick_line_points

    def make_branch_recurse(self, all_lines, ix, pos, line, cut, a_disp, depth_remaining, thickness_mm):

        def gen_curved_line(start, end):

            diff = end - start
            d = diff.dist()
            d1 = d / 5
            d2 = d / 8
            
            t1 = 1/3
            control1 = start + diff * t1 + Point(rand_1(), rand_1()) * d1
            t2 = 2/3
            control2 = start + diff * t2 + Point(rand_1(), rand_1()) * d2
            
            return [Point.From(b[2]) for b in bezier_subdivide(start, [[control1, control2, end]], 0.01)]
            
        def rand_1():

            return 2 * (random() - 0.5)

        row_width = self.pen_type.pen_width / 5
        
        new_pos = pos + line
        curved_line = gen_curved_line(pos, new_pos)
        # print(all_lines)
        curr_path = all_lines[ix]
        paths = StandardDrawing.make_thick_line(curr_path[-1], curved_line, thickness_mm, thickness_mm*cut, row_width)
        curr_path.extend(paths)
        # curr_path.extend(curved_line)
        # print(all_lines)
        # raise Exception("foo")

        if depth_remaining == 0:
            return
            
        line_dist = line.dist()
        new_norm_direction = (curr_path[-1] - curr_path[-2]).norm()
        
        scaled_dist = cut * line_dist
        new_line = new_norm_direction * scaled_dist
        new_thickness = thickness_mm * cut
        
        # do the higher-index branch first so our indexing doesn't get messed up!
        all_lines[ix+1:ix+1] = [[new_pos]]
        self.make_branch_recurse(all_lines, ix+1, new_pos, StandardDrawing.rotate_about(new_line, Point.Origin(), -a_disp), cut, a_disp, depth_remaining - 1, new_thickness)
        # now go further along the ix-branch
        self.make_branch_recurse(all_lines, ix, new_pos, StandardDrawing.rotate_about(new_line, Point.Origin(), a_disp), cut, a_disp, depth_remaining - 1, new_thickness)

    def make_branch(self, pos_start, line, cut, a_disp, max_depth, thickness_mm):

        branch_polylines = [[pos_start]]
        self.make_branch_recurse(branch_polylines, 0, pos_start, line, cut, a_disp, max_depth, thickness_mm)
        return branch_polylines
        
    @staticmethod
    def sort_polylines(polylines_input):

        # Convert tuples to Points
        polylines = [[Point.From(pt) for pt in polyline] for polyline in polylines_input]
        
        i_start = 0
        unsorted = [x for x in polylines]
        sorted = [unsorted[i_start]]
        del unsorted[i_start:i_start+1]
        while len(unsorted) > 0:
            e = sorted[-1][-1]
            # print(e)
            is_fwd = True
            min_dist = 1000000
            min_ix = 0
            for i in range(0, len(unsorted)):
                p = unsorted[i]
                dist_s = (e - p[0]).dist()
                dist_e = (e - p[-1]).dist()
                if dist_e < min_dist:
                    min_ix = i
                    is_fwd = False
                    min_dist = dist_e
                if dist_s < min_dist:
                    min_ix = i
                    is_fwd = True
                    min_dist = dist_s
                    
            best = unsorted[min_ix]
            sorted.append(best if is_fwd else best[::-1])
            del unsorted[min_ix:min_ix+1]
    
        return sorted

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

    tot_split = 0
    tot_split2 = 0
    tot_split3 = 0
    
    class PathState:

        def __init__(self):
            self.path = []
            self.c_prev = None
            self.connected = False
        
    class EdgeHit:

        def __init__(self, x, ix_shape, ix_s, ix_e):
            self.x = x
            self.ix_shape = ix_shape
            self.ix_s = ix_s
            self.ix_e = ix_e
            
        def __str__(self):
            return f"x={self.x}, ix_shape={self.ix_shape}, ix_s={self.ix_s}, ix_e={self.ix_e}"

    class Limits:
    
        def __init__(self, min_x, min_y, max_x, max_y):
            self.min_x = min_x
            self.min_y = min_y
            self.max_x = max_x
            self.max_y = max_y

    def __init__(self, shapes_input):
        # Convert tuples to Point
        shapes = [[Point.From(pt) for pt in shape] for shape in shapes_input]
        self.unrotated_shapes = shapes
        self.shape_limits = [ShapeFiller.Limits(min([pt.x for pt in shape]), min(pt.y for pt in shape), max([pt.x for pt in shape]), max(pt.y for pt in shape)) for shape in shapes]
        self.min_x = min(limit.min_x for limit in self.shape_limits)
        self.min_y = min(limit.min_y for limit in self.shape_limits)
        self.max_x = max(limit.max_x for limit in self.shape_limits)
        self.max_y = max(limit.max_y for limit in self.shape_limits)
        self.tot = 0

    def add_shape(self, shape):
        shape = [Point.From(pt) for pt in shape]
        self.unrotated_shapes.append(shape)
        limit = ShapeFiller.Limits(min([pt.x for pt in shape]), min(pt.y for pt in shape), max([pt.x for pt in shape]), max(pt.y for pt in shape))
        self.shape_limits.append(limit)
        self.min_x = min(limit.min_x, self.min_x)
        self.min_y = min(limit.min_y, self.min_y)
        self.max_x = max(limit.max_x, self.max_x)
        self.max_y = max(limit.max_y, self.max_y)

    # "Clever" plotting of crossings
    # Aims to keep as many connected regions going as possible - think it's pretty much optimal from that standpoint
    # Could try to reorder to get optimal TSP type path between sections but won't really make much difference to time
    def get_paths(self, row_width, angle=0):
    
        shapes = []
        for unrotated_shape in self.unrotated_shapes:
            shapes.append([StandardDrawing.rotate_about(x, Point.Origin(), angle) for x in unrotated_shape])
    
        # scan all y-lines in range and get the crossing points
        y_min = min([min([p.y for p in shape]) for shape in shapes])
        y_max = max([max([p.y for p in shape]) for shape in shapes])
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
 
        path_states = [ShapeFiller.PathState() for i in range(0, num_paths)]
        
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
                path_states[ix_path].connected = False

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
                    if prev_path_state.connected:
                        continue
                    # This path didn't have anything in the previous scan line so we can't connect to it
                    if prev_path_state.c_prev == None:
                        continue
                    # Try to connect to the previous scan line - can we reach either of our two crossing points by
                    # going around the shape that the previous line ended on, without y decreasing?
                    c_prev = prev_path_state.c_prev
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
                        path_state.connected = True
                        # add points in correct order - connected point first so we zigzag nicely
                        p_start = c_s if connection == "s" else c_e
                        p_end = c_e if connection == "s" else c_s
                        path_points = path_state.path
                        path_points.append((p_start.x, y_for_scan))
                        path_points.append((p_end.x, y_for_scan))
                        # keep track of which pointt we ended with for this scan line and section
                        path_state.c_prev = p_end
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
                if path_state.connected:
                    continue

                # Flush any existing set
                if len(path_state.path) > 0:
                    # print(f'path[{ix_path}]: flushing path {path_state["path"]}')
                    all_paths.append([x for x in path_state.path])
                    path_state.path = []

                # If there's nothing for path #ix_path on this scan line, then mark that fact and continue
                if len(crossings[1]) < 2 * (ix_path + 1):
                    path_state.c_prev = None
                    continue
                    
                # Otherwise add points
                # print(f'path[{ix_path}]: starting new path')
                c_s = crossings[1][2 * ix_path]
                c_e = crossings[1][2 * ix_path + 1]
                path_state.path.append((c_s.x, y_for_scan))
                path_state.path.append((c_e.x, y_for_scan))
                path_state.c_prev = c_e

        # Flush all remaining sets (ongoing connected sections)
        for ix_path in range(0, num_paths):
            path_state = path_states[ix_path]
            if len(path_state.path) > 0:
                all_paths.append(path_state.path)

        # append closed loop for each shape = tidies things up at the boundaries
        for shape in shapes:
            a = [s for s in shape]
            a.append(a[0])
            all_paths.append(a)
            
        # now reverse the rotation
        returned_paths = []
        for rotated_path in all_paths:
            returned_paths.append([StandardDrawing.rotate_about(x, Point.Origin(), -angle) for x in rotated_path])
            
        return returned_paths
        
    def is_inside(self, pt, any=False):

        # Gross bounds check
        if pt.x <= self.min_x or pt.y <= self.min_y or pt.x >= self.max_x or pt.y >= self.max_y:
            return False

        inside_count = 0
        
        # We exclude anything actually *on* an edge - otherwise we 
        # are "inside" if we are inside an odd number of shapes. We are inside 
        # a given shape if we have an odd number of crossings as we increase x
        for ix_shape in range(0, len(self.unrotated_shapes)):
        
            shape = self.unrotated_shapes[ix_shape]
            shape_limit = self.shape_limits[ix_shape]

            # Short-circuit if we know we're outside shape bounds
            if pt.y > shape_limit.max_y:
                continue
            if pt.y < shape_limit.min_y:
                continue
            
            crossings = ShapeFiller.get_crossings([shape], pt.y)
                
            counts = {}
            hits = {}
            for crossing in crossings:
                if crossing.x == pt.x:
                    hits[crossing.ix_shape] = True
                elif crossing.x > pt.x:
                    if not crossing.ix_shape in counts:
                        counts[crossing.ix_shape] = 1
                    else:
                        counts[crossing.ix_shape] += 1
            
            for ix_shape in counts:
                if ix_shape not in hits:
                    if counts[ix_shape] % 2 == 1:
                        if any:
                            return True
                        inside_count += 1;
                    
        return inside_count % 2 == 1
        
    timeTotal1 = 0
    timeTotal2 = 0

    def clip(self, polylines_input, union=False, inverse=False):

        (t1, t2, t3) = (ShapeFiller.tot_split, ShapeFiller.tot_split2, ShapeFiller.tot_split3)
        tStart = time.perf_counter()
    
        # Convert tuples to Point
        polylines = [[Point.From(pt) for pt in polyline] for polyline in polylines_input]
        
        #print("pre-split shapes")
        #print(self.unrotated_shapes)
        #print("pre-split")
        #print(polylines)
        split_polylines = self.split_polylines(polylines)
        #print("post-split")
        #print(split_polylines)
        
        tEnd1 = time.perf_counter()
        ShapeFiller.timeTotal1 += (tEnd1 - tStart)
        
        #print("start")
        clipped_polylines = []
        for polyline in split_polylines:
            path = []
            s = polyline[0]
            for e in polyline[1:]:
            
                # are we going to include this edge?
                m = (s + e) / 2
                include = not self.is_inside(m, union)
                if inverse:
                    include = not include
                #print(f"s={s}, e={e}, m={m}, include={include}")
                    
                if include:
                    # add to pending path
                    if len(path) == 0:
                        path.append(s)
                    path.append(e)
                    #print(path)
                else:
                    # commit any pending path
                    if len(path) > 0:
                        clipped_polylines.append(path)
                        path = []
                s = e
                
            # commit any pending path
            if len(path) > 0:
                clipped_polylines.append(path)
                path = []
                
        tEnd2 = time.perf_counter()
        ShapeFiller.timeTotal2 += (tEnd2 - tEnd1)
                
        print("clip.split", ShapeFiller.tot_split - t1, ShapeFiller.tot_split2 - t2, ShapeFiller.tot_split3 - t3, ShapeFiller.timeTotal1, ShapeFiller.timeTotal2)
            
        return clipped_polylines

    def split_polylines(self, polylines):
        return [self.split_polyline(p) for p in polylines]
            
    def split_polyline(self, polyline):
    
        s = polyline[0]
        path = [s]
        for e in polyline[1:]:
            #print("split_edge_endpoints", s, e)
            path.extend(self.split_edge_endpoints(s, e))
            s = e
        #if len(polyline) != len(path):
            #print(f"splitting polyline length {len(polyline)}->{len(path)} starting at {polyline[0]}")
            
        return path
        
    def split_edge_endpoints(self, s, e):
    
        split_edges = [(s, e)]
        i = 0
        while i < len(split_edges):

            # Get edge details
            edge = split_edges[i]
            edge_s = edge[0]
            edge_e = edge[1]
            edge_limits = ShapeFiller.Limits(min(edge_s[0], edge_e[0]), min(edge_s[1], edge_e[1]), max(edge_s[0], edge_e[0]), max(edge_s[1], edge_e[1]))
            
            # Check against overall bound
            if edge_limits.max_x < self.min_x:
                i += 1
                continue
            if edge_limits.min_x > self.max_x:
                i += 1
                continue
            if edge_limits.max_y < self.min_y:
                i += 1
                continue
            if edge_limits.min_y > self.max_y:
                i += 1
                continue
        
            for ix_shape in range(0, len(self.unrotated_shapes)):
            
                ShapeFiller.tot_split += 1
                shape = self.unrotated_shapes[ix_shape]
                shape_limits = self.shape_limits[ix_shape]
                
                # Minimise full intersection checks: whole shape bounding box
                if edge_limits.max_x < shape_limits.min_x:
                    #print("bail:min-x", edge_s, edge_e, shape_limits.min_x)
                    continue
                if edge_limits.min_x > shape_limits.max_x:
                    #print("bail:max-x", edge_s, edge_e, shape_limits.max_x)
                    continue
                if edge_limits.max_y < shape_limits.min_y:
                    #print("bail:min-y", edge_s, edge_e, shape_limits.min_y)
                    continue
                if edge_limits.min_y > shape_limits.max_y:
                    #print(shape)
                    #print(edge_limits.min_y)
                    #print(edge_limits.max_y)
                    #print(shape_limits.min_y)
                    #print(shape_limits.max_y)
                    #print("bail:max-y", edge_s, edge_e, shape_limits.max_y)
                    continue
                
                # Try each shape edge in turn
                n_points = len(shape)
                for ix_s in range(0, n_points):
                
                    ShapeFiller.tot_split2 += 1
                    
                    ix_e = 0 if ix_s == n_points - 1 else ix_s + 1
                    shape_s = shape[ix_s]
                    shape_e = shape[ix_e]
                    
                    # Minimise full intersection checks: shape edge bounding box
                    if edge_limits.max_x < min(shape_s[0], shape_e[0]):
                        #print("bail:shape")
                        continue
                    if edge_limits.min_x > max(shape_s[0], shape_e[0]):
                        #print("bail:shape")
                        continue
                    if edge_limits.max_y < min(shape_s[1], shape_e[1]):
                        #print("bail:shape")
                        continue
                    if edge_limits.min_y > max(shape_s[1], shape_e[1]):
                        #print("bail:shape")
                        continue
                        
                    # We are inside shape edge bounding box: do a full intersection check
                    #print("check", edge, (shape_s, shape_e))
                    intersect = ShapeFiller.line_intersection(edge, (shape_s, shape_e))
                    if not intersect is None:
                        k = intersect[0]
                        # We don't count intersections as endpoints.
                        # So don't count it as an interssction if we are very nearly at an endpoint
                        # You just end up with floating point errors giving us repeatedly dividing an edge by tiny amounts
                        if abs(k) > 1e-6 and abs(k-1) > 1e-6:
                        
                            ShapeFiller.tot_split3 += 1
                            
                            # Get the intersection point and split the edge at it
                            pt = edge[0] + (edge[1] - edge[0]) * k
                            e = split_edges[i][1]
                            split_edges[i] = (split_edges[i][0], pt)
                            split_edges[i+1:i+1] = [(pt, e)]
                            # Update edge info
                            edge = split_edges[i]
                            edge_s = edge[0]
                            edge_e = edge[1]
                            edge_limits = ShapeFiller.Limits(min(edge_s[0], edge_e[0]), max(edge_s[0], edge_e[0]), min(edge_s[1], edge_e[1]), max(edge_s[1], edge_e[1]))
                            
            # This edge has done intersection checks for all shapes: go to the next (if any)
            i += 1
            
        # Return endpoints
        return [edge[1] for edge in split_edges]
    
    @staticmethod
    # Taken from https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
    def line_intersection(line1, line2):
    
        s1 = line1[0]
        e1 = line1[1]
        s2 = line2[0]
        e2 = line2[1]
        x0 = s1.x
        y0 = s1.y
        x1 = e1.x
        y1 = e1.y
        a0 = s2.x
        b0 = s2.y
        a1 = e2.x
        b1 = e2.y

        def is_between(x0, x, x1):
            return x0 <= x and x <= x1

        partial = False;
        denom = (b0 - b1) * (x0 - x1) - (y0 - y1) * (a0 - a1);
        if denom == 0:
            return None
        xy = (a0 * (y1 - b1) + a1 * (b0 - y1) + x1 * (b1 - b0)) / denom;
        partial = is_between(0, xy, 1);
        if (partial):
            # no point calculating this unless xy is between 0 & 1
            ab = (y1 * (x0 - a1) + b1 * (x1 - x0) + y0 * (a1 - x1)) / denom; 
        if partial and is_between(0, ab, 1):
            ab = 1-ab;
            xy = 1-xy;
            return (xy, ab)
        return None
   
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
        if c.ix_shape != c_prev.ix_shape:
            return False
          
        # What we are trying to find
        curr_edge = [c.ix_s, c.ix_e]
        ix_shape = c_prev.ix_shape
        shape = shapes[ix_shape]
        # print(f"Searching for {curr_edge}: {shape[curr_edge[0]]}->{shape[curr_edge[1]]}")

        # Where we're starting from
        prev_ix1 = c_prev.ix_s
        prev_ix2 = c_prev.ix_e
        # print(f"Previous is {[prev_ix1, prev_ix2]}: {shape[prev_ix1]}->{shape[prev_ix2]}")
        if prev_ix1 in curr_edge and prev_ix2 in curr_edge:
            # print("Search: on same edge")
            return True
        
        # We're not on the same edge as c_prev. But are we on a subsequent one? Figure out which direction
        # to start looking in - need y to be increasing. Note that y cannot be the same on both ends because
        # we don't do crossings for such edges in get_crossings()
        prev_p1 = shape[prev_ix1]
        prev_p2 = shape[prev_ix2]
        y1 = prev_p1.y
        y2 = prev_p2.y
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
            y_next = shape[ix_next].y
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
                y_s = shape[ix_s].y
                y_e = shape[ix_e].y
                x_s = shape[ix_s].x
                x_e = shape[ix_e].x
                
                # We want to be a bit careful about *what* crossings we add!
                if (y_s < y and y_e < y) or (y_s > y and y_e > y):
                    continue
                elif y_e == y and y_s == y:
                    # We are wholly along the y-line - we ignore segments like this
                    hits = hits
                elif y_e == y:
                    # We are ENDING at the y-line - we always include a crossing in this case
                    hits.append(ShapeFiller.EdgeHit(x_e, ix_shape, ix_s, ix_e))
                elif y_s == y:
                    # We are STARTING at the y-line - here we need to be careful.
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
                    while shape[ix_before_s].y == y:
                        ix_before_s = n_points - 1 if ix_before_s == 0 else ix_before_s - 1
                    y_prev = shape[ix_before_s].y
                    sign_prev = -1 if y_prev < y else +1
                    sign_next = -1 if y_e < y else +1
                    if sign_prev == sign_next:
                        hits.append(ShapeFiller.EdgeHit(x_s, ix_shape, ix_s, ix_e))
                elif (y_s < y and y_e > y) or (y_s > y and y_e < y):
                    # We are crossing the y-line - these segments always get added as a crossing point
                    x = x_s + (x_e - x_s) * (y - y_s) / (y_e - y_s)
                    hits.append(ShapeFiller.EdgeHit(x, ix_shape, ix_s, ix_e))
                        
        # sort by x-value - this helps when we are using a naive strategy for plotting
        # doubt if it makes any real difference for the more intelligent connection strategy we are now using by dfault.
        hits = sorted(hits, key=lambda hit: hit.x)
        
        return hits
        
class Point:

    @staticmethod
    def From(other):
        if type(other) == Point:
            return other
        return Point(other[0], other[1])

    @staticmethod
    def Origin():
        return Point(0, 0)
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        elif isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]
        else:
            return False
            
    def __add__(self, o):
        return Point(self.x + o.x, self.y + o.y)

    def __sub__(self, o):
        return Point(self.x - o.x, self.y - o.y)

    def dist(self):
        return math.sqrt(self.x*self.x + self.y*self.y)

    def norm(self):
        dist = self.dist()
        return Point(self.x / dist, self.y / dist)
        
    def __mul__(self, other):
        return Point(self.x * other, self.y * other)
        
    def __truediv__ (self, other):
        return Point(self.x / other, self.y / other)
        
    def __len__(self):
        return 2
        
    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        raise IndexError

    def __repr__(self):
        return f"({self.x},{self.y})"