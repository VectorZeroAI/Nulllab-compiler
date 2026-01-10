# Python file. 

import json
from rich import print, print_json
import requests
import config

def compile(path_to_blueprint: str, path_to_plan: str) -> str:
    """
    This is the main function, the one that compiles the json spec to actual code. 
    I should definetly add some more fields to the plan.json, since what I have there is 100% not enough
    Build info for AI to actually build a correct app. 
    """
    if config.verbosity >= 2:
        print("You have entered the following paths for the json objekts to be compiled:")
    

    try:
        with open(path_to_blueprint, "r") as f:
            blueprint = json.load(f)
        with open(path_to_plan, "r") as f:
            plan = json.load(f)
    except RuntimeError as e:
        print("[red]files could not be loaded[/red]")
        raise RuntimeWarning("files failed to load") from e
    
    if config.verbosity >= 3:
        print("Opened bluepirnt: ")
        print_json(blueprint)
        print("Opened plan: ")
        print_json(plan)

    for i in plan[plan]:
        raise NotImplementedError("Not implemented the actual compiler yet")
        # TODO:: Add the new fields to the json and plan specification. 
        # Make the specification of this repo the upstream one, and make all the other repos load the 
        # Specifications from here.
