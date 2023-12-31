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
    json_data = {}

    if "start_key" in frontmatter:
        start_key_list = frontmatter["start_key"].split(".")
    else:
         start_key_list = []

    if "json_path" in frontmatter:
        json_path = frontmatter["json_path"]
        json_file_path = util.find_file(source_template_dir, json_path)
        with open(json_file_path, "r") as f:
            json_data = json.load(f)
        json_data = util.dict_lookup_function(json_data, start_key_list)

    env = Environment(loader=ChoiceLoader([
        DictLoader({'the_template': content}),
        FileSystemLoader(compiled_template_dir)
    ]))

    template = env.get_template('the_template')
    return  template.render(json_data)