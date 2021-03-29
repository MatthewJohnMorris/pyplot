import math

from pyplot import Point

class turtle:

    def __init__(self):
        self.instructions = []
        self.angle = 0
    
    def nop(self):
        self = self
    
    def forward(self):
        self.instructions.append(("F"))

    def turn(self, delta):
        self.instructions.append(("A", delta))
        
    def render(self, size):
        pos = Point(0,0)
        points = [pos]
        a = 0
        for instruction in self.instructions:
            if instruction[0] == "F":
                radians = a/360*2*math.pi
                pos = pos + Point(math.cos(radians), math.sin(radians)) * size
                points.append(pos)
            elif instruction[0] == "A":
                a += instruction[1]
            else:
                raise Exception(f'Unknown code: {instruction[0]}')
        return points

gosper_map = {
    "A": (lambda turtle: turtle.forward(), "A-B--B+A++AA+B-"),
    "B": (lambda turtle: turtle.forward(), "+A-BB--B-A++A+B"),
    "-": (lambda turtle: turtle.turn(60), None),
    "+": (lambda turtle: turtle.turn(-60), None),
}

hilbert_map = {
    "A": (lambda turtle: turtle.nop(), "+BF-AFA-FB+"),
    "B": (lambda turtle: turtle.nop(), "-AF+BFB+FA-"),
    "F": (lambda turtle: turtle.forward(), None),
    "-": (lambda turtle: turtle.turn(90), None),
    "+": (lambda turtle: turtle.turn(-90), None),
}

arrowhead_map = {
    "A": (lambda turtle: turtle.forward(), "B-A-B"),
    "B": (lambda turtle: turtle.forward(), "A+B+A"),
    "-": (lambda turtle: turtle.turn(60), None),
    "+": (lambda turtle: turtle.turn(-60), None),
}

def lsystem_process_token(target, order, token, lsystem_map):

    map_elem = lsystem_map[token]
    if order == 0 or map_elem[1] is None:
        map_elem[0](target)
    else:
        for new_token in map_elem[1]:
            lsystem_process_token(target, order-1, new_token, lsystem_map)

def test_lsystem_gosper(order, size):

    target = turtle()
    lsystem_process_token(target, order, "A", gosper_map)
    return target.render(size)

def test_lsystem_hilbert(order, size):

    target = turtle()
    lsystem_process_token(target, order, "A", hilbert_map)
    return target.render(size)

def test_lsystem_arrowhead(order, size):

    target = turtle()
    lsystem_process_token(target, order, "A", arrowhead_map)
    return target.render(size)

