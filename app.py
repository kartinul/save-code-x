import os
import shlex
import subprocess
import systask
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

inputScan = ("gets", "fgets", "scanf")
toScan = ("printf", "gets", "fgets", "scanf", "puts")
EXTENTION = ".c"
COMPILE_STR = "gcc $s.c -o $s"
RUN_STR = "$s.exe"

pathStr = "C:/Users/karti/Desktop/Code/TRY/C/week9/"
path = os.fsencode(pathStr)

contents = {}


def sort_key(name):
    fileName = os.fsdecode(name)
    num_part = "".join(ch for ch in fileName if ch.isdigit())
    if num_part.isdigit():
        return (0, int(num_part))
    else:
        return (1, fileName.lower())


listDir = os.listdir(path)
listDir.sort(key=sort_key)

cases = {}
for name in listDir:
    fileName = os.fsdecode(name)
    if fileName.endswith(EXTENTION):
        fileNameOnly = fileName.split(".")[0]
        with open(pathStr + fileName, "r", encoding="utf-8") as f:
            content = f.read()
            contents[fileNameOnly] = content
            matchedLines = [
                line
                for line in content.split("\n")
                if any(word in line for word in inputScan)
            ]
            cases[fileNameOnly] = matchedLines

prompt = """
You are given multiple program files in any programming language.  
Each file listing includes only the I/O-related lines (e.g. print, input, scanf, cin, readline, prompt, etc.).  
Your task is to infer what the user is supposed to type into the terminal when running that program, and generate 1-2 realistic example input sets per file.
For example: if the input takes a string, enter a string. if it takes a float, enter a float. 
And for example: if the final output is something like armstrong number or something similar... give 2 realistic examples. With 1 satisfying and 1 not.
Otherwise 1 is fine!

OUTPUT FORMAT RULES (MUST FOLLOW EXACTLY)
1. Output only valid JSON.
2. JSON structure:
   {
     "filename": ["input example 1", "input example 2"],
     "filename2": ["input example 1"],
     "filename3": []
   }
   (filename 3 has no input source)
3. Each string inside the array represents one full example of what the user would type in the terminal — use "\\n" for newlines.
4. Do not include any outputs, file names, comments, or explanations.
5. If a file requires no input, return an empty array for it.
6. Inputs must look like what a real person would type based on the prompts and code context.
7. Keep the examples practical, human-like, and consistent with likely variable types and constraints.
8. Do not use markdown, triple backticks, or text before/after JSON.
9. If the language uses typed input (like scanf, cin, or Python input→int), infer the type and give proper values (no dummy text unless strings are expected).
10. If you enter the length of some array as 5, make sure you have 5 elements in it!

GOAL
Return a JSON object that's easy to parse and can be directly used to feed realistic input values into each program for testing.

Now process the following files exactly as given:

"""
for baseFileName, ioList in cases.items():
    prompt += baseFileName + EXTENTION + "\n"

    for io in ioList:
        prompt += io + "\n"

    prompt += "\nEND\n"


client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
response = (
    client.responses.create(model="gpt-4o-mini", input=prompt).output[0].content[0].text
)

for baseFileName in cases:

    compileArgs = shlex.split(COMPILE_STR.replace("$s", pathStr + baseFileName))

    runArgsStr = RUN_STR.replace("$s", pathStr + baseFileName)

    # compile
    subprocess.run(compileArgs)
    print(baseFileName, ", ")

    inputs = response[baseFileName + EXTENTION]
    if len(inputs) == 0:
        systask.run_and_type_in_exe(runArgsStr, "", baseFileName)

    for i, inp in enumerate(inputs):
        systask.run_and_type_in_exe(runArgsStr, inp, f"{baseFileName}({i})")
