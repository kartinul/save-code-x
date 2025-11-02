import pyperclip


async def get_clipboard_code_name(client):
    code = pyperclip.paste().strip()
    if not code:
        return None  # no code in clipboard

    prompt = f"""
    You are an assistant that names code files.
    The following code was copied from clipboard:

    ---
    {code}
    ---

    Suggest a concise and natural file name (no spaces, just lowercase, underscores or hyphens).
    DO NOT INCLUDE ANY FILE EXTENTION. Just the pure name
    Respond with only the filename, nothing else.
    """

    response = await client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=16,
    )

    name = response.output_text.strip().replace("`", "").replace('"', "")
    return name
