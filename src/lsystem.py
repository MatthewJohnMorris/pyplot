

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

def test_lsystem_gosper(order):

    target = turtle()
    lsystem_process_token(target, order, "A", gosper_map)
    return target.instructions

def test_lsystem_hilbert(order):

    target = turtle()
    lsystem_process_token(target, order, "A", hilbert_map)
    return target.instructions

def test_lsystem_arrowhead(order):

    target = turtle()
    lsystem_process_token(target, order, "A", arrowhead_map)
    return target.instructions

