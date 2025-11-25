import os
import subprocess
import sys


def save_file(full_path: str, content: str):
    import os

    print(full_path, end="()")
    # make sure the directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # write the file
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)


import subprocess


def commit_file(folder_path: str, commit_text: str):

    if not os.path.exists(os.path.join(folder_path, ".git")):
        subprocess.run(["git", "init"], cwd=folder_path)

    subprocess.run(["git", "add", "."], cwd=folder_path)
    subprocess.run(["git", "commit", "-m", commit_text], cwd=folder_path)


def shortenPath(path: str, parts: int = 3) -> str:
    """Return only the last `parts` of a path, e.g. C:/.../foo/bar"""
    import os

    split_path = os.path.normpath(path).split(os.sep)
    if len(split_path) > parts:
        return f"...{os.sep}" + os.sep.join(split_path[-parts:])
    return path
