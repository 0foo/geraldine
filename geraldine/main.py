import sys
import os
import pathlib
import shutil


# ensure this directory on class path
# directory_path = os.path.abspath(__file__)
# parent_directory = os.path.dirname(os.path.dirname(directory_path))
# sys.path.append(parent_directory)
# sys.path.append(directory_path)
import util

# editable configs
destination_location="dist"
source_dir = "/geri_src"
max_depth=10

cwd = os.getcwd()
source_dir = cwd + source_dir
destination_dir = os.path.join(cwd, destination_location)

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
plugin_path = os.path.join(script_dir, 'plugins')
modules={}

def get_info():
    return {
        "install location" : script_dir,
        "plugin path" : plugin_path 
    }

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
    util.delete_dir(destination_dir)
    util.create_dir(destination_dir)
    for location in util.depth_first_dir_walk(source_dir, max_depth=max_depth):
        name = location.name
        extension = pathlib.Path(location.path).suffix
        full_path = location.path
        new_path = util.replace_path_base(full_path, source_dir, destination_dir)

        if name == destination_location:
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
            post = util.get_front_matter(full_path)

            if not post.metadata:
                shutil.copy(full_path, new_path)
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
                        "template_content" : content,
                        "src_path" : full_path,
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
                    print(processor + " module not found in: " + full_path)

            if content:
                with open(new_path, "w") as new_f:
                    new_f.write(content)
            continue

        print(f"Couldn't identify node type for: {location.path}")