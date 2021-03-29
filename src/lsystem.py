

class turtle:

    def __init__(self):
        self.instructions = []
        self.angle = 0
    
    def forward(self):
        self.instructions.append(("F"))

    def turn(self, delta):
        self.instructions.append(("A", delta))

def lsystem_process_token(turtle, order, replace_map, token) -> None:
    """Draw the Gosper curve."""
    if order == 0:
        turtle.forward()
        return
        
    ops = None
    if token == "A":
        ops = "A-B--B+A++AA+B-"
    elif token == "B":
        ops = "+A-BB--B-A++A+B"
    if ops == None:
        raise Exception(f"Unexpected token: '{token}'")
        
    for op in ops:
        replace_map[op](turtle, order - 1, replace_map)

def test_lsystem(order):
    t = turtle()
    
    lsystem_replace_map = {
        "A": lambda turtle, o, replace_map: lsystem_process_token(turtle, o, replace_map, "A"),
        "B": lambda turtle, o, replace_map: lsystem_process_token(turtle, o, replace_map, "B"),
        "-": lambda turtle, o, replace_map: turtle.turn(60),
        "+": lambda turtle, o, replace_map: turtle.turn(-60),
    }
    
    lsystem_process_token(t, order, lsystem_replace_map, "A")
    return t.instructions
