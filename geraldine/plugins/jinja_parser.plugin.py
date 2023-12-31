import jinja2
import json
import os
from geraldine import util
from jinja2 import Environment, ChoiceLoader, FileSystemLoader, DictLoader

environment = jinja2.Environment()

remove_extensions=['jinja']


def geraldine(processor_data):
    frontmatter = processor_data["frontmatter"]
    template_path = processor_data["src_path"]
    content = processor_data["template_content_string"]
    destination_path = processor_data["destination_path"]
    source_template_dir = os.path.dirname(template_path)
    compiled_template_dir = os.path.dirname(destination_path)
    project_root_path = processor_data["project_root_path"]
    destination_dir_name = processor_data["destination_dir_name"]
    destination_root_path = os.path.join(project_root_path, destination_dir_name)
    json_data = {}

    if "start_key" in frontmatter:
        start_key_list = frontmatter["start_key"].split(".")
    else:
        start_key_list = []

    if "json_path" in frontmatter:
        json_path = frontmatter["json_path"]

        try:
            json_file_path = util.find_file(source_template_dir, json_path)
        except Exception as e:
            print(f"Cant find json data in front matter of: {template_path}")
            exit()
        
        with open(json_file_path, "r") as f:
            json_data = json.load(f)

        json_data = util.dict_lookup_function(json_data, start_key_list)
    
    
        if isinstance(json_data, list):
            json_data = {"data": json_data}
            print(f"Your json_path frontmatter data in {template_path} was pointing to a list, and jinja requires a dict to render. So wrapped it in an dict under the key: \"data\"")
    
    env = Environment(loader=ChoiceLoader([
        DictLoader({'the_template': content}),
        FileSystemLoader(destination_root_path)
    ]))
    template = env.get_template('the_template')
    out =  template.render(json_data)
    return out