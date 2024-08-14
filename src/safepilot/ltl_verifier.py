import spot
spot.setup()
from buddy import bdd_ithvar
import numpy as np

class LTL_Verifier(object):
    def __init__(self, problem_path, reason_path='run.txt'):
        self.raw_plan = None
        self.plan = []
        # Read raw problem from a file
        self.raw_problem = self.get_problem(problem_path)
        # Atomic proposition list from raw_problem
        self.aps = self.get_aps()
        # LTL formula
        self.formula = None
        # !formula
        self.aformula = None
        self.d = spot.make_bdd_dict()
        self.states = None
        self.kripke = None
        self.reasoning_kripke = None
        self.reason_path = reason_path

    # Read raw problem from a file
    def get_problem(self, problem_path):
        with open(problem_path, 'r', encoding='utf-8') as file:
            raw_problem = file.read()
        return raw_problem

    # Return atomic proposition list from problem
    # Customize according to each specific tasks
    def get_aps(self, problem_path):
        pass
    
    # Return plan list from raw_plan
    # Customize according to each specific tasks
    def get_plan(self):
        pass

    # Return !formula
    def get_aformula(self):
        aparsed_formula = spot.formula.Not(self.formula)
        # aformula = spot.translate(self.formula, dict=self.d)
        aformula = spot.translate(aparsed_formula, dict=self.d)
        return aformula
    
    # Return state list
    # Customize according to each specific tasks
    def get_states(self, bdd_ithvar_list):
        pass

    def create_kripke(self, bdddict, name_states=False):
        kripke = spot.make_kripke_graph(bdddict)

        # create a bdd_ithvar list to hold the proposition
        bdd_ithvar_list = []
        for ap in self.aps:
            bdd_ithvar_list.append(bdd_ithvar(kripke.register_ap(ap.lower())))
        
        # Add states and transitions to the Kripke graph
        self.states = self.get_states(bdd_ithvar_list)
        # States list in current kripke
        kripke_states = []
        for state in self.states:
            kripke_states.append(kripke.new_state(state))
        
        # Set initial state
        kripke.set_init_state(kripke_states[0])

        # Add edges
        for i in range(len(self.states) - 1):
            kripke.new_edge(kripke_states[i], kripke_states[i + 1])
        # Add a cycle 
        kripke.new_edge(kripke_states[len(self.states) - 1], kripke_states[len(self.states) - 1])
        return kripke
    
    def intersect(self, kripke, aformula, save_run=False):
        run = kripke.intersecting_run(aformula)
        if run:
            result = False
            # print(run)
            if save_run:
                # print("Formula is violated.")
                with open(self.reason_path, 'w', encoding='utf-8') as file:
                    print(run, file=file)
        else:
            # print("Formula is verified")
            result = True
        return result
    
    def create_reasoning_kripke(self, bdddict, name_states=False):
        kripke = spot.make_kripke_graph(bdddict)

        # create a list to hold the proposition
        bdd_ithvar_list = []
        for ap in self.aps:
            bdd_ithvar_list.append(bdd_ithvar(kripke.register_ap(ap.lower())))
        
        # Add states and transitions to the Kripke graph
        self.states = self.get_states(bdd_ithvar_list)
        # States list in current kripke
        kripke_states = []
        for state in self.states:
            kripke_states.append(kripke.new_state(state))
        
        # Set initial state
        kripke.set_init_state(kripke_states[0])

        # Add edges
        for i in range(len(self.states) - 1):
            kripke.new_edge(kripke_states[i], kripke_states[i + 1])
            kripke.new_edge(kripke_states[i + 1], kripke_states[i + 1])
        # Add a cycle 
        kripke.new_edge(kripke_states[len(self.states) - 1], kripke_states[len(self.states) - 1])
        return kripke
    
    def get_wrong_steps(self):
        with open(self.reason_path, 'r', encoding='utf-8') as file:
            run_info = file.read()
        prefix_content = run_info.split("Cycle:")[0]
        num_pipes = prefix_content.count('|')
        wrong_step = num_pipes - 1
        return wrong_step

    # Generate reason according to the wrong steps
    # Customize according to each specific tasks
    def reasoning(self, wrong_steps):
        pass

    def verification(self, formula, raw_plan):
        self.formula = formula
        self.raw_plan = raw_plan
        self.plan = self.get_plan()
        self.aformula = self.get_aformula()
        self.kripke = self.create_kripke(self.d, True)
        result = self.intersect(self.aformula, self.kripke)

        # provide reasoning if invalid
        if not result:
            self.reasoning_kripke = self.create_reasoning_kripke(self.d, True)
            result = self.intersect(self.aformula, self.reasoning_kripke, save_run=True)
            wrong_steps = self.get_wrong_steps()
            reason = self.reasoning(wrong_steps)
            return result, reason
        else:
            return result, None
