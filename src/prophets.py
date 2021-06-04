import math
import perlin

import svgwrite

from pyplot import Point, ShapeFiller

def text_in_circle(drawing, centre, radius=30):

    layer = drawing.add_layer('1')
    for angle in range(0, 360, 30):
        drawing.add_spiral_letter("X", 24, centre, radius, angle=angle*math.pi/180, family='CNC Vector', container=layer)
    drawing.add_dot(centre, radius + 7.3, r_start = radius  + 5.8, stroke=svgwrite.rgb(255, 255, 0, '%'), container=layer)
    drawing.add_dot(centre, radius - 1.8, r_start = radius  - 3.3, stroke=svgwrite.rgb(255, 255, 0, '%'), container=layer)


def draw_false_prophets(d):

    # A4
    top_left = (0, 0)
    x_size = 210
    y_size = 297
    projection_angle=math.pi*0.2
    p = perlin.PerlinNoise(scale=400, octaves=2)
    polylines = d.make_surface(top_left, x_size, int(y_size / math.cos(projection_angle)), p.calc2d, projection_angle=projection_angle)

    # clip to margin around edge of paper
    topleft = (20, 20)
    shapes = [d.make_rect(topleft, x_size - 2 * topleft[0], y_size - 2 * topleft[1])]
    sf = ShapeFiller(shapes)
    polylines = sf.clip(polylines, inverse=True)
    
    # medallion
    medallion_centre = (int(x_size/2), int(y_size/2))
    shapes = [d.make_circle(medallion_centre, 29, x_scale = 0.7), d.make_circle(medallion_centre, 27, x_scale = 0.7)]
    sf = ShapeFiller(shapes)
    polylines = sf.clip(polylines, union=True)
    new_lines = sf.get_paths(d.pen_type.pen_width / 5)
    for line in new_lines:
        polylines.append(line)
    
    image_path = d.make_image_spiral_single('burroughs.jpg', medallion_centre, 25, x_scale = 0.7)
    polylines.append(image_path)

    family='CNC Vector'
    # family = 'HersheyScript1smooth'
    family = 'Arial'
    family = 'Caslon Antique'
    header_pos = (int(x_size/2), 40)
    fontsize = 36
    text = "False Prophets Of The New Millenium."
    ext = d.text_bound(text, fontsize, family)
    position = (header_pos[0] - ext.width/2, header_pos[1])
    text_paths = d.make_text(text, position, fontsize=fontsize, family=family)
    rect_width = 0.5
    rect1 = d.make_rect((position[0] - 2, position[1] + ext.y_bearing - 2), ext.width + 4, ext.height + 4)
    rect2 = d.make_rect((position[0] - (2+rect_width), position[1] + ext.y_bearing - (2+rect_width)), ext.width + (4+2*rect_width), ext.height + (4+2*rect_width))
    sf = ShapeFiller([rect1, rect2])
    polylines = sf.clip(polylines, union=True)
    rect_paths = sf.get_paths(d.pen_type.pen_width / 5)
    for p in rect_paths:
        polylines.append(p)
    sf = ShapeFiller(text_paths)
    filled_text_paths = sf.get_paths(d.pen_type.pen_width / 5)
    for p in filled_text_paths:
        polylines.append(p)
    
    for text_path in text_paths:
        polylines.append(text_path)

    # legend

    family='CNC Vector'
    # family = 'HersheyScript1smooth'
    family = 'Caslon Antique'
    fontsize = 24
    text = "WAKEFIELD"
    ext = d.text_bound(text, fontsize, family)
    
    position = (medallion_centre[0] - ext.width/2, medallion_centre[1]+30+4+ext.height)
    text_paths = d.make_text(text, position, fontsize=fontsize, family=family)
    sf = ShapeFiller(text_paths)
    filled_text_paths = sf.get_paths(d.pen_type.pen_width / 5)
    
    rect_width = 0.5
    rect1 = d.make_rect((position[0] - 2, position[1] + ext.y_bearing - 2), ext.width + 4, ext.height + 4)
    rect2 = d.make_rect((position[0] - (2+rect_width), position[1] + ext.y_bearing - (2+rect_width)), ext.width + (4+2*rect_width), ext.height + (4+2*rect_width))
    sf = ShapeFiller([rect1, rect2])
    polylines = sf.clip(polylines, union=True)
    rect_paths = sf.get_paths(d.pen_type.pen_width / 5)
    for p in rect_paths:
        polylines.append(p)
    for text_path in filled_text_paths:
        polylines.append(text_path)

    polylines2 = []
    family = 'Aquifer'
    family = 'Caslon Antique'
    fontsize = 48

    row_ext = d.text_bound("Op", fontsize, family)
    
    header_pos = (int(x_size/2), 80)
    text = "False Prophets Of"
    ext = d.text_bound(text, fontsize, family)
    position = (header_pos[0] - ext.width/2, header_pos[1])
    text_paths = d.make_text(text, position, fontsize=fontsize, family=family)
    sf = ShapeFiller(text_paths)
    filled_text_paths = sf.get_paths(d.pen_type.pen_width / 5)
    for p in filled_text_paths:
        polylines2.append(p)
        
    header_pos = (header_pos[0], header_pos[1] + row_ext.height + 2)
    text = "The New Millenium"
    ext = d.text_bound(text, fontsize, family)
    position = (header_pos[0] - ext.width/2, header_pos[1])
    text_paths = d.make_text(text, position, fontsize=fontsize, family=family)
    sf = ShapeFiller(text_paths)
    filled_text_paths = sf.get_paths(d.pen_type.pen_width / 5)
    for p in filled_text_paths:
        polylines2.append(p)

    d.add_polylines(polylines)

def multi_burroughs(drawing):
    layer1 = drawing.add_layer('1')
    drawing.image_spiral_single(layer1, 'burroughs.jpg', (100, 60), 30, svgwrite.rgb(255, 0, 0, '%'))
    layer2 = drawing.add_layer('2')
    drawing.image_spiral_single(layer2, 'burroughs.jpg', (100, 130), 30, svgwrite.rgb(255, 255, 0, '%'))
    layer3 = drawing.add_layer('3')
    drawing.image_spiral_single(layer3, 'burroughs.jpg', (100, 200), 30, svgwrite.rgb(0, 255, 0, '%'))

def burroughs_medal(d):
    # print("medal")
    d.image_spiral_single(d.add_layer('2'), 'burroughs.jpg', (100, 160), 25)
    text_in_circle(d, (100,160))
            
def wakefield_medal(d):
    # print("medal")
    d.image_spiral_single(d.add_layer('2'), 'wakefield2.jpg', (100, 90), 60)
    # text_in_circle(d, (100,90), radius=65)
           
def draw_wakefield(drawing):    
    
    import lsystem

    nslice = 40    
    
    polylines = []
    
    paper_centre = Point(102.5, 148)
    
    rect_size = Point(192, 276)
    clip_2 = drawing.make_rect(paper_centre - rect_size / 2, rect_size.x, rect_size.y)
    clip_shape = drawing.make_circle(paper_centre, 44, x_scale=0.8)
    sf = ShapeFiller([clip_shape, clip_2])

    drawing.image_spiral_single(drawing.dwg, 'wakefield2.jpg', paper_centre, 40, x_scale=0.8)

    all_lines = lsystem.test_lsystem_hilbert(order=8, size=1)
    def centre_on(polylines, new_centre):
        n = 0
        sumx = 0
        sumy = 0
        for line in polylines:
            for point in line[:-1]:
                n += 1
                sumx += point.x
                sumy += point.y
        centre = Point(sumx / n, sumy / n)
        adj = paper_centre - centre
        return [[p + adj for p in line] for line in polylines]
    all_lines = centre_on(all_lines, paper_centre)
    all_lines = sf.clip(all_lines, inverse=True)
    
    background_layer = drawing.add_layer("2-hilbert")
    drawing.add_polylines(all_lines, container=background_layer)
    
