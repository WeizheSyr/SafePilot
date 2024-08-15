import json
from verifier import *
from fol_verifier import *

import sys
import os
current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
grand_path = os.path.dirname(parent_path)
sys.path.append(parent_path)
sys.path.append(grand_path)

from safepilot import Llm

# api_key=''

func_formula = [
        {
            "name": "save_formula",
            "description": "Save the formula",
            "parameters": {
                "type": "object",
                "properties": {
                    "formula": {
                        "type": "string",
                        "description": "The formula you generated from the specification",
                    },
                },
                "required": ["formula"],
            },
        }
    ]
func_call_formula = {"name": "save_formula"}
model_formula = "gpt-4-turbo"

func_plan = [
        {
            "name": "save_plan",
            "description": "Save the plan",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan": {
                        "type": "string",
                        "description": "The plan you generated",
                    },
                },
                "required": ["plan"],
            },
        }
    ]
func_call_plan = {"name": "save_plan"}
# model_plan = "gpt-4-turbo"
model_plan ="gpt-4o"

formula_path = "first_prompt_formula.txt"
problem_path = "first_prompt_plan.txt"
reason_path='run1.txt'

llm_formula = Llm(func_formula, func_call_formula, model_formula, api_key)
llm_plan = Llm(func_plan, func_call_plan, model_plan, api_key)
verifier = Verifier(problem_path, reason_path)
fol_verifier = Verifier2(problem_path)

def main():
    first_prompt_formula = llm_formula.get_prompt_from_file(formula_path)
    response_formula, llm_formula.conversation_history = llm_formula.call(first_prompt_formula)
    while True:
        formula_dict = json.loads(response_formula)
        ltl_spec = formula_dict["formula"]
        print(f"GPT: Here is the formula. Please let me know if this meets the requirements. Please answer yes or no.\n{ltl_spec}")
        user_input = input("User: ")
        if user_input.lower() in ['no']:
            if llm_formula.iter_num < 2:
                new_prompt = "This formula does not meet the specification."
                response_formula, llm_formula.conversation_history = llm_formula.call(new_prompt)
            else:
                print("GPT: Please enter the correct formula.")
                ltl_spec = input("User: ")
                break
        else:
            break

    first_prompt_plan = llm_plan.get_prompt_from_file("first_prompt_plan.txt")
    response_plan, llm_plan.conversation_history = llm_plan.call(first_prompt_plan)
    while True:
        # Extract raw plan from response_plan
        response_plan_dict = json.loads(response_plan)
        raw_plan = response_plan_dict["plan"]
        print(raw_plan)
        verification_result1, reason1 = verifier.verification(ltl_spec, raw_plan)
        verification_result2, reason2 = fol_verifier.verification(raw_plan)
        if verification_result1 and verification_result2:
            print("This plan meets the specification.")
            break
        if not verification_result1 and verification_result2:
            reason = reason1
        if verification_result1 and not verification_result2:
            reason = reason2
        else:
            if len(reason) > len(reason2):
                reason = reason2
            else:
                reason = reason1
        print(reason)
        if llm_plan.iter_num < 4:
            response_plan, llm_plan.conversation_history = llm_plan.call(reason)
        else:
            print("Reach iteration limit")
            break


if __name__ == "__main__":
    main()