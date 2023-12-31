import sys
import os
import pathlib
import shutil
from geraldine import util

# editable configs until config file functionality is implemented
destination_dir_name="geri_dist"
source_dir_name = "geri_src"
max_depth=10
priority_directories=[
    "includes"
]

cwd = os.getcwd()
source_dir =  os.path.join(cwd, source_dir_name)
destination_dir = os.path.join(cwd, destination_dir_name)

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
plugin_path = os.path.join(script_dir, 'plugins')
modules={}

def get_info():
    return {
        "install location" : script_dir,
        "plugin path" : plugin_path 
    }
    destination_dir = os.path.dirname(in_dir)


def list_plugins():
    files = [f for f in os.listdir(plugin_path) 
        if os.path.isfile(os.path.join(plugin_path, f))]
    return files

def create_geri_src():
    util.create_dir(source_dir)

def load_modules():
    for module in util.depth_first_dir_walk(plugin_path, max_depth=0):
        if module.name.endswith('.plugin.py'):
            the_module = util.import_module_from_path(module.path)
            modules[module.name[:-10]] = the_module
            

def run():  
    if not os.path.exists(source_dir):
        print(f"Can't find source directory: {source_dir}")
        exit()

    load_modules()
    try:
        util.create_dir(destination_dir)
        util.clear_directory(destination_dir)
    except:
        pass

    for dir_item in priority_directories:
        the_dir = os.path.join(source_dir, dir_item)
        if os.path.exists(the_dir):
            process(the_dir)
            print(f"Priority directory processed: {the_dir}")

    process(source_dir)


def process(in_dir):
    for location in util.depth_first_dir_walk(in_dir, max_depth=max_depth):
        name = location.name
        old_path = util.remove_subpath(location.path, source_dir)
        new_path = os.path.join(destination_dir, old_path)

        if name == destination_dir_name:
            continue

        # is_dir
        if location.is_dir():
            util.create_dir(new_path)
            continue
        
        # is_sym
        if location.is_symlink():
            continue

        # is file
        if location.is_file():
            if util.is_image(location.path):
                try:
                    util.copy_path(location.path, new_path)
                except:
                    pass
                continue

            post = util.get_front_matter(location.path)

            if not post.metadata:
                util.copy_path(location.path, new_path)
                continue

            frontmatter=post.metadata
            content=post.content
            processor_list = frontmatter["processor"]
            if not isinstance(processor_list, list):
                processor_list = [processor_list]
            

            for processor in processor_list:
                if processor in modules:
                    the_processor=modules[processor]

                    processor_data = {
                        "frontmatter":frontmatter,
                        "template_content_string" : content,
                        "src_path" : location.path,
                        "destination_path": new_path,
                        "template_filename": name
                    }

                    content = the_processor.geraldine(processor_data)

                    # begin post processing
                    if hasattr(the_processor, 'remove_extensions'):
                        for remove_extension in the_processor.remove_extensions:
                            if remove_extension[0] != ".":
                                remove_extension = "." + remove_extension
                            new_path = util.remove_extension_from_path(new_path, remove_extension)
                    # post processing end
                else:
                    print(processor + " module not found in: " + location.path)

            if content:
                with open(new_path, "w") as new_f:
                    new_f.write(content)
            continue

        print(f"Couldn't identify node type for: {location.path}")