# Generate me a JSON

You are given multiple program source files written in a single programming language (for example, C).  
Your task is to produce the exact stdin input that each program consumes, based strictly on its input-handling calls.  
You will only receive the lines that read from stdin (e.g., scanf, gets, fgets, input(), readLine()).  
From these, you must infer 1–3 complete stdin sessions for each file.

---

## INPUT RULES

1. Never assume or invent extra input.
2. Include only characters consumed by actual input functions.
3. Preserve exact execution order of input calls.
4. Represent the Enter key with `\n`.
5. Do not include prompts, printf text, or any program output.
6. For format strings with required separators (e.g., "%d,%d"), reproduce them exactly.
7. For loops:
   - Repeat inputs exactly as many times as the loop executes.
   - If loop bounds depend on user input, use that value consistently.
   - For sentinel/terminating loops, include at least one session that reaches termination.
8. For conditional input calls:
   - Include that input only if prior inputs satisfy the condition.
9. Use the most conservative interpretation when ambiguity exists.

---

## OUTPUT FORMAT

Output must be a single JSON object.

Keys: exact filenames including extension, e.g., `"1.c"`.  
Values: arrays of 1–3 complete stdin sessions (strings).

Rules:

- If a file has **no** input calls, use `[]`.
- If only one execution path exists, return **exactly one** session.
- If the program contains meaningful branching or sentinel loops, return up to **three** distinct sessions.
- If the program asks a number which will be used further (for ex in loops) make sure its neither too big nor too small. It should be appropriate for the example
- Each session is a single string containing the full stdin input in order, using `\n` for Enter.
- No commentary, no explanation, no markdown outside the JSON block when responding.

Think hard while checking the rules

## Example structure (not literal):

This is a complete example demonstrating loops with variable bounds, sentinel termination, branching, NxN matrices (with size > 1), and multiple stdin sessions where meaningful.

```json
{
  "1.c": ["hello world\n"],

  "2.c": ["5\n10\n20\n30\n40\n50\n", "3\n7\n7\n7\n"],

  "3.c": ["3\n1\n2\n3\n4\n5\n6\n7\n8\n9\n"],

  "4.c": ["4\n12\n4\n16\n8\n", "4\n1\n3\n5\n7\n"],

  "5.c": ["apple\nbanana\nx\n", "test\nx\n"],

  "6.c": ["2\n9\n8\n7\n6\n5\n4\n3\n2\n"],

  "7.c": ["6\n10\n20\n30\n40\n50\n60\n", "2\n100\n200\n"],

  "8.c": ["6\n1\n2\n2\n3\n3\n3\n", "4\n9\n9\n9\n9\n"],

  "9.c": ["5\n10\n20\n30\n40\n50\n", "5\n1\n2\n3\n4\n5\n", "1\n9\n"]
}
```

The above's example in c. The actual could be of any language and you must adjust accordingly

Return only the JSON object inside a single code block, with no commentary, no markdown, and no text outside the JSON.
