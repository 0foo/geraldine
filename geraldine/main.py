import os
import json
import pathlib
import shutil
import importlib.util



destination_location="dist"
cwd = os.getcwd()
source_dir = cwd + "/geri_src"
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

class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)
    def all(self):
        properties = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        for prop in properties:
            print(f"{prop}: {getattr(self, prop)}")

def strip_quotes(s):
    return s.strip('\'"')

def load_json_or_str(input_string):
    try:
        # Try parsing the string as JSON
        json_object = json.loads(input_string)
        return json_object  # It's valid JSON
    except json.JSONDecodeError:
        return strip_quotes(input_string.strip())


def get_front_matter(file_path):
    with open(file_path, 'r') as file:
        file_data = file.readlines()
    lines_encountered = 0
    metadata = {}
    content=""

    for the_line in file_data:

        if the_line.strip() == '---':
            lines_encountered += 1
            continue

        if  lines_encountered == 0 and the_line.strip():
            content = "\n".join(file_data)
            break

        if lines_encountered == 1:
            the_line = the_line.strip()
            key_value = the_line.split(':', 1)
            if len(key_value) == 2:
                the_key = key_value[0].strip()
                the_value = load_json_or_str(key_value[1])
                metadata[the_key]=the_value
            else:
                raise Exception("Malformed metadata or improper closing of metadata: " + the_line)
      
        if lines_encountered == 2:
            content += the_line

    return DictToObject({
        "metadata":metadata,
        "content":content
    })


def import_module_from_path(path):
    module_name = os.path.basename(path).split('.')[0]
    module_spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module

def delete_dir(dirname, error=False):
    try:
        shutil.rmtree(dirname)
    except OSError as e:
        if error:
            print("Error: %s - %s." % (e.filename, e.strerror))


def create_dir(dir, gitkeep=False):
    if not os.path.exists(dir):
        os.makedirs(dir)
    if gitkeep:
        file = open(dir + "/.gitkeep", 'w')
        file.write('')
        file.close()


def depth_first_dir_walk(path, max_depth=10, current_depth=0):
    """ walk the directory tree in a depth first fashion with a max_depth limit """
    if current_depth > max_depth:
        return
    for entry in os.scandir(path):
        try:
            yield entry
            if entry.is_dir(follow_symlinks=False):
                yield from depth_first_dir_walk(entry.path, max_depth, current_depth + 1)
        except Exception as e:
            print(e)

def load_modules():
    for module in depth_first_dir_walk(plugin_path, max_depth=0):
        if module.name.endswith('.plugin.py'):
            the_module = import_module_from_path(module.path)
            modules[module.name[:-10]] = the_module
            


def delete_dir(dirname, error=False):
    try:
        shutil.rmtree(dirname)
    except OSError as e:
        if error:
            print("Error: %s - %s." % (e.filename, e.strerror))


def replace_path_base(original_path, source_dir, destination_dir):
    # Remove the source directory from the original path
    relative_path = os.path.relpath(original_path, source_dir)

    # Join the relative path with the destination directory
    new_path = os.path.join(destination_dir, relative_path)

    return new_path

def remove_extension_from_path(file_path, extension_to_remove):
    extension_queue = []
    root, extension = os.path.splitext(file_path)
    while extension:    
        if extension != extension_to_remove:
            extension_queue.append(extension)
        root, extension = os.path.splitext(root)
    while extension_queue:
        root += extension_queue.pop()
    return root

def run():  
    if not os.path.exists(source_dir):
        print(f"Can't find source directory: {source_dir}")
        exit()

    load_modules()
    delete_dir(destination_dir)
    create_dir(destination_dir)
    for location in depth_first_dir_walk(source_dir):
        name = location.name
        extension = pathlib.Path(location.path).suffix
        full_path = location.path
        new_path = replace_path_base(full_path, source_dir, destination_dir)

        if name == destination_location:
            continue

        # is_dir
        if location.is_dir():
            create_dir(new_path)
            continue
        
        # is_sym
        if location.is_symlink():
            continue

        # is file
        if location.is_file():
            post = get_front_matter(full_path)

            if not post.metadata:
                shutil.copy(full_path, new_path)
                continue

            metadata=post.metadata
            content=post.content

            for processor, data in post.metadata.items():
                if processor in modules:
                    the_processor=modules[processor]
                    content = the_processor.geraldine(data, full_path, content)

                    # begin post processing
                    if hasattr(the_processor, 'remove_extensions'):
                        for remove_extension in the_processor.remove_extensions:
                            if remove_extension[0] != ".":
                                remove_extension = "." + remove_extension
                            new_path = remove_extension_from_path(new_path, remove_extension)
                    # post processing end
                else:
                    print(processor + " module not found in: " + full_path)

            if content:
                with open(new_path, "w") as new_f:
                    new_f.write(content)
            continue

        print(f"Couldn't identify node type for: {location.path}")