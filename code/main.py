# Python file. 

import json
from rich import print, print_json
import config
from pathlib import Path

# Langchain chain creation

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, SecretStr

# output Schema definitions. 
class CodeFile(BaseModel):
    """
    Returned objekt for the parser
    """
    filename: str
    content: str

parser = PydanticOutputParser(pydantic_object=CodeFile)
prompt = ChatPromptTemplate.from_messages([
    ("system", f"{config.prompt.prompt}" ),
    ("human",
     """
     JSON SOURSE: \n{spec}\n\n{format_instructions}
     """)
    ])

llm = ChatOpenAI(
    model=config.model,
    temperature=0,
    api_key=SecretStr(config.api_key),
    base_url="https://openrouter.ai/api/v1"
    )

chain = prompt | llm | parser

# Main function
def compile(path_to_blueprint: str, path_to_plan: str) -> bool:
    """
    This is the main function, the one that compiles the json spec to actual code. 
    I should definetly add some more fields to the plan.json, since what I have there is 100% not enough
    Build info for AI to actually build a correct app. 
    from langchain.output_parsers import PydanticOutputParser
    """
    if config.verbosity >= 2:
        print("You have entered the following paths for the json objekts to be compiled:")

    # JSON loading
    try:
        with open(path_to_blueprint, "r") as f:
            blueprint = json.load(f)
            blueprint_str = str(blueprint)
        with open(path_to_plan, "r") as f:
            plan = json.load(f)
    except IOError as e:
        print("[red]files could not be loaded[/red]")
        raise IOError("files failed to load") from e
    
    if config.verbosity >= 3:
        print("Opened blueprint: ")
        print_json(blueprint)
        print("Opened plan: ")
        print_json(plan)

    results = []

    parrent_directory = Path(__file__).resolve().parent

    for i in plan[plan]:
        try: 
            result = chain.invoke({
                "spec": f"do: {i} . The full blueprint of the programm : {blueprint_str}"
            })
        except RuntimeError as e:
            print("Couldnt generate the code file. Retrying")
            try:
                result = chain.invoke({
                    "spec": f"do: {i} . The full blueprint of the programm : {blueprint_str}"
                })
            except RuntimeError as e2:
                print("Couldnt Generate the code file. ")
                return False
            else:
                print("it actually sucseeded on second attempt. Still throuwing an warning")
                raise RuntimeWarning("The first time failed for some reason. ")
        if config.verbosity >= 2:
            print(result)
        
        results.append(result)
        
        try:
            file_name: Path = parrent_directory / result.filename #FIXME: I dont trust this shit
            file_name.write_text(result.content)

        except IOError as e:
            print("couldnt write the answer. ")

    return True
