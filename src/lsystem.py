import math

from pyplot import Point

class turtle:

    def __init__(self):
        self.instructions = []
        self.angle = 0
    
    def nop(self):
        self = self
    
    def forward(self):
        self.instructions.append(["F"])

    def turn(self, delta):
        self.instructions.append(["A", delta])
        
    def push(self):
        self.instructions.append(["PUSH"])
        
    def pop(self):
        self.instructions.append(["POP"])
        
    def render(self, size, start_a = 0):
        stack = []
        pos = Point(0,0)
        all_lines = []
        current_line = [pos]
        a = start_a
        for instruction in self.instructions:
            if instruction[0] == "F":
                radians = a/360*2*math.pi
                pos = pos + Point(math.cos(radians), math.sin(radians)) * size
                current_line.append(pos)
            elif instruction[0] == "A":
                a += instruction[1]
            elif instruction[0] == "PUSH":
                stack.append((pos, a))
            elif instruction[0] == "POP":
                if len(current_line) > 1:
                    all_lines.append(current_line)
                (pos, a) = stack.pop()
                current_line = [pos]
            else:
                print(self.instructions)
                raise Exception(f'Unknown code: {instruction[0]}')
        if len(current_line) > 1:
            all_lines.append(current_line)
        return all_lines

def lsystem_process_token(target, order, token, lsystem_map):

    map_elem = lsystem_map[token]
    if order == 0 or map_elem[1] is None:
        map_elem[0](target)
    else:
        for new_token in map_elem[1]:
            lsystem_process_token(target, order-1, new_token, lsystem_map)

class lsystem_map():

    def __init__(self, angle):
        self.token_map = {
            "-": (lambda turtle: turtle.turn(-angle), None),
            "+": (lambda turtle: turtle.turn(+angle), None),
            "[": (lambda turtle: turtle.push(), None),
            "]": (lambda turtle: turtle.pop(), None),
            }
            
    def add_entry(self, token, turtle_op, image=None):
        self.token_map[token] = (turtle_op, image)
        return self
        
    def process_token(self, target, order, token):

        map_elem = self.token_map[token]
        if order == 0 or map_elem[1] is None:
            map_elem[0](target)
        else:
            for new_token in map_elem[1]:
                self.process_token(target, order-1, new_token)
            
    def process(self, order, size, start, start_a):
        target = turtle()
        for token in start:
            self.process_token(target, order, token)
        return target.render(size, start_a=start_a)

def test_lsystem_gosper(order, size):

    return lsystem_map(-60) \
        .add_entry("A", lambda turtle: turtle.forward(), "A-B--B+A++AA+B-") \
        .add_entry("B", lambda turtle: turtle.forward(), "+A-BB--B-A++A+B") \
        .process(order, size, "A")

def test_lsystem_hilbert(order, size):

    return lsystem_map(-90) \
        .add_entry("F", lambda turtle: turtle.forward()) \
        .add_entry("A", lambda turtle: turtle.nop(), "+BF-AFA-FB+") \
        .add_entry("B", lambda turtle: turtle.nop(), "-AF+BFB+FA-") \
        .process(order, size, "A")

def test_lsystem_arrowhead(order, size):

    return lsystem_map(-60) \
        .add_entry("A", lambda turtle: turtle.forward(), "B-A-B") \
        .add_entry("B", lambda turtle: turtle.forward(), "A+B+A") \
        .process(order, size, "A")

def test_lsystem_tree(order, size):

    return lsystem_map(45) \
        .add_entry("0", lambda turtle: turtle.forward(), "1[+0]-0") \
        .add_entry("1", lambda turtle: turtle.forward(), "11") \
        .process(order, size, "0")

def test_lsystem_barnsley_fern(order, size):

    return lsystem_map(25) \
        .add_entry("F", lambda turtle: turtle.forward(), "FF") \
        .add_entry("X", lambda turtle: turtle.nop(), "F+[[X]-X]-F[-FX]+X") \
        .process(order, size, "----X")

def test_lsystem_koch_snowflake(order, size):

    return lsystem_map(60) \
        .add_entry("F", lambda turtle: turtle.forward(), "F+F--F+F") \
        .process(order, size, "F--F--F")

def test_lsystem_pentaplexity(order, size):

    return lsystem_map(36) \
        .add_entry("F", lambda turtle: turtle.forward(), "F++F++F|F-F++F") \
        .add_entry("|", lambda turtle: turtle.turn(+180)) \
        .process(order, size, "F++F++F++F++F")

def test_lsystem_bot_example(order, size, start_a=0):

    return lsystem_map(83) \
        .add_entry("F", lambda turtle: turtle.forward(), "XF+XLLF") \
        .add_entry("L", lambda turtle: turtle.nop(), "XLGX")        \
        .add_entry("J", lambda turtle: turtle.nop(), "[X-]JE")      \
        .add_entry("X", lambda turtle: turtle.nop(), "F")           \
        .add_entry("E", lambda turtle: turtle.nop(), "[[JXX]XG]")   \
        .add_entry("G", lambda turtle: turtle.nop(), "G")           \
        .process(order, size, "LL", start_a=start_a)

def test_lsystem_bot_example2(order, size, start_a=0):

    # Jul 5, 2020
    return lsystem_map(16) \
        .add_entry("F", lambda turtle: turtle.forward(), "FSSF--+") \
        .add_entry("S", lambda turtle: turtle.nop(), "-FFF-F+")        \
        .process(order, size, "FSF", start_a=start_a)

def test_lsystem_bot_example3(order, size, start_a=0):

    return lsystem_map(89) \
        .add_entry("F", lambda turtle: turtle.forward(), "N") \
        .add_entry("G", lambda turtle: turtle.nop(), "DGMGD-F") \
        .add_entry("M", lambda turtle: turtle.nop(), "FFMGZ-") \
        .add_entry("Z", lambda turtle: turtle.nop(), "MMG") \
        .add_entry("D", lambda turtle: turtle.nop(), "ZN-") \
        .add_entry("N", lambda turtle: turtle.nop(), "N") \
        .process(order, size, "MDMM", start_a=start_a)

def test_lsystem_bot_example4(order, size, start_a=0):

    return lsystem_map(24) \
        .add_entry("F", lambda turtle: turtle.forward(), "O-FGR") \
        .add_entry("O", lambda turtle: turtle.nop(), "+FFFFR+G") \
        .add_entry("G", lambda turtle: turtle.nop(), "F") \
        .add_entry("R", lambda turtle: turtle.nop(), "F") \
        .add_entry("H", lambda turtle: turtle.nop(), "[]") \
        .process(order, size, "OO", start_a=start_a)

def test_lsystem_fass(order, size, start_a=0):

    return lsystem_map(45) \
        .add_entry("F", lambda turtle: turtle.forward(), "F") \
        .add_entry("X", lambda turtle: turtle.forward(), "X+F+X--F--X+F+X") \
        .process(order, size, "FX++FX++FX++FX", start_a=start_a)

def test_lsystem_fassA(order, size, start_a=0):

    example_map = {
        "F": (lambda turtle: turtle.forward(), "F"),
        "X": (lambda turtle: turtle.forward(), "X+F+X--F--X+F+X"),
        "-": (lambda turtle: turtle.turn(-45), None),
        "+": (lambda turtle: turtle.turn(+45), None),
        "[": (lambda turtle: turtle.push(), None),
        "]": (lambda turtle: turtle.pop(), None),
    }
    target = turtle()
    for token in "FX++FX++FX++FX":
        lsystem_process_token(target, order, token, example_map)
    # print(target.instructions)
    return target.render(size, start_a = start_a)

 

 

