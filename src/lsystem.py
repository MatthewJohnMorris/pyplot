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

class lsystem_map():

    def __init__(self, angle):
        # Create some standard tokens whose meaning seems pretty universal
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
            
    def process(self, order, size, start, start_a=0):
        target = turtle()
        for token in start:
            self.process_token(target, order, token)
        return target.render(size, start_a=start_a)

ACTION_FWD = lambda turtle: turtle.forward()
ACTION_NOP = lambda turtle: turtle.nop()
ACTION_180 = lambda turtle: turtle.turn(+180)

def test_lsystem_gosper(order, size):

    return lsystem_map(-60) \
        .add_entry("A", ACTION_FWD, "A-B--B+A++AA+B-") \
        .add_entry("B", ACTION_FWD, "+A-BB--B-A++A+B") \
        .process(order, size, "A")

def test_lsystem_hilbert(order, size):

    return lsystem_map(-90) \
        .add_entry("F", ACTION_FWD) \
        .add_entry("A", ACTION_NOP, "+BF-AFA-FB+") \
        .add_entry("B", ACTION_NOP, "-AF+BFB+FA-") \
        .process(order, size, "A")

def test_lsystem_arrowhead(order, size):

    return lsystem_map(-60) \
        .add_entry("A", ACTION_FWD, "B-A-B") \
        .add_entry("B", ACTION_FWD, "A+B+A") \
        .process(order, size, "A")

def test_lsystem_tree(order, size):

    return lsystem_map(45) \
        .add_entry("0", ACTION_FWD, "1[+0]-0") \
        .add_entry("1", ACTION_FWD, "11") \
        .process(order, size, "0")

def test_lsystem_barnsley_fern(order, size):

    return lsystem_map(25) \
        .add_entry("F", ACTION_FWD, "FF") \
        .add_entry("X", ACTION_NOP, "F+[[X]-X]-F[-FX]+X") \
        .process(order, size, "----X")

def test_lsystem_koch_snowflake(order, size):

    return lsystem_map(60) \
        .add_entry("F", ACTION_FWD, "F+F--F+F") \
        .process(order, size, "F--F--F")

def test_lsystem_pentaplexity(order, size):

    return lsystem_map(36) \
        .add_entry("F", ACTION_FWD, "F++F++F|F-F++F") \
        .add_entry("|", ACTION_180) \
        .process(order, size, "F++F++F++F++F")

def test_lsystem_bot_example(order, size, start_a=0):

    return lsystem_map(83) \
        .add_entry("F", ACTION_FWD, "XF+XLLF") \
        .add_entry("L", ACTION_NOP, "XLGX")        \
        .add_entry("J", ACTION_NOP, "[X-]JE")      \
        .add_entry("X", ACTION_NOP, "F")           \
        .add_entry("E", ACTION_NOP, "[[JXX]XG]")   \
        .add_entry("G", ACTION_NOP, "G")           \
        .process(order, size, "LL", start_a=start_a)

def test_lsystem_bot_example2(order, size, start_a=0):

    # Jul 5, 2020
    return lsystem_map(16) \
        .add_entry("F", ACTION_FWD, "FSSF--+") \
        .add_entry("S", ACTION_NOP, "-FFF-F+")        \
        .process(order, size, "FSF", start_a=start_a)

def test_lsystem_bot_example3(order, size, start_a=0):

    return lsystem_map(89) \
        .add_entry("F", ACTION_FWD, "N") \
        .add_entry("G", ACTION_NOP, "DGMGD-F") \
        .add_entry("M", ACTION_NOP, "FFMGZ-") \
        .add_entry("Z", ACTION_NOP, "MMG") \
        .add_entry("D", ACTION_NOP, "ZN-") \
        .add_entry("N", ACTION_NOP, "N") \
        .process(order, size, "MDMM", start_a=start_a)

def test_lsystem_bot_example4(order, size, start_a=0):

    return lsystem_map(24) \
        .add_entry("F", ACTION_FWD, "O-FGR") \
        .add_entry("O", ACTION_NOP, "+FFFFR+G") \
        .add_entry("G", ACTION_NOP, "F") \
        .add_entry("R", ACTION_NOP, "F") \
        .add_entry("H", ACTION_NOP, "[]") \
        .process(order, size, "OO", start_a=start_a)

def test_lsystem_fass(order, size, start_a=0):

    return lsystem_map(45) \
        .add_entry("F", ACTION_FWD, "F") \
        .add_entry("X", ACTION_FWD, "X+F+X--F--X+F+X") \
        .process(order, size, "FX++FX++FX++FX", start_a=start_a)

def lsystem_test(drawing):
    # A good source for new ideas: http://paulbourke.net/fractals/lsys/

    import lsystem
    # all_lines = lsystem.test_lsystem_gosper(order=5, size=1)
    all_lines = lsystem.test_lsystem_hilbert(order=8, size=0.7)
    # all_lines = lsystem.test_lsystem_arrowhead(order=8, size=0.5)
    # all_lines = lsystem.test_lsystem_arrowhead(order=9, size=0.3)
    # all_lines = lsystem.test_lsystem_tree(order=7, size=1)
    # all_lines = lsystem.test_lsystem_barnsley_fern(order=6, size=1)
    # all_lines = lsystem.test_lsystem_koch_snowflake(order=5, size=0.5)
    # all_lines = lsystem.test_lsystem_pentaplexity(order=5, size=0.8)
    # all_lines = lsystem.test_lsystem_bot_example(order=7, size=3, start_a=45)
    # all_lines = lsystem.test_lsystem_bot_example2(order=5, size=3, start_a=45)
    # all_lines = lsystem.test_lsystem_bot_example3(order=7, size=3, start_a=45)
    # all_lines = lsystem.test_lsystem_bot_example4(order=7, size=1.3, start_a=90)
    # all_lines = lsystem.test_lsystem_fass(order=6, size=0.75, start_a=90)

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
    
    # centre the drawing on the paper
    paper_centre = Point(102.5, 148)
    drawing.add_polylines(centre_on(all_lines, paper_centre))

