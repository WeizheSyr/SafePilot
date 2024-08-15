import spot
spot.setup()
from buddy import bdd_ithvar
import numpy as np
import re

import sys
import os
current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
grand_path = os.path.dirname(parent_path)
sys.path.append(parent_path)
sys.path.append(grand_path)

from safepilot import LTL_Verifier

class Verifier(LTL_Verifier):
    def __init__(self, problem_path, reason_path='run.txt'):
        super().__init__(problem_path, reason_path)

    # Return atomic proposition list from problem
    def get_aps(self):
        # Extract aps using re
        matches = re.findall(r'\(:cities\s+([A-Z\s]+)\)', self.raw_problem)
        # Select the correct objects
        if matches and len(matches) > 1:
            aps = matches[1].split()
        for i in range(len(aps)):
            aps[i] = aps[i].lower()
        return np.array(aps)

    # Return plan list from raw_plan
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

    # Return state list
    def get_states(self, bdd_ithvar_list):
        states = []
        # Express whether a city has been visited
        visited = np.zeros(len(self.aps))
        # Start city
        position = np.where(self.aps == self.plan[0][0].lower())
        visited[position] = 1
        states.append(self.get_state_from_visited(visited, bdd_ithvar_list))
        # Each steps
        for i in range(len(self.plan)):
            position = np.where(self.aps == self.plan[i][1].lower())
            visited[position] = 1
            states.append(self.get_state_from_visited(visited, bdd_ithvar_list))
        return states
    
    # Get single state from visited list
    def get_state_from_visited(self, visited, bdd_ithvar_list):
        state = None
        for i in range(len(self.aps)):   
            if visited[i] == 1:
                if i == 0:
                    state = bdd_ithvar_list[0]
                else:
                    state = state & bdd_ithvar_list[i]
            else:
                if i == 0:
                    state = -bdd_ithvar_list[0]
                else:
                    state = state & -bdd_ithvar_list[i]
        return state
    
    def reasoning(self, wrong_steps):
        reason = "The following run is invalid: \n"
        pairs = self.raw_plan.split("\n")
        for i in range(wrong_steps + 1):
            if i != 0:
                reason += str(pairs[i]) + "\n"
        return reason
        
# if __name__ == "__main__":
#     with open('plan.txt', 'r', encoding='utf-8') as file:
#         raw_plan = file.read()
#     verifier = Verifier("first_prompt_plan.txt", "run.txt")
#     result, reason = verifier.verification(raw_plan)
#     print("Reason")
#     print(reason)
