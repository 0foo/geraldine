import jinja2
import json
import os
from geraldine import util
from jinja2 import Environment, ChoiceLoader, FileSystemLoader, DictLoader
import logging

the_logger = logging.getLogger("geri_logger")

environment = jinja2.Environment()

remove_extensions=['jinja']

def get_custom_filter_files(frontmatter, project_root_path, template_path):
    out=[]
    if "custom_filter_files" in frontmatter:
        custom_filter_files = frontmatter["custom_filter_files"]
        if isinstance(custom_filter_files, str):
            custom_filter_files = [custom_filter_files]
        for custom_filter_file in custom_filter_files:
            try:
                the_file = util.find_file(custom_filter_file, project_root_path, project_root_path)
                out.append(the_file)
            except Exception as e:
                raise FileNotFoundError(f"Cant find custom_filter_file {e} defined in front matter of: {template_path}.")
    return out
        
def load_custom_filters_from_files(env, file_paths):
    for file_path in file_paths:
        namespace = {}
        with open(file_path, 'r') as file:
            exec(file.read(), namespace)
        # Add the functions defined in the file to the Jinja environment
        for name, func in namespace.items():
            if callable(func):
                env.filters[name] = func


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
    custom_filter_files = get_custom_filter_files(frontmatter, project_root_path, source_template_dir)

    

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

    if custom_filter_files:
        load_custom_filters_from_files(env, custom_filter_files)

    template = env.get_template('the_template') 
    json_data["geraldine_full_data"] = json_data
    out =  template.render(json_data)
    return out