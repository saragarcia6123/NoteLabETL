import os
import toml

def get_project_metadata():
    try:
        with open('pyproject.toml', 'r') as f:
            pyproject_data = toml.load(f)

        project = pyproject_data.get('project', {})
        project_name = project.get('name', 'Unknown Project')
        project_version = project.get('version', '0.1.0')
        project_description = project.get('description', 'No description available')

        return project_name, project_version, project_description
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")
        return 'Unknown Project', '0.1.0', 'No description available'

project_name, project_version, project_description = get_project_metadata()

def generate_tree_structure(startpath):
    tree = ""
    for root, dirs, files in os.walk(startpath):
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

## Description
{project_description}

## The following is the directory structure of the project:
{directory_structure}

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

    Set up a Conda environment (recommended):
    ```bash
    conda create -n notelabenv python=3.12
    conda activate notelabenv
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the app, use the following command:
    ```bash
    python -m src.init
    ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""

# Save the README content to a file
with open("README.md", "w") as f:
    f.write(readme_content)

print("README.md generated successfully!")
