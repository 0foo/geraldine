import jinja2
import json
import os
from pprint import pprint
from geraldine import util
import copy
from jinja2 import Environment, ChoiceLoader, FileSystemLoader, DictLoader
import logging

environment = jinja2.Environment()

remove_extensions=['jinja']

the_logger = logging.getLogger("geri_logger")

def module_apply(processor_data):
    frontmatter = processor_data["frontmatter"]
    processor_list = frontmatter["processor"]
    modules = processor_data["modules"]
    original_template_content_string = processor_data["template_content_string"]
    processor_data["template_content_string"] = processor_data["merged_template"]
    project_root_path = processor_data["project_root_path"]
    project_root_src_dir = processor_data["project_root_src_dir"]

    if not isinstance(processor_list, list):
        processor_list = [processor_list]
    if "jinja_file_parser" in processor_list:
        processor_list.remove("jinja_file_parser")

    for processor in processor_list:
        if processor in modules:
            the_processor=modules[processor]
            content = the_processor.geraldine(processor_data)
            processor_data["template_content_string"] = content
    processor_data["template_content_string"] = original_template_content_string
    return content


def process_file_name_key(filename):
    pass


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

def geraldine(in_data):
    frontmatter = in_data["frontmatter"]
    json_project_path = frontmatter["json_project_path"]
    source_path = in_data["src_path"]
    template_dir = os.path.dirname(in_data["src_path"])
    project_root_path = in_data["project_root_path"]
    destination_dir_name = in_data["destination_dir_name"]
    destination_root_path = os.path.join(project_root_path, destination_dir_name)
    project_root_src_dir = in_data["project_root_src_dir"]
    custom_filter_files = get_custom_filter_files(frontmatter, project_root_path, source_path)

    try:
        json_file_path = util.find_file(json_project_path, template_dir, project_root_src_dir) # the json file
    except Exception as e:
        raise FileNotFoundError(f"Cant find json data {e} defined in front matter of: {source_path}")

    filename_key = frontmatter["filename_key"]
    content = in_data["template_content_string"]
    destination_file = in_data["destination_path"]
    destination_dir = os.path.dirname(destination_file)
    destination_extension = frontmatter["extension"]

    if destination_extension[0] != ".":
        destination_extension = f".{destination_extension}"

    # process start data
    with open(json_file_path, "r") as f:
        json_data = json.load(f)
    if "start_key" in frontmatter:
        start_key_list = frontmatter["start_key"].split(".")
    else:
         start_key_list = []
    dict_to_use = util.dict_lookup_function(json_data, start_key_list)
    the_logger.debug(f"There are {len(dict_to_use)} components being build from the {os.path.basename(source_path)} template reading the {os.path.basename(json_project_path)} dataset." )


    # iterate
    # file template
    # jinja_template = environment.from_string(content) # the jinja template
    env = Environment(loader=ChoiceLoader([
        DictLoader({'the_template': content}),
        FileSystemLoader(destination_root_path)
    ]))

    if custom_filter_files:
        load_custom_filters_from_files(env, custom_filter_files)
    
    jinja_template = env.get_template('the_template')

    
    for dict_item in dict_to_use:

            # process filename template
            jinja_filename_template = environment.from_string(filename_key)
            filename = jinja_filename_template.render(dict_item)

            # process content template
            if "add_full_data_variable" in frontmatter and frontmatter["add_full_data_variable"]:
                dict_item["geraldine_full_data"] = copy.deepcopy(dict_item)


            merged_template = jinja_template.render(dict_item)
            in_data["merged_template"] = merged_template

            # apply additional processors defined in front matter
            final_content = module_apply(in_data)

            # write to filesystem
            filename = filename + destination_extension
            destination_location = os.path.join(destination_dir, filename)
            with open(destination_location, "w") as file:
                 file.write(final_content)