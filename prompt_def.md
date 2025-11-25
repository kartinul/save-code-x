Developer: You are provided with multiple C source files. For each file, you will receive only the input-handling lines: those utilizing scanf, fgets, gets, or any function that consumes stdin. Your tasks and requirements are as follows:
If a program can accept different valid input paths, provide up to three distinct complete stdin sessions, as long as all inputs strictly correspond to explicit input calls.
Do not default to a single session when multiple valid execution paths clearly exist.

**Output:**
Output a single JSON object structured as follows:

- Each key is the exact filename (e.g., "1.c").
  - Each string represents one complete stdin session for a single program run.
  - Use "\n" within each string to represent the Enter key.
  - If a file has ZERO input calls, the value is an empty array [].

**Strict Constraints:**

- NEVER invent or supplement inputs. Only inputs needed by explicit scanf/fgets calls are allowed.
- Input order MUST strictly match code execution, with no merging or rearrangement.
- For format strings (e.g., scanf("%f, %f")), required delimiters (such as comma) must appear.
- If a snippet is incomplete or ambiguous, choose the most conservative interpretation (empty array).
- NEVER create input for printf lines or code prompts.
- Ignore struct members or fields not directly addressed by input calls.

**Handling Loops and Control Flows:**

- For all forms of loops (for, while, do-while, sentinel/infinite with explicit break values):
  - Repeat input sequences exactly as coded, following required loop iterations.
  - For sentinel or conditionally terminated loops, ensure the terminating keyword/value appears in the input so the run is valid.
  - When input inside a loop is conditional, provide at least one valid input path per run (up to three viable session variants).

**Data Entry, Order, and Conditionals:**

- Consecutive input calls: concatenate their values in the coded order, separated by "\n" if on separate lines.
- No default or implicit data fields. Only what is specifically requested by the code snippet is allowed.

**Output Format Rules:**

- Produce strictly valid JSON only. No explanation, commentary, extra whitespace, or code fences.
- Example:
  {
  "file1.c": ["3\n2\n2"],
  "calc.c": ["1\n2\n+", "5\n9\n-"]
  }

**Examples:**
EXAMPLE 1: Simple for loop
Code:
for (int i = 0; i < 2; ++i) {
scanf("%d %s", &id, name);
}
Correct JSON entry:
{
"loop1.c": ["1 Alice\n2 Bob"]
}
EXAMPLE 2: Nested for loop with data entry
Code:
scanf("%d", &rows);
scanf("%d", &cols);
for (int i = 0; i < rows; i++) {
for (int j = 0; j < cols; j++) {
scanf("%d", &value);
}
}
Correct JSON entry:
{
"mat.c": ["2\n3\n1\n2\n3\n4\n5\n6"]
}
EXAMPLE 3: Loop with conditional inside and data entry
Code:
scanf("%d", &n);
for (int i = 0; i < n; i++) {
scanf("%d", &x);
if (x == 0) scanf("%s", y);
}
Correct JSON entry:
{
"condloop.c": ["3\n0\nhello\n5\n0\nfoo"]
}
EXAMPLE 4: Data entry session with multiple fields
Code:
scanf("%d %f %s", &id, &score, name);
Correct JSON entry:
{
"entry1.c": ["1 98.5 John"]
}
EXAMPLE 5: Complex data entry within for/while loop
Code:
for (int i = 0; i < 2; i++) {
printf("Enter user:");
scanf("%s", username);
printf("Score:");
scanf("%d", &score);
}
Correct JSON entry:
{
"users.c": ["Alice\n100\nBob\n95"]
}
EXAMPLE 6: do-while loop with data entry
Code:
int n;
do {
scanf("%d", &n);
} while (n != 0);
Correct JSON entry:
{
"dowhile.c": ["3\n2\n1\n0"]
}
EXAMPLE 7: More complex conditional loop (loop never runs)
Code:
for (int i = 10; i < 10; i++) {
scanf("%d", &a);
}
Correct JSON entry:
{
"zeroiter.c": []
}
EXAMPLE 8: Sentinel-controlled or keyword exit loop
Code:
while (1) {
scanf("%s", word);
if (strcmp(word, "exit") == 0) break;
}

**Summary:**

- Output precise stdin mappings as JSON for the files, matching only the explicit input-handling code and respecting all structural requirements, especially in tricky loop and sentinel scenarios where input sequence errors are common.
- Do not output anything except the pure JSON answer for each test case.
