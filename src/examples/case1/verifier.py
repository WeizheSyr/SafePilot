import re
from draft import *

import sys
import os
current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
grand_path = os.path.dirname(parent_path)
sys.path.append(parent_path)
sys.path.append(grand_path)

from safepilot import Fol_verifier
# from fol import *

class Verifier(Fol_verifier):
    def __init__(self, problem_path):
        super().__init__(problem_path)
        self.num_blocks = self.get_num_blocks()

    # Return problem from raw_problem
    def get_problem(self):
        matches = [match.start() for match in re.finditer(r'\(define', self.raw_problem)]
        if len(matches) >= 2:
            second_define_pos = matches[1]
        problem = self.raw_problem[second_define_pos:]
        return problem

    # Get the num of blocks from the problem
    def get_num_blocks(self):
        # Extract (:objects ...) from the problem
        objects = re.findall(r'\(:objects (.+?)\)', self.problem)
        objects_list = objects[0].split() if objects else []
        num_objects = len(objects_list)
        return num_objects

    # Extract plan list from raw_plan
    def get_plan(self):
        plan = self.raw_plan.split('\n')[1:-1]
        return plan
    
    # Parse block name to int
    def parse_block_name(self, block_name):
        # block_name: b1, b2,... to 1, 2, ...
        return int(block_name[1:])

    # Set states from plan
    def set_states(self):
        # Fill in the action you defined
        action_map = {
            "unstack": unstack,
            "put-down": put_down,
            "pick-up": pick_up,
            "stack": stack
        }

        # Initialize states for each step
        self.states = [State(f"s{i}", self.num_blocks) for i in range(len(self.plan) + 1)]

        # Define the steps according to the provided plan
        steps = []
        for i, step in enumerate(self.plan):
            parts = step.split()
            action = parts[1]
            if action in ["pick-up", "put-down"]:
                block = self.parse_block_name(parts[2]) # Extract the block number
                steps.append((action_map[action], block, self.states[i], self.states[i + 1]))
            elif action in ["stack", "unstack"]:
                block1 = self.parse_block_name(parts[2])  # Extract the first block number
                block2 = self.parse_block_name(parts[3]) # Extract the second block number
                steps.append((action_map[action], block1, block2, self.states[i], self.states[i + 1]))
        return steps
    
    # Set the initial state
    def set_initial_state(self, s):
        # Find the objects
        start_obj = self.problem.find("(:objects") + len("(:objects")
        end_obj = self.problem.find("(:init")
        obj_content = self.problem[start_obj:end_obj].strip()
        obj_lines = obj_content.strip("()").splitlines()
        objs = obj_lines[0].split()
        for i in range(len(objs)):
            objs[i] = self.parse_block_name(objs[i])
        unclear_list = objs

        # Extract init state from problem
        start_index = self.problem.find("(:init") + len("(:init")
        end_index = self.problem.find("(:goal")
        init_content = self.problem[start_index:end_index].strip()
        init_lines = init_content.strip("()").splitlines()
        init_lines_clean = [line.strip(" ()") for line in init_lines if line.strip()]

        clauses = []
        for statement in init_lines_clean:
            parts = statement.split()
            if parts[0] == 'arm-empty':
                clauses.append(s.handsfree())
            elif parts[0] == 'on':
                b1 = self.parse_block_name(parts[1])
                b2 = self.parse_block_name(parts[2])
                clauses.append(s.stacked(b1, b2))
            elif parts[0] == 'on-table':
                b = self.parse_block_name(parts[1])
                clauses.append(s.table(b))
            elif parts[0] == 'clear':
                b = self.parse_block_name(parts[1])
                clauses.append(s.clear(b))
                unclear_list.remove(b)
        # set up unclear blocks
        for item in unclear_list:
            clauses.append(Not(s.clear(item)))
        return And(*clauses)
    
    # Set the goal state
    def is_goal_state(self, s):
        # Extract goal state from problem
        start_index_goal = self.problem.find("(:goal") + len("(:goal")
        end_index_goal = self.problem.rfind(")")
        goal_content = self.problem[start_index_goal:end_index_goal].strip()
        goal_lines = goal_content.strip("()").splitlines()
        goal_lines_clean = [line.strip(" ()") for line in goal_lines if line.strip() and line.strip() != "and"]

        clauses = []
        for statement in goal_lines_clean:
            parts = statement.split()
            if parts[0] == 'arm-empty':
                clauses.append(s.handsfree())
            elif parts[0] == 'on':
                b1 = self.parse_block_name(parts[1])
                b2 = self.parse_block_name(parts[2])
                clauses.append(s.stacked(b1, b2))
            elif parts[0] == 'on-table':
                b = self.parse_block_name(parts[1])
                clauses.append(s.table(b))
            elif parts[0] == 'clear':
                b = self.parse_block_name(parts[1])
                clauses.append(s.clear(b))
        return And(*clauses)

    def reasoning(self, wrong_steps):
        if wrong_steps == None:
            # The plan does not meet the goal.
            reason = "The plan does not meet the goal."
        else:
            # The plan has invalid steps.
            reason = ""
            for i in range(wrong_steps):
                reason += str(self.plan[i]) + '\n'
            reason += "The plan is invalid according to the steps above."
        return reason

if __name__ == "__main__":
    verifier = Verifier("first_prompt_plan.txt")
    # raw_plan = "START-PLAN\n1. unstack b4 b1\n2. put-down b4\n3. unstack b1 b6\n4. put-down b1\n5. pick-up b6\n6. stack b6 b4\n7. pick-up b5\n8. stack b5 b3\n9. pick-up b1\n10. stack b1 b2\nEND-PLAN"
    raw_plan = "START-PLAN\n1. unstack b4 b1\n2. put-down b4\n3. unstack b1 b6\n4. put-down b1\n5. pick-up b6\n6. stack b6 b4\n7. unstack b2 b3\n8. put-down b2\n9. pick-up b5\n10. stack b5 b3\n11. pick-up b1\n12. stack b1 b2\nEND-PLAN"
    result, reason = verifier.verification(raw_plan)
    print(raw_plan)
    print(reason)