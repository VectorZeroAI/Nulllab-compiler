# Nulllab-compiler
The compiler for my NullLab-mini, and future NullLab-full projekts. 

## Input

It takes 2 files as input, e.g. 2 paths : 
blueprint.json path and plan.json path .

## Output

The output code is put into the **./output_code** dir, with each file being a file. 

## Guidelines 

Generally, each step of plan.json should output 1 file. 
A step can not output 2 files. 
A step may output 0 new files, but that kind of behaviour confuses the AI, so its not ideomatic. 

## Architecture

There is a cli way to call it, and an importable python executable. 
The programm is written in python. 

> [!NOTE]
> It will be hella slow due to using OpenRouter API, but I also plan to add google gemini api, as well as other apis support. 

