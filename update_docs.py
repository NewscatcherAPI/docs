# update_docs.py
# Add new article files according to the JSON schema
# Use entire mint.json or any JSON with the "navigation" field

# Further improvements: implement Markdown parsing to update
# "navigation" in mint.json and use titles and article descriptions

import os
import json

# Define the path to the JSON file containing the navigation schema
MINT_FILE_PATH = "v3/documentation/v3-nav.json"


# Function to load the schema from the JSON file
def load_schema(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


# Function to create directories and files based on the navigation schema
def create_structure(navigation):
    for group in navigation:
        if "pages" in group:
            process_pages(group["pages"])
        if "group" in group and "pages":
            print(f"Processing group: {group['group']}")


def process_pages(pages):
    for page in pages:
        if isinstance(page, dict):
            # Recursively process nested groups
            if "group" in page and "pages" in page:
                print(f"Processing nested group: {page['group']}")
                process_pages(page["pages"])
        else:
            # Construct the directory path and the file name relative to the current directory
            full_path = os.path.join(page)
            dir_path = os.path.dirname(full_path)
            file_name = os.path.basename(full_path) + ".mdx"

            # Extract title and description from the file name (customize as needed)
            title = file_name.replace(".mdx", "").replace("-", " ").title()
            description = f"Description for {title}"

            # Create the directories if they don't exist
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created directory: {dir_path}")

            # Create the file with title and description if it doesn't exist
            file_path = os.path.join(dir_path, file_name)
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    f.write(f"---\ntitle: {title}\ndescription: {description}\n---\n")
                print(f"Created file: {file_path}")
            else:
                print(f"File already exists, not modifying: {file_path}")


# Main execution
if __name__ == "__main__":
    # Load the schema from the JSON file
    schema = load_schema(MINT_FILE_PATH)

    # Run the function to create the structure
    create_structure(schema["navigation"])
