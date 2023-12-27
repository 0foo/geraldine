import jinja2
import json
import os
from pprint import pprint
import util
environment = jinja2.Environment()

remove_extensions=['jinja']


def geraldine(in_data):
    frontmatter = in_data["frontmatter"]
    json_path = frontmatter["json_path"]
    template_dir = os.path.dirname(in_data["src_path"])
    json_file_path = util.find_file(template_dir, json_path) # the json file
    if "start_key" in frontmatter:
        start_key_list = frontmatter["start_key"].split(".")
    else:
         start_key_list = []
    filename_key = frontmatter["filename_key"].split(".")
    content = in_data["template_content"]
    destination_file = in_data["destination_path"]
    destination_dir = os.path.dirname(destination_file)
    destination_extension = frontmatter["extension"]
    if destination_extension[0] != ".":
        destination_extension = f".{destination_extension}"
    
    with open(json_file_path, "r") as f:
        json_data = json.load(f)

    dict_to_use = util.dict_lookup_function(json_data, start_key_list)
    
    jinja_template = environment.from_string(content) # the jinja template

    for dict_item in dict_to_use:
            filename = util.dict_lookup_function(dict_item, filename_key)
            merged_template = jinja_template.render(dict_item)
            filename = filename + destination_extension
            destination_location = os.path.join(destination_dir, filename)
            with open(destination_location, "w") as file:
                 file.write(merged_template)