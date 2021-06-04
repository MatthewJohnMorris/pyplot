import random
import svgwrite

from pyplot import Point

def random_coloured_rects(drawing):

    inner_tl = (100, 100)
    inner_ext = (50, 20)
    width = 0.4
    strokes = [svgwrite.rgb(101, 67, 33, '%'), svgwrite.rgb(128, 70, 0, '%'), svgwrite.rgb(255, 255, 0, '%'), svgwrite.rgb(255, 0, 0, '%')]
    layers = [drawing.add_layer('1-brown'), drawing.add_layer('2-orange'), drawing.add_layer('3-yellow'), drawing.add_layer('4-red')]
    for i in range(0, 100):
        i_tl = (inner_tl[0] - width*i, inner_tl[1] - width*i)
        i_ext = (inner_ext[0] + width*i*2, inner_ext[1] + width*i*2)
        i_layer = int(random.random() * 4)
        layer = layers[i_layer]
        stroke = strokes[i_layer]
        drawing.add_rect(i_tl, i_ext[0], i_ext[1], stroke=stroke, container=layer)

def test_line_colour(d):

    base_pos = Point(20, 20)
    size = 14
    gap = 16
    diff = d.pen_type.pen_width * 0.9
    layers = [d.add_layer(f"{i+1}") for i in range(0,10)]
    for i in range(0, 10):
        for j in range(i, 10):
            sq_pos = base_pos + Point(i*gap, j*gap)
            k = 0
            while diff * k < size:
                ix_layer = i if k % 2 == 0 else j
                layer = layers[ix_layer]
                pos = sq_pos + Point(diff*k, 0)
                d.add_polyline([pos, pos + Point(0, size)], container=layer)
                k += 1

