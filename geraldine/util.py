import os
import json
import shutil
import importlib.util
import re
import yaml
import subprocess
from time import sleep
import time
from watchdog.events import FileSystemEventHandler





def destination_file_name_parser(filename_string, json_file):
    pattern = r"{{(.*?)}}"
    
    def dynamic_replace(match):
        key = match.group(1).split(".")
        result = dict_lookup_function(json_file, key)
        return result
    
    return re.sub(pattern, dynamic_replace, filename_string)


# escaping functionality, in progress
# def convert_to_ascii_escapes(match):
#     char_after_slash = match.group()[1]
#     ascii_code = ord(char_after_slash)
#     return "{" + str(ascii_code) + "}"
# def convert_from_ascii_escapes(match):
#     number = int(match.group(1))
#     return chr(number)
# def escape_to_ascii_tags(s, pattern):
#     return re.sub(pattern, lambda match: convert_to_ascii_escapes(match), s)
# def ascii_tags_to_character(s):
#     pattern = r"\{(\d+)\}"
#     return re.sub(pattern, convert_from_ascii_escapes, s)

# # 0.0.class + test.1.name\+ + thing.0.amabob
# def destination_file_name_parser(filename_string, json_file, separator="_"):
#     filename_string = escape_to_ascii_tags(filename_string, "\\.")
#     filename_list = filename_string.split("+")
#     outname = []
#     for item in filename_list:
#         item_list = item.split(".")
#         item_list = [ascii_tags_to_character(x) for x in item_list]
#         result = dict_lookup_function(item_list, json_file)
#         outname.append(result)
#     return separator.join(outname)


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

def consists_of_three_or_more_dashes(input_string):
    pattern = r'^[-]{3,}$'  # Pattern to match strings with only 3 or more dashes
    return bool(re.match(pattern, input_string))

def get_front_matter(file_path):
    with open(file_path, 'r') as file:
        file_data = file.readlines()
    lines_encountered = 0
    metadata = ""
    content=""

    for the_line in file_data:

        if consists_of_three_or_more_dashes(the_line.strip()):
            lines_encountered += 1
            continue

        if  lines_encountered == 0 and the_line.strip():
            content = "\n".join(file_data)
            break

        if lines_encountered == 1:
            metadata += the_line
      
        if lines_encountered == 2:
            content += the_line

    massage_metadata=metadata.replace('\t', ' ' * 4) # yaml hates tabs
    massage_metadata=yaml.safe_load(massage_metadata)

    return DictToObject({
        "metadata":massage_metadata,
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


def depth_first_dir_walk(path, max_depth=20, current_depth=0):
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

def delete_dir(dirname, error=False):
    try:
        shutil.rmtree(dirname)
    except OSError as e:
        if error:
            print("Error: %s - %s." % (e.filename, e.strerror))

def clear_directory(directory):
    # Check if the directory exists
    if not os.path.exists(directory):
        print("Directory does not exist:", directory)
        return

    # Remove each item in the directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        
        if os.path.isfile(item_path) or os.path.islink(item_path):
            # It's a file or symlink - delete it
            os.unlink(item_path)
        elif os.path.isdir(item_path):
            # It's a directory - delete it and all its contents
            shutil.rmtree(item_path)
            
def replace_path_base(original_path, source_dir, destination_dir):
    # Remove the source directory from the original path
    relative_path = os.path.relpath(original_path, source_dir)

    # Join the relative path with the destination directory
    new_path = os.path.join(destination_dir, relative_path)

    return new_path

# finds a file, if file is relative will use relative to the base_path, otherwise if absolute will return absolute file
def find_file(base_path, file_path):
    # Check if the file_path is relative
    if not os.path.isabs(file_path):
        file_path = os.path.join(base_path, file_path)
    else:
        return file_path

    # Check if the file exists
    if os.path.exists(file_path):
        return file_path
    else:
        raise Exception("File path: " + file_path + " doesn't exist. ")

def is_int(key):
    try:
        int(key)
        return True
    except:
        return False

# looks up in a dictionary based on a list, ie ["0", "class", "1] will return dict[0]["class"][1]
def dict_lookup_function(input_dict, lookup_list):
    current_dict = input_dict
    for key in lookup_list:
        if is_int(key):
            key = int(key)
            current_dict = current_dict[key]
            continue
        if key in current_dict:
            current_dict = current_dict[key]
        else:
            print(f"{key} not in dictionary")
            return None  # Key not found in the dictionary
    return current_dict


def start_simple_server(port=8000, directory=None):
    import http.server
    import socketserver


    if directory:
        os.chdir(directory)
    

    directory = os.getcwd()

    # Create an HTTP request handler
    handler = http.server.SimpleHTTPRequestHandler

    # Create the HTTP server
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\nServing from directory root: {directory}")
        print(f"Starting HTTP server at http://localhost:{port}")
        # Start serving requests
        httpd.serve_forever()


def get_watcher_handler(source_dir):
    class MyHandler(FileSystemEventHandler):
            def __init__(self):
                self.last_handled_time = 0
                self.delay = 1
            def should_handle_event(self):
                current_time = time.time()
                if current_time - self.last_handled_time > self.delay:
                    self.last_handled_time = current_time
                    return True
                return False
            def run(self):
                command = "geri"
                directory = os.path.dirname(source_dir)
                result = subprocess.run(command, shell=True, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    print(f"{result.stdout}")
                else:
                    print(f"Error in executing geri command:\n{result.stderr}")
            def on_any_event(self, event):
                if not self.should_handle_event():  
                    return
                if event.event_type == "opened":
                    return
                if event.event_type == "closed":
                    return
                print(event)
                self.run()
    return MyHandler

def watcher(directory_to_watch, file_system_event_handler):
    import time
    from watchdog.observers import Observer
    
    class DirectoryWatcher:
        def __init__(self, directory_to_watch):
            self.observer = Observer()
            self.directory_to_watch = directory_to_watch

        def run(self):
            event_handler = file_system_event_handler()
            self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
            self.observer.start()
            print(f"\nStarted watching directory: {directory_to_watch}. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping directory watcher...")
                self.observer.stop()

            self.observer.join()

    watcher = DirectoryWatcher(directory_to_watch)
    watcher.run()