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
    root_path = processor_data["project_root_path"]
    destination_root_path = os.path.join(root_path, processor_data["destination_dir_name"])
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
            raise e
        
        with open(json_file_path, "r") as f:
            json_data = json.load(f)

        json_data = util.dict_lookup_function(json_data, start_key_list)
    
    print(content)
    print(compiled_template_dir)
    
    env = Environment(loader=ChoiceLoader([
        DictLoader({'the_template': content}),
        FileSystemLoader(destination_root_path)
    ]))
    template = env.get_template('the_template')
    out =  template.render(json_data)
    print(out)
    return out