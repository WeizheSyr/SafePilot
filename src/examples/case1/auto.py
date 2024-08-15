import json
from verifier import *

import sys
sys.path.append('..')

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
            "name": "save_code",
            "description": "Save the code",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The full runnable code you generated from the description",
                    },
                },
                "required": ["code"],
            },
        }
    ]
func_call_formula = {"name": "save_code"}
model_formula = "gpt-4-turbo"
# model_formula ="gpt-4o"

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
model_plan = "gpt-4-turbo"

formula_path = "first_prompt_formula.txt"
problem_path = "first_prompt_plan.txt"
fol_spec_path = 'fol.py'

llm_formula = Llm(func_formula, func_call_formula, model_formula, api_key)
llm_plan = Llm(func_plan, func_call_plan, model_plan, api_key)
verifier = Verifier(problem_path)

def main():
    first_prompt_formula = llm_formula.get_prompt_from_file(formula_path)
    response_formula, llm_formula.conversation_history = llm_formula.call(first_prompt_formula)
    while True:
        formula_dict = json.loads(response_formula)
        fol_spec = formula_dict["code"]
        print(f"GPT: Here is the formula. Please let me know if this meets the requirements. Please answer yes or no.\n{fol_spec}")
        user_input = input("User: ")
        if user_input.lower() in ['no']:
            if llm_formula.iter_num < 2:
                new_prompt = "This formula does not meet the specification. Please give me the full runnable code."
                response_formula, llm_formula.conversation_history = llm_formula.call(new_prompt)
            else:
                print("GPT: Please write your answer in draft.py. Please answer 'finish' if you finished.")
                while True:
                    user_input = input("User: ")
                    if user_input.lower() == 'finish':
                        break
                with open('draft.py', 'r', encoding='utf-8') as file:
                    fol_spec = file.read()
                break
        else:
            break
    with open(fol_spec_path, 'w', encoding='utf-8') as file:
        file.write(fol_spec)
    

    first_prompt_plan = llm_plan.get_prompt_from_file("first_prompt_plan.txt")
    response_plan, llm_plan.conversation_history = llm_plan.call(first_prompt_plan)
    while True:
        response_plan_dict = json.loads(response_plan)
        plan = response_plan_dict["plan"]
        print(plan)
        verification_result, reason = verifier.verification(plan)
        if not verification_result:
            print(reason)
            if llm_plan.iter_num < 5:
                response_plan, llm_plan.conversation_history = llm_plan.call(reason)
            else:
                print("Reach iteration limit")
                break
        else:
            print("This plan meets the specification.")
            break


if __name__ == "__main__":
    main()