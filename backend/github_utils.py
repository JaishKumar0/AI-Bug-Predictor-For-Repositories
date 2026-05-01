import os
import tempfile
import subprocess
from pathlib import Path


def extract_python_files(repo_url: str, max_file_size_kb: int = 200) -> dict:
    """
    Clone a public GitHub repo (shallow clone, depth=1 for speed),
    walk every .py file, read its contents, and return a dict of:
        { "relative/path/to/file.py": "file contents as string", ... }

    max_file_size_kb: skip files larger than this (avoids huge auto-generated files
                      that would overflow the CodeBERT tokenizer anyway).
    """
    extracted_data = {}

   
    if not repo_url.startswith(("https://github.com/", "http://github.com/")):
        raise ValueError("Only public GitHub URLs are supported (https://github.com/...).")

    with tempfile.TemporaryDirectory() as temp_dir:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_dir],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
           
            raise ValueError(f"Git clone failed: {result.stderr.strip()}")

        for root, dirs, files in os.walk(temp_dir):
            # Skip hidden folders (.git, .github, __pycache__, venv, etc.)
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in (
                "__pycache__", "venv", "env", ".venv", "node_modules", "dist", "build"
            )]

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = Path(root) / file

                # Skip files that are too large
                size_kb = file_path.stat().st_size / 1024
                if size_kb > max_file_size_kb:
                    continue

                rel_path = os.path.relpath(file_path, temp_dir)

                try:
                    content = file_path.read_text(encoding="utf-8")
                    # Skip empty files
                    if content.strip():
                        extracted_data[rel_path] = content
                except (UnicodeDecodeError, OSError):
                    # Skip files that can't be decoded as UTF-8
                    pass

    return extracted_data
