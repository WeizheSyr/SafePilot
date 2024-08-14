# from fol import *
from z3 import *
import json

class Fol_verifier(object):
    def __init__(self, problem_path):
        self.raw_problem = self.get_raw_problem(problem_path)
        self.problem = self.get_problem()
        self.raw_plan = None
        # list each state, the state changes after the execution of a step
        self.states = None
        # List each step, detailing the action and the associated object
        self.steps = None
        self.plan = None

    # Read raw problem from a file
    def get_raw_problem(self, problem_path):
        with open(problem_path, 'r', encoding='utf-8') as file:
            raw_problem = file.read()
        return raw_problem
    
    # Return problem from raw_problem
    # Customize according to each specific tasks
    def get_problem(self):
        pass
    
    # Return plan list from raw_plan
    # Customize according to each specific tasks
    def get_plan(self):
        pass
    
    # Set states from plan
    # Customize according to each specific tasks
    def set_states(self):
        pass
    
    # Set the initial state
    # Customize according to each specific tasks
    # Return the initial state
    def set_initial_state(self, s):
        pass
    
    # Set the goal state
    # Customize according to each specific tasks
    # Return the goal state
    def is_goal_state(self, s):
        pass
    
    # Populate self.steps based on the obtained plan, 
    # with each entry comprising (action, *args, s_prev, s_next), 
    # representing the action, action objects, previous state, and next state, respectively.
    def set_states(self):
        pass
    
    # Generate reasoning according to wrong_steps
    def reasoning(self, wrong_steps):
        pass

    def verification(self, plan):
        self.raw_plan = plan
        self.plan = self.get_plan()

        # Set states from plan
        self.steps = self.set_states()

        # Instantiate the Z3 solver.
        solver = Solver()

        # set initial state
        solver.add(self.set_initial_state(self.states[0]))

        # verification
        wrong_steps = None
        for i, step in enumerate(self.steps):
            action, *args, s_prev, s_next = step
            solver.add(action(s_prev, s_next, *args))

            # Verify whether each step violates the specifications
            if solver.check() != sat:
                wrong_steps = i + 1
                self.flag = False
                break

        if wrong_steps == None:
            # Check if the final state meets the goal conditions
            solver.add(self.is_goal_state(self.states[-1]))
            if solver.check() == sat:
                # The plan is valid and meet the goal.
                return True, None
            else:
                # The plan does not meet the goal.
                return False, self.reasoning(wrong_steps)
        else:
            return False, self.reasoning(wrong_steps)