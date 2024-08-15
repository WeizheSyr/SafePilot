from z3 import *
import numpy as np
import re

import sys
import os
current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
grand_path = os.path.dirname(parent_path)
sys.path.append(parent_path)
sys.path.append(grand_path)

from safepilot import Fol_verifier

class Verifier2(Fol_verifier):
    def __init__(self, problem_path):
        super().__init__(problem_path)
        self.roads = self.get_roads()

    # Return problem from raw_problem
    def get_problem(self):
        matches = [match.start() for match in re.finditer(r'\(define', self.raw_problem)]
        if len(matches) >= 2:
            second_define_pos = matches[1]
        problem = self.raw_problem[second_define_pos:]
        return problem

    def get_roads(self):
        roads = re.findall(r'\((\w)-(\w)\)', self.problem)
        road_list = [[start, end] for start, end in roads]
        return road_list
    
    def get_init(self):
        start_index = self.problem.find("(:init") + len("(:init")
        end_index = self.problem.find("(:goal")
        init_content = self.problem[start_index:end_index].strip()
        init_lines = init_content.strip("()").splitlines()
        init_lines_clean = [line.strip(" ()") for line in init_lines if line.strip()]
        return init_lines_clean[0]

    def get_goal(self):
        start_index_goal = self.problem.find("(:goal") + len("(:goal")
        end_index_goal = self.problem.rfind(")")
        goal_content = self.problem[start_index_goal:end_index_goal].strip()
        goal_lines = goal_content.strip("()").splitlines()
        goal_lines_clean = [line.strip(" ()") for line in goal_lines if line.strip()]
        return goal_lines_clean[0]

    def get_plan(self):
        pairs = self.raw_plan.split("\n")
        pairs = pairs[1:-1]
        plan = []
        for pair in pairs:
            if '.' in pair:
                elements = pair.split('.', 1)[1].strip()
            if '->' in pair:
                elements = elements.split('->')
            elements = [element.strip() for element in elements]
            plan.append(elements)
        return plan

    def road_constraint(self, from_city, to_city):
        if [from_city, to_city] in self.roads or [to_city, from_city] in self.roads:
            return True
        return False
    
    def city_constraint(self, prev_city, from_city):
        if prev_city == from_city:
            return True
        return False

    def reasoning(self, wrong_steps):
        reason = "The following run is invalid: \n"
        pairs = self.raw_plan.split("\n")[1:-1]
        for i in range(wrong_steps):
            reason += str(pairs[i]) + '\n'
        return reason
    
    def verification(self, plan):
        self.raw_plan = plan
        self.plan = self.get_plan()

        wrong_steps = None

        # Check init
        init_city = self.get_init()
        if init_city != self.plan[0][0]:
            wrong_steps = 1
            reason = self.reasoning(wrong_steps)
            return False, reason

        # Define the solver and check each steps of the plan
        solver = Solver()
        prev_city = None
        for i in range(len(self.plan) - 1):
            from_city = self.plan[i][0]
            to_city = self.plan[i][1]
            solver.add(self.road_constraint(from_city, to_city))
            if i > 0:
                solver.add(self.city_constraint(prev_city, from_city))
            prev_city = to_city
            if solver.check() != sat:
                wrong_steps = i + 1
                reason = self.reasoning(wrong_steps)
                return False, reason
            
        # Check goal
        goal_city = self.get_goal()
        if goal_city != self.plan[-1][-1]:
            wrong_steps = len(self.plan)
            reason = self.reasoning(wrong_steps)
            return False, reason
        
        return True, None


if __name__ == "__main__":
    with open('plan.txt', 'r', encoding='utf-8') as file:
        raw_plan = file.read()
    verifier = Verifier2("first_prompt_plan.txt")
    result, reason = verifier.verification(raw_plan)
    print(reason)
