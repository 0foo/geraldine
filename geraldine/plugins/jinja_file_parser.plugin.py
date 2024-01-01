import jinja2
import json
import os
from pprint import pprint
from geraldine import util

environment = jinja2.Environment()

remove_extensions=['jinja']


def module_apply(processor_data):
    frontmatter = processor_data["frontmatter"]
    processor_list = frontmatter["processor"]
    modules = processor_data["modules"]

    if not isinstance(processor_list, list):
        processor_list = [processor_list]
        processor_list.remove("jinja_file_parser")
    
    for processor in processor_list:
        if processor in modules:
            the_processor=modules[processor]
            content = the_processor.geraldine(processor_data)
            processor_data["template_content_string"] = content
    return processor_data


def geraldine(in_data):
    frontmatter = in_data["frontmatter"]
    json_path = frontmatter["json_path"]
    source_path = in_data["src_path"]
    template_dir = os.path.dirname(in_data["src_path"])
    try:
        json_file_path = util.find_file(template_dir, json_path) # the json file
    except Exception as e:
        print(f"Cant find json data in front matter of: {source_path}")
        raise(e)

    filename_key = frontmatter["filename_key"]
    content = in_data["template_content_string"]
    destination_file = in_data["destination_path"]
    destination_dir = os.path.dirname(destination_file)
    destination_extension = frontmatter["extension"]

    if destination_extension[0] != ".":
        destination_extension = f".{destination_extension}"
    


    # start data
    with open(json_file_path, "r") as f:
        json_data = json.load(f)
    if "start_key" in frontmatter:
        start_key_list = frontmatter["start_key"].split(".")
    else:
         start_key_list = []
    dict_to_use = util.dict_lookup_function(json_data, start_key_list)
    print(f"There are {len(dict_to_use)} in dataset being converted to files." )


    # iterate
    jinja_template = environment.from_string(content) # the jinja template
    for dict_item in dict_to_use:
            # print(dict_item)
            if "{{" in filename_key and "}}" in filename_key:
                 filename = util.destination_file_name_parser(filename_key, dict_item)
            else:
                filename = util.dict_lookup_function(dict_item, filename_key.split("."))
            merged_template = jinja_template.render(dict_item)
            in_data["template_content_string"] = merged_template
            final_content = module_apply(in_data)
            filename = filename + destination_extension
            destination_location = os.path.join(destination_dir, filename)
            with open(destination_location, "w") as file:
                 file.write(final_content)