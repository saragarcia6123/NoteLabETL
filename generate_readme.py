import os
import toml
import pathspec

def get_project_metadata():
    try:
        with open('pyproject.toml', 'r') as f:
            pyproject_data = toml.load(f)

        project = pyproject_data.get('tool', {}).get('poetry', {})
        project_name = project.get('name', 'Unknown Project')
        project_version = project.get('version', '0.1.0')
        project_description = project.get('description', 'No description available')
        project_authors = project.get('authors', [])
        project_license = project.get('license', 'No license available')

        return project_name, project_version, project_description, ', '.join(project_authors), project_license
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")
        return 'Unknown Project', '0.1.0', 'No description available', [], 'No license available'

project_name, project_version, project_description, project_authors, project_license = get_project_metadata()

def generate_tree_structure(startpath):
    tree = ""

    # Compile pathspec from .gitignore if it exists
    gitignore_path = os.path.join(startpath, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            ignored_patterns = f.read().splitlines()
        spec = pathspec.PathSpec.from_lines('gitwildmatch', ignored_patterns)
    else:
        spec = pathspec.PathSpec([])

    for root, dirs, files in os.walk(startpath):
        # Filter directories using pathspec
        dirs[:] = [d for d in dirs if not spec.match_file(os.path.relpath(os.path.join(root, d), startpath))]

        # Filter files using pathspec
        files = [f for f in files if not spec.match_file(os.path.relpath(os.path.join(root, f), startpath))]

        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        tree += f"{indent}{os.path.basename(root)}/\n"
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree += f"{subindent}{f}\n"

    return tree

directory_structure = generate_tree_structure('src')

readme_content = f"""
## {project_name} - {project_version}
## Authors: {project_authors}
## License: {project_license}

## Description
{project_description}

## The following is the directory structure of the project:
```
{directory_structure}
```

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/NoteLabETL.git
    cd NoteLabETL
    ```

2. Set up environment (optional, recommended):

    Set up a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\\Scripts\\activate`
    ```

    OR

    Set up a Conda environment:
    ```bash
    conda create -n notelabenv
    conda activate notelabenv
    ```

3. Install dependencies:
    ```bash
    pip install poetry
    poetry install
    ```

## Usage

To run the app, use the following command:
    ```bash
    python -m src.init
    ```
"""

# Save the README content to a file
with open("README.md", "w") as f:
    f.write(readme_content)

print("README.md generated successfully!")
