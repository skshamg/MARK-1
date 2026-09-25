import os


def write_file(filename: str, content: str) -> str:
    """
    Creates or overwrites a file with the specified text content.
    Useful for generating code, scripts, logs, or notes.
    """
    try:
        # Prevent writing outside the workspace for safety
        clean_path = os.path.abspath(filename)
        with open(clean_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File '{filename}' successfully written ({len(content)} characters)."
    except Exception as e:
        return f"Failed to write file '{filename}': {str(e)}"


def read_file(filename: str) -> str:
    """
    Reads and returns the contents of a specified file.
    Capped at the first 100 lines to avoid memory overflow.
    """
    try:
        clean_path = os.path.abspath(filename)
        if not os.path.exists(clean_path):
            return f"Error: File '{filename}' does not exist."

        with open(clean_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        truncated = lines[:100]
        preview = "".join(truncated)

        if len(lines) > 100:
            preview += f"\n... [Truncated: {len(lines) - 100} additional lines omitted]"

        return f"Contents of {filename}:\n{preview}"
    except Exception as e:
        return f"Failed to read file '{filename}': {str(e)}"


def append_to_file(filename: str, content: str) -> str:
    """
    Appends text or logs to the end of an existing file.
    """
    try:
        clean_path = os.path.abspath(filename)
        with open(clean_path, "a", encoding="utf-8") as f:
            f.write("\n" + content)
        return f"Appended content to '{filename}' successfully."
    except Exception as e:
        return f"Failed to append to '{filename}': {str(e)}"


def search_files(extension: str = ".py", directory: str = ".") -> str:
    """
    Recursively finds all files ending with a given extension (e.g., '.py', '.txt', '.json').
    """
    try:
        matched_files = []
        target_dir = os.path.abspath(directory)

        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(extension):
                    relative_path = os.path.relpath(os.path.join(root, file), target_dir)
                    matched_files.append(relative_path)

        if not matched_files:
            return f"No files ending with '{extension}' found in {target_dir}."

        return f"Found {len(matched_files)} files matching '{extension}':\n" + "\n".join(
            [f"- {f}" for f in matched_files[:30]]
        )
    except Exception as e:
        return f"Search error: {str(e)}"