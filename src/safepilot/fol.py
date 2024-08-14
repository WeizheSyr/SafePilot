from z3 import *
import sys

# State class definition
class State:
    def __init__(self, name, num_blocks):
        self.name = name
        self.table = Function(f'{name}_table', IntSort(), BoolSort())
        self.hand = Function(f'{name}_hand', IntSort(), BoolSort())
        self.stacked = Function(f'{name}_stacked', IntSort(), IntSort(), BoolSort())
        self.clear = Function(f'{name}_clear', IntSort(), BoolSort())
        self.handsfree = Function(f'{name}_handsfree', BoolSort())
        self.num_blocks = num_blocks

    def is_same_for_other_blocks(self, other, block):
        return And([And(self.table(x) == other.table(x),
                        self.hand(x) == other.hand(x),
                        self.clear(x) == other.clear(x))
                   for x in range(1, self.num_blocks + 1) if x != block])

    def is_stacked_same(self, other):
        return And([self.stacked(x, y) == other.stacked(x, y)
                   for x in range(1, self.num_blocks + 1) for y in range(1, self.num_blocks + 1)])

# Action definitions
def pick_up(s1, s2, block):
    preconditions = And(s1.clear(block), s1.table(block), Not(s1.hand(block)), s1.handsfree())
    effects = And(s2.hand(block), Not(s2.table(block)), Not(s2.clear(block)),
                  s1.is_same_for_other_blocks(s2, block),
                  s1.is_stacked_same(s2))
    return And(preconditions, effects)

def put_down(s1, s2, block):
    preconditions = And(s1.hand(block), Not(s1.handsfree()))
    effects = And(Not(s2.hand(block)), s2.table(block), s2.clear(block),
                  s1.is_same_for_other_blocks(s2, block),
                  s1.is_stacked_same(s2))
    return And(preconditions, effects)

def stack(s1, s2, block1, block2):
    constraints = []
    # General conditions for all other blocks
    for x in range(s1.num_blocks):
        if x != block1 and x != block2:
            constraints.append(s1.table(x) == s2.table(x))
            constraints.append(s1.hand(x) == s2.hand(x))
            constraints.append(s1.clear(x) == s2.clear(x))
            for y in range(s1.num_blocks):
                if y != block1 and y != block2:
                    constraints.append(s1.stacked(x, y) == s2.stacked(x, y))

    constraints.append(Or(
        And(
            s1.table(block1),
            Not(s1.stacked(block1, block2)),
            s1.clear(block1),
            s1.clear(block2),
            s1.handsfree(),
            Not(s2.table(block1)),
            Not(s2.hand(block1)),
            s2.stacked(block1, block2),
            s2.clear(block1),
            Not(s2.clear(block2)),
            s2.handsfree()
        ),
        And(
            s1.hand(block1),
            Not(s1.stacked(block1, block2)),
            s1.clear(block2),
            Not(s1.handsfree()),
            Not(s2.table(block1)),
            Not(s2.hand(block1)),
            s2.stacked(block1, block2),
            s2.clear(block1),
            Not(s2.clear(block2)),
            s2.handsfree()
        )
    ))

    return And(constraints)

def unstack(s1, s2, block1, block2):
    constraints = []
    # General conditions for all other blocks
    for x in range(s1.num_blocks):
        if x != block1 and x != block2:
            constraints.append(s1.table(x) == s2.table(x))
            constraints.append(s1.hand(x) == s2.hand(x))
            constraints.append(s1.clear(x) == s2.clear(x))
            for y in range(s1.num_blocks):
                if y != block1 and y != block2:
                    constraints.append(s1.stacked(x, y) == s2.stacked(x, y))

    constraints.append(Or(
        And(
            s1.stacked(block1, block2),
            s1.clear(block1),
            s1.handsfree(),
            s2.table(block1),
            Not(s2.stacked(block1, block2)),
            s2.clear(block1),
            s2.clear(block2),
            s2.handsfree()
        ),
        And(
            s1.stacked(block1, block2),
            s1.clear(block1),
            s1.handsfree(),
            Not(s2.stacked(block1, block2)),
            s2.hand(block1),
            Not(s2.clear(block1)),
            s2.clear(block2),
            Not(s2.handsfree())
        )
    ))
    return And(constraints)