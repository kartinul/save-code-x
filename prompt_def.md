Developer: You are provided with multiple program source files. For each file, you will receive only the input-handling lines: those using scanf, fgets, gets, or any function that reads from stdin.

Your task is to infer the complete stdin input required for each program to run, based strictly on the explicit input calls.

OUTPUT REQUIREMENTS:

• Return a single JSON object.
• Each key must be the exact filename, including extension (e.g., "1.c").
• Each value must be an array of 1–3 complete stdin sessions.
• Each stdin session must:
– contain only inputs explicitly consumed by input calls
– follow the exact order of execution
– use "\n" to represent Enter
• If the program has no input calls, the value must be [].
• If the program has only one possible execution path, provide exactly one session.
• If the program can clearly execute in different valid ways (e.g., branching based on input, type selectors, sentinel loops), provide up to three distinct sessions that meaningfully demonstrate those paths.

STRICT CONSTRAINTS:

• Never invent or assume extra input.
• Never add inputs for printf or prompts.
• Never reorder or merge inputs.
• For format strings with required separators (e.g., "%f,%f"), inputs must include them.
• For loops:
– repeat inputs exactly as many times as the loop executes
– if loop bounds depend on input, use the supplied value consistently
– for sentinel or branching loops, include at least one terminating case
• For conditional input:
– only include conditional reads when conditions are satisfied by previous inputs
– provide different sessions only when the code meaningfully diverges
• Use the most conservative interpretation if ambiguous.

OUTPUT FORMAT:

Return ONLY valid JSON — no commentary, no explanation, no Markdown.

Example formatting:

{
"file1.c": ["3\n2\n2\n"],
"calc.c": ["1\n2\n+\n", "5\n9\n-\n"]
}

think hard about it and give me a sensible JSON which showes all the aspects of my programs
ONLY give the JSON with no formatting including `json ` or any other text
