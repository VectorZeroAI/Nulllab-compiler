# The doc for the compiler pipeline. 

the compiler will be spawning an autonome agent per plan step, wich would output the code for that step. 
It will be doing that via creating a langchain Agent, with the task to do so. 
More details on that in the section "Agent"

## Agent

An agent is composed of tools and text. 
A fancy way to describe text is "prompt"
But because its basicaly text, I will not treat it as a prompt, but rather as a blob of text data. 
So, the blob of text data that the agent becomes is its core. 
Everything else us basically just a prebuilt coding agent I will yank from Langchain. 

### Blob of text data

Its composed of:
    - The generall instructions
    - all of the step from inside plan.json
    - all of blueprint.json

> [!NOTE]
> Its not getting the actual codebase fed. Only json spec files. 

#### General Instructions

They are just the prompt that is gonna enhanse the Agents performance as a compiler. 
Example prompt:
```txt
You are an compiler. You are to output exatly what you are told, deterministially, with no fluf, and no creativity, unpredictability, and own self-added parts. 
You must follow the provided json specifications.
You must not get out of scope. 
You must stay inside the scope of plan.json
You must try to generate deterministic, simple, straitforward code from the json spec provided. 
You must follow plan.json and blueprint.json 
``` 

> [!NOTE]
> This prompt will 100% need future refactoring, this is just an example. 

#### the jsons

The jsons are provided as is, and are not to be questioned. 
Hoever, if any inconsistansy or a paradox occures, the compiler must refuse the JSONs, and tell the user to fix the issue. 
The schemas are part of the repo, so they are the first guard rail. 
The second guard rail is AI based validation. 
An agent must iterate through the JSONs step by step, and try to catch any inconsistansy. 
But because we cant guarantie that the agents output was correct, we will only through a warning, and not an error. 

Finaly, the jsons are planned to be deterministic enough for the AI to output code consistantly enough, that it works like a compiler. 

# Some thoughts 

Generally speaking, I dont neseseraly think that AI is really nesesery in this scenario. If I were to actually try, I think I could write an compiler to an actual languege even without AI, with just an translation algoritm. 
