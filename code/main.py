# Python file. 

import json
from jsonschema import validate
from rich import print, print_json
import config
from pathlib import Path
from typing import overload

# Langchain chain creation

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, SecretStr, ValidationError

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

parrent_directory = Path(__file__).resolve().parent

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

    for i in plan[plan]:
        try: 
            result = chain.invoke({
                "spec": f"do: {i} . The full blueprint of the programm : {blueprint_str}"
            })
        except RuntimeError as e:
            print("Couldnt generate the code file. Retrying")
            print(f"error {e}")
            try:
                result = chain.invoke({
                    "spec": f"do: {i} . The full blueprint of the programm : {blueprint_str}"
                })
            except RuntimeError as e2:
                print("Couldnt Generate the code file. ")
                print("Failed to generate codefiles. Lanchain chain couldnt complete")
                print(e2)
                return False
            else:
                print("it actually sucseeded on second attempt. Still throuwing an warning")
                print("The first time failed for some reason. ")
        else:
            print("results generated")
        if config.verbosity >= 2:
            print(result)
        
        results.append(result)
        
        print(f"Outputting into directory {parrent_directory}/{result.filename}")

        try:
            file_name: Path = parrent_directory / result.filename #FIXME: I dont trust this shit
            file_name.write_text(result.content)

        except IOError as e:
            print("couldnt write the answer. ")
            print(e)

    return True

@overload
def validate_input_schemas(blueprint_path: str, plan_path: str) -> bool: ...
@overload
def validate_input_schemas(blueprint_path: str, plan_path: None) -> bool: ...
@overload
def validate_input_schemas(blueprint_path: None, plan_path: str) -> bool: ...
def validate_input_schemas(blueprint_path, plan_path) -> bool:
    """
    This function validates the blueprint and or plan schemas
    YOU MUST PROVIDE AT LEAST ONE OF THOSE
    """
    RESULT = True
    if blueprint_path is not None:
        with open(f"{parrent_directory}/../blueprint.schema.json", "r") as f:
            blueprint_schema = json.load(f)
        with open(blueprint_path, "r") as f:
            blueprint = json.load(f)
        try:
            validate(instance=blueprint, schema=blueprint_schema)
        except ValidationError as e:
            print("validation failed")
            print(e)
            RESULT = False

    if plan_path is not None:
        with open(f"{parrent_directory}/../plan.schema.json", "r") as f:
            plan_schema = json.load(f)
        with open(plan_path, "r") as f:
            plan = json.load(f)
        try:
            validate(instance=plan, schema=plan_schema)
        except ValidationError as e:
            print("validation failed")
            print(e)
            RESULT = False

    return RESULT

def compile_text_to_spec(path_to_text: str, output_path: str | None = None) -> str | bool:
    """
    This is the text to spec compilation pipeline. 
    This one is not deterministic, but Agentic and errores a lot more often. 
    Dont expect deterministic outputs yet.
    """
    OUTPUT_INTO_STDOUT = False
    if output_path is None:
        OUTPUT_INTO_STDOUT = True
    else:
        output_file: Path = Path(output_path)

    with open(path_to_text, "r") as f:
        text = f.read()
    if not OUTPUT_INTO_STDOUT:
        if output_file.exists():
            print("output file exitst. Aborting")
            return False
    result = NotImplementedError("TODO: FINISH") #FIXME: Well, finish this
    try: 
        raise result
    except NotImplementedError:
        raise result
    else:
        print("Its actually implemented")

    if OUTPUT_INTO_STDOUT:
        print(result)
    else:
        output_file.write_text(result)
    


if __name__ == "__main__":
    print("Stupid. This is not supposed to be run directly. ")
    raise RuntimeError("This is not supposed to be run directly. ")
