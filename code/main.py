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


parent_directory = Path(__file__).resolve().parent

# Configs

# TODO: Add the config values here. 

# Main function
def compile_json_to_code(path_to_blueprint: str, path_to_plan: str) -> bool:
    """
    This is the main function, the one that compiles the json spec to actual code. 
    I should definitely add some more fields to the plan.json, since what I have there is 100% not enough
    Build info for AI to actually build a correct app. 
    from langchain.output_parsers import PydanticOutputParser
    """
    # Langchain chain creation

    # output Schema definitions. 
    class CodeFile(BaseModel):
        """
        Returned object for the parser
        """
        filename: str
        content: str

    parser = PydanticOutputParser(pydantic_object=CodeFile)
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"{config.Prompt.prompt}" ),
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
    if config.verbosity >= 2:
        print("You have entered the following paths for the json objekts to be compiled:")

    # JSON loading
    try:
        with open(path_to_blueprint, "r") as f:
            blueprint = json.load(f)
            blueprint_str = json.dumps(blueprint)
        with open(path_to_plan, "r") as f:
            plan = json.load(f)
    except Exception as e:
        print("[red]files could not be loaded[/red]")
        raise RuntimeError("files failed to load") from e
    
    if config.verbosity >= 3:
        print("Opened blueprint: ")
        print_json(blueprint)
        print("Opened plan: ")
        print_json(plan)

    results = []

    for i in plan["plan"]:
        try: 
            result = chain.invoke({
                "spec": f"do: {i} . The full blueprint of the program : {blueprint_str}"
            })
        except Exception as e:
            print("Couldnt generate the code file. Retrying")
            print(f"error {e}")
            try:
                result = chain.invoke({
                    "spec": f"do: {i} . The full blueprint of the program : {blueprint_str}"
                })
            except Exception as e2:
                print("Couldnt Generate the code file. ")
                print("Failed to generate codefiles. Lanchain chain couldnt complete")
                print(e2)
                return False
            else:
                print("it actually succeeded on second attempt. Still throwing an warning")
                print("The first time failed for some reason. ")
        else:
            print("results generated")
        if config.verbosity >= 2:
            print(result)
        
        results.append(result)
        
        print(f"Outputting into directory {parent_directory}/{result.filename}")

        try:
            file_name: Path = parent_directory / result.filename #FIXME: I dont trust this shit
            file_name.write_text(result.content)

        except IOError as e:
            print("couldnt write the answer. ")
            print(e)

    return True

@overload
def validate_input_schemas(blueprint_path: str, plan_path: str, blueprint_json: None, plan_json: None) -> bool | str: ...
@overload
def validate_input_schemas(blueprint_path: str, plan_path: None, blueprint_json: None, plan_json: None) -> bool | str: ...
@overload
def validate_input_schemas(blueprint_path: None, plan_path: str, blueprint_json: None, plan_json: None) -> bool | str: ...
@overload
def validate_input_schemas(blueprint_path: None, plan_path: None, blueprint_json: dict, plan_json: dict) -> bool | str: ...
@overload
def validate_input_schemas(blueprint_path: None, plan_path: None, blueprint_json: dict, plan_json: None) -> bool | str: ...
@overload
def validate_input_schemas(blueprint_path: None, plan_path: None, blueprint_json: None, plan_json: dict) -> bool | str: ...
@overload
def validate_input_schemas(blueprint_path: str, plan_path: None, blueprint_json: None, plan_json: dict) -> bool | str: ...
@overload
def validate_input_schemas(blueprint_path: None, plan_path: str, blueprint_json: dict, plan_json: None) -> bool | str: ...
def validate_input_schemas(blueprint_path, plan_path, blueprint_json, plan_json) -> bool | str:
    """
    This function validates the blueprint and or plan schemas
    YOU MUST PROVIDE AT LEAST ONE OF THOSE
    """
    result_plan = False
    result_blueprint = False

    with open(f"{parent_directory}/../plan.schema.json", "r") as f:
        plan_schema = json.load(f)

    with open(f"{parent_directory}/../blueprint.schema.json", "r") as f:
        blueprint_schema = json.load(f)

    if blueprint_path is not None:
        with open(blueprint_path, "r") as f:
            blueprint = json.load(f)
        try:
            validate(instance=blueprint, schema=blueprint_schema)
        except ValidationError as e:
            print("validation failed")
            print(e)
        else:
            result_blueprint = True

    if plan_path is not None:
        with open(plan_path, "r") as f:
            plan = json.load(f)
        try:
            validate(instance=plan, schema=plan_schema)
        except ValidationError as e:
            print("validation failed")
            print(e)
        else:
            result_plan = True

    if plan_json is not None:
        try:
            validate(instance=plan_json, schema=plan_schema)
        except ValidationError as e:
            print("validation failed")
            print(e)
        else:
            result_plan = True
    if blueprint_json is not None:
        try:
            validate(instance=blueprint_json, schema=blueprint_schema)
        except ValidationError as e:
            print("validation failed")
            print(e)
        else:
            result_blueprint = True
    
    if result_plan and result_blueprint:
        return True
    elif result_plan or result_blueprint:
        return "one of them"
    elif not result_plan and not result_blueprint:
        return False
    return "The fuck happened here ? ... Actually, I will still leave this here, to make my LSP happy."

def compile_text_to_spec(path_to_text: str, output_path: str | None = None) -> bool:
    """
    This is the text to spec compilation pipeline. 
    This one is not deterministic, but Agentic and errores a lot more often. 
    Dont expect deterministic outputs yet.
    """
    # Langchain chain creation
    class SpecFile(BaseModel):
        """
        Pydantic objekt for the output
        """
        blueprint: dict
        plan: dict

    with open(f"{parent_directory}/../blueprint.schema.json", "r") as f:
        blueprint_schema = json.load(f)

    with open(f"{parent_directory}/../plan.schema.json", "r") as f:
        plan_schema = json.load(f)

    parser = PydanticOutputParser(pydantic_object=SpecFile)
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a text to spec compiler. Your task is to output 2 structured files: plan and blueprint.
                    You must output valid json only. The json is only valid if it followes this schema. 
                    Blueprint schema:
                        {blueprint_schema}
                    plan schema:
                        {plan_schema}
        """ ), 
        ("human",
         """
            TEXT: \n{text}\n
         """)
        ])

    llm = ChatOpenAI(
        model=config.model,
        temperature=0.3,
        api_key=SecretStr(config.api_key),
        base_url="https://openrouter.ai/api/v1"
        )

    chain = prompt | llm | parser

    OUTPUT_INTO_STDOUT = False
    if output_path is None:
        OUTPUT_INTO_STDOUT = True
        output_file: Path = Path("") # dummy
    else:
        output_file: Path = Path(output_path)


    with open(path_to_text, "r") as f:
        text = f.read()

    # Check for quick exit
    if not OUTPUT_INTO_STDOUT:
        if output_file.exists():
            print("output file exitst. Aborting")
            return False
    # Actually result generation
    try:
        result = chain.invoke({
            "text": text
        })
    except RuntimeError as e:
        print(f"errored out. Error: {e}")
        print("trying again")
        try:
            result = chain.invoke({
                "text": text
            })
        except RuntimeError as e:
            print("failed again. ")
            print("erroring out")
            return False
        else:
            print("for some reason it actually worked now.")
    else:
        print("result was sucsessfully generated. ")

    # Actual Output
    if OUTPUT_INTO_STDOUT:
        try:
            print(str(result))
        except RuntimeError as e:
            print("couldnt write to the STDOUT. ")
            print(f"{e}")
            return False
        return True
    else:
        try:
            output_file.write_text(result.json()) # FIXME: split the answer into plan.json and blueprint.json 
        except IOError as e:
            print("couldnt write to the file. ")
            print(f"error: {e}")
            print("trying again")
            try:
                output_file.write_text(result.json()) # FIXME: split the answer into plan.json and blueprint.json 
            except IOError as e:
                print("Couldnt write to the file")
                print(f"error: {e}")
                print("erroring out")
                return False
    print("wrote into the file")
    return True

    
if __name__ == "__main__":
    print("Stupid. This is not supposed to be run directly. ")
    raise RuntimeError("This is not supposed to be run directly. ")
