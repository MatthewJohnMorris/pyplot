

class turtle:

    def __init__(self):
        self.instructions = []
        self.angle = 0
    
    def forward(self, size):
        self.instructions.append(("F", size))

    def right(self, delta):
        self.instructions.append(("A", delta))

    def left(self, delta):
        self.instructions.append(("A", -delta))

def lsystem_process_token(turtle, order, size, replace_map, token) -> None:
    """Draw the Gosper curve."""
    if order == 0:
        turtle.forward(size)
        return
        
    ops = None
    if token == "A":
        ops = "A-B--B+A++AA+B-"
    elif token == "B":
        ops = "+A-BB--B-A++A+B"
    if ops == None:
        raise Exception(f"Unexpected token: '{token}'")
        
    for op in ops:
        replace_map[op](turtle, order - 1, size, replace_map)

def test_lsystem(order, size):
    t = turtle()
    
    lsystem_replace_map = {
        "A": lambda turtle, o, size, replace_map: lsystem_process_token(turtle, o, size, replace_map, "A"),
        "B": lambda turtle, o, size, replace_map: lsystem_process_token(turtle, o, size, replace_map, "B"),
        "-": lambda turtle, o, size, replace_map: turtle.right(60),
        "+": lambda turtle, o, size, replace_map: turtle.left(60),
    }
    
    lsystem_process_token(t, order, size, lsystem_replace_map, "A")
    return t.instructions