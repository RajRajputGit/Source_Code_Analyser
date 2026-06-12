import os

def main():
    # Define the directory to ensure it exists
    src_dir = "src"
    
    # Define files to create along with their basic boilerplate content
    files = {
        "src/__init__.py": "",
        "src/helper.py": "# Helper functions and utility utilities for the application\n",
        "src/prompt.py": "# Prompts and prompt templates for the application\n",
        ".env": "# Environment Variables\n",
        "app.py": "# Main entry point for the lightweight Python application\n",
        "notebook/test.ipynb": ""
    }

    # 1. Safely check and create the src directory
    if not os.path.exists(src_dir):
        os.makedirs(src_dir)
        print(f"Created directory: {src_dir}")
    else:
        print(f"Directory already exists: {src_dir}")

    # 2. Safely check and create each file
    for filepath, content in files.items():
        # Avoid overwriting existing files
        if os.path.exists(filepath):
            print(f"File already exists: {filepath}")
        else:
            # Ensure the directory for the file exists (e.g. if we add more nested files later)
            dir_name = os.path.dirname(filepath)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print(f"Created directory: {dir_name}")
                
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created file: {filepath}")

if __name__ == "__main__":
    main()
