import os
import re
from pathlib import Path

EXAMPLES_DIR = "examples"
DOCS_DIR = "docs/examples"
MKDOCS_FILE = "mkdocs.yml"


def extract_metadata(file_path):
    """Extract metadata like docstring and the rest of the code from a Python script."""
    with open(file_path, "r") as f:
        content = f.read()

    # Extract the module-level docstring
    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    docstring = docstring_match.group(1).strip() if docstring_match else ""

    # Extract everything after the docstring
    if docstring_match:
        code_start = docstring_match.end()
        remaining_code = content[code_start:].strip()
    else:
        remaining_code = content.strip()

    return docstring, remaining_code


def generate_markdown(file_name, docstring, remaining_code):
    """Generate Markdown content for a given example."""
    markdown = f"# {file_name} Example\n\n"
    if docstring:
        markdown += f"{docstring}\n\n"
    markdown += "```python\n"
    markdown += remaining_code
    markdown += "\n```\n"
    return markdown


def update_docs():
    """Scan examples and update documentation."""
    examples_path = Path(EXAMPLES_DIR)
    docs_path = Path(DOCS_DIR)
    mkdocs_path = Path(MKDOCS_FILE)

    # Ensure the docs directory exists
    docs_path.mkdir(parents=True, exist_ok=True)

    # Scan examples folder
    example_files = examples_path.glob("*.py")
    nav_entries = []

    for example_file in example_files:
        if example_file.name == "__init__.py":  # Skip __init__.py
            continue

        file_name = example_file.stem
        docstring, full_code = extract_metadata(example_file)

        # Generate Markdown content
        markdown_content = generate_markdown(file_name, docstring, full_code)

        # Write to Markdown file
        markdown_file = docs_path / f"{file_name}.md"
        with open(markdown_file, "w") as f:
            f.write(markdown_content)

        # Add to navigation
        nav_entries.append(f"      - {file_name}: 'examples/{file_name}.md'\n")

    # Update mkdocs.yml
    with open(mkdocs_path, "r") as f:
        mkdocs_content = f.readlines()

    # Find the Examples section in mkdocs.yml
    try:
        examples_index = mkdocs_content.index("    - Examples:\n")
    except ValueError:
        print("Examples section not found in mkdocs.yml.")
        return

    # Insert navigation entries
    end_index = examples_index + 1
    while end_index < len(mkdocs_content) and mkdocs_content[end_index].startswith("      -"):
        end_index += 1

    mkdocs_content = (
        mkdocs_content[:examples_index + 1] + nav_entries + mkdocs_content[end_index:]
    )

    # Write back to mkdocs.yml
    with open(mkdocs_path, "w") as f:
        f.writelines(mkdocs_content)


if __name__ == "__main__":
    update_docs()
