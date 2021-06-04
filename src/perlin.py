import math
import random

from noise import pnoise1, pnoise2

import svgwrite

class PerlinNoise:

    def __init__(self, seed=None, octaves=2, persistence=0.5, lacunarity=6, scale=1):
    
        self.seed = 200 if seed is None else seed
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.scale = scale

    def calc2d(self, norm_coord):

        return self.scale*pnoise2(
            norm_coord[0],
            norm_coord[1],
            octaves=self.octaves,
            persistence=self.persistence,
            lacunarity=self.lacunarity,
            repeatx=1,
            repeaty=1,
            base=self.seed)

    def calc1d(self, norm_coord):

        return self.scale*pnoise1(
            norm_coord,
            octaves=self.octaves,
            persistence=self.persistence,
            lacunarity=self.lacunarity,
            repeat=1,
            base=self.seed)

def plot_perlin_drape_spiral(drawing, seed, centre=(100,70), r_base=50):  

    circ = 2 * math.pi * r_base
    n = int(circ) + 1
    ni = int(r_base / (drawing.pen_type.pen_width * 1.5))
    target = n * ni
    iscale = r_base / ni * 2
    points = []
    p = PerlinNoise(seed=seed)
    
    for t in range(0, target):
        a = 2 * math.pi * (t / n)
        c = math.cos(a)
        s = math.sin(a)
        r_noise = p.calc2d((a / (2 * math.pi), 0))
        r_adj = r_base + r_noise * 150 * t / target
        pt = (centre[0] + r_adj * c, centre[1] + iscale * (t / n) + r_adj * s)
        points.append(pt)
    drawing.add_polyline(points)
  
def plot_perlin_spiral(drawing, centre, r_start, r_end, r_layer, seed, stroke=None, container=None):  

    circ = 2 * math.pi * r_end
    n = int(circ) * 2
    points = []
    layers = (r_end - r_start) / r_layer
    p = PerlinNoise(seed=seed)
    for t in range(0, int(n * layers)):
        a = 2 * math.pi * (t / n)
        c = math.cos(a)
        s = math.sin(a)
        
        octaves = 2
        # 0 = perfectly smooth
        persistence = 0.6
        lacunarity = 7
        repeat = 1
        x = a / (2 * math.pi)
        z = p.calc1d(x)
        
        r_now = r_start + (r_end - r_start) * t / (n * layers)
        r_adj = r_now + z * r_now * t / (n * layers)
        pt = (centre[0] + r_adj * c, centre[1] + r_adj * s)
        points.append(pt)
    drawing.add_polyline(points, stroke=stroke, container=container)

def plot_perlin_spirals(drawing):

    back_layer = drawing.add_layer('0-black')
    spiral_strokes = [svgwrite.rgb(255, 0, 0, '%'), svgwrite.rgb(0, 128, 0, '%'), svgwrite.rgb(0, 0, 255, '%')]
    spiral_layers = [drawing.add_layer('1-red'), drawing.add_layer('2-green'), drawing.add_layer('3-blue')]
    for i in range(0, 9):
        for j in range(0, 13):
            seed = 10 * i + j
            # for k in range(1, 7):
            #    plot_perlin_ring(drawing, (10*(i+1),10*(j+1)), k/2, seed)
            drawing.add_square((20*(i+1)-9,20*(j+1)-9),18,container=back_layer)
            drawing.add_square((20*(i+1)-9.2,20*(j+1)-9.2),18.4,container=back_layer)
            drawing.add_square((20*(i+1)-9.4,20*(j+1)-9.4),18.8,container=back_layer)
            for x in range(0, 2):
                i_layer = int(random.random() * 3)
                spiral_layer = spiral_layers[i_layer]
                spiral_stroke = spiral_strokes[i_layer]
                plot_perlin_spiral(drawing, (20*(i+1),20*(j+1)), 0.5, 6, 0.6, seed + i_layer, stroke=spiral_stroke, container=spiral_layer)
    
def plot_perlin_surface(drawing):

    # can render texture with z-function applied by preserving x, and doing y-out = y * cos(a) + z * sin(a) with a the viewing angle?  
    top_left = (30, 30)
    x_size = 140
    y_size = 240
    p = PerlinNoise(scale=100)
    drawing.add_surface(top_left, x_size, y_size, p.calc2d)

