import jinja2
import json
import os

environment = jinja2.Environment()

remove_extensions=['jinja']

def find_file(base_path, file_path):
    # Check if the file_path is relative
    if not os.path.isabs(file_path):
        file_path = os.path.join(base_path, file_path)
    else:
        return file_path

    # Check if the file exists
    if os.path.exists(file_path):
        return file_path
    else:
        raise Exception("File path: " + file_path + " doesn't exist. ")

def geraldine(json_path, template_path, content):
    template_dir = os.path.dirname(template_path)
    json_file_path = find_file(template_dir, json_path)
    template = environment.from_string(content)
    with open(json_file_path, "r") as f:
        json_data = json.load(f)
    return  template.render(json_data)