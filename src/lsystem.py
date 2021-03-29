

class turtle:

    def __init__(self):
        self.instructions = []
        self.angle = 0
    
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

def lsystem_process_token(target, order, token, lsystem_map):

    map_elem = lsystem_map[token]
    if order == 0 or map_elem[1] is None:
        map_elem[0](target)
    else:
        for new_token in map_elem[1]:
            lsystem_process_token(target, order-1, new_token, lsystem_map)

def test_lsystem(order):

    target = turtle()
    lsystem_process_token(target, order, "A", gosper_map)
    return target.instructions

