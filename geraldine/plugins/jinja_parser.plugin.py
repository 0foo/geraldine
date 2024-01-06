import jinja2
import json
import os
from geraldine import util
from jinja2 import Environment, ChoiceLoader, FileSystemLoader, DictLoader
import logging

the_logger = logging.getLogger("geri_logger")

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
    project_root_src_dir = processor_data["project_root_src_dir"]
    json_data = {}

    if "start_key" in frontmatter:
        start_key_list = frontmatter["start_key"].split(".")
    else:
        start_key_list = []

    if "json_project_path" in frontmatter:
        json_project_path = frontmatter["json_project_path"]

        try:
            json_file_path = util.find_file(json_project_path, source_template_dir, project_root_src_dir)
        except Exception as e:
            raise FileNotFoundError(f"Cant find json data {e} defined in front matter of: {template_path}.")
        
        with open(json_file_path, "r") as f:
            json_data = json.load(f)

        json_data = util.dict_lookup_function(json_data, start_key_list)
    
    
        if isinstance(json_data, list):
            json_data = {"data": json_data}
            the_logger.info(f"Your json_project_path frontmatter data in {template_path} was pointing to a list, "
                            "and jinja requires a dict to render. So wrapped it in an dict under the key: \"data\". " 
                            "Use the key \"data\" as the root variable in your jinja template.")
    
    env = Environment(loader=ChoiceLoader([
        DictLoader({'the_template': content}),
        FileSystemLoader(destination_root_path)
    ]))
    template = env.get_template('the_template') 
    out =  template.render(json_data)
    return out