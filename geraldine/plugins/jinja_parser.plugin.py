import jinja2
import json
import os
import util

environment = jinja2.Environment()

remove_extensions=['jinja']


def geraldine(processor_data):
    frontmatter = processor_data["frontmatter"]
    json_path = frontmatter["json_path"]
    template_path = processor_data["src_path"]
    content = processor_data["template_content"]
    template_dir = os.path.dirname(template_path)
    json_file_path = util.find_file(template_dir, json_path)
    template = environment.from_string(content)
    with open(json_file_path, "r") as f:
        json_data = json.load(f)
    return  template.render(json_data)