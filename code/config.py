# Config for the compiler
# IGNOTE THIS
from pathlib import Path
# IGNORE THIS

# You may change from here: ----------

# verbosity of the output, e.g. how much you want it to spit into the terminal
verbosity: int = 1 
# We use OPENROUTER api key. 
api_key: str = ""
prompt_version: str = "0.1" 
model: str = "model here"

# To here: ------------------------

# DONT TOUCH THE PART BELOW
# genuenly, DONT! I just write the config that way for now. 

class prompt:
    if prompt_version == "0.1":
        prompt = """
        You are an deterministic compiler. 
        Your task is to execute what plan.json states. 
        Blueprint.json is the full programm description.
        YOU MUST FOLLOW THE 
        """
    if prompt_version == "1":
        BASE = Path(__file__).resolve().parent
        with open(f"{BASE / prompt.txt}", "r") as file:
            prompt = file.read()
