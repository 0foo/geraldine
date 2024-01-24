import os
'''
Example: config file setup:
post_processors:
  -   name: file_appender
      dirs_to_append: 
      - path: /geri_dist/js/util
        extension: js
        delete_originals: true
        destination_path: /geri_dist/js/util/util.js
      - path: /geri_dist/js/components
        extenstion: js
        delete_originals: true
        destination_path: /geri_dist/js/components/components.js
'''

def join_two_absolute_paths(path1, path2):
    from pathlib import Path
    path1 = Path(path1)
    path2 = Path(path2)
    file_path = path1 / path2.relative_to(path2.anchor)
    return str(file_path)


def file_appender(config_file_data, the_state, the_logger):
    dirs_to_append = config_file_data['dirs_to_append']
    
    for item in dirs_to_append:

        delete_originals = False
        if "delete_originals" in item:
            delete_originals = item["delete_originals"]

        directory = join_two_absolute_paths(the_state.data.root_directory , item["path"])
        if os.path.isdir(directory):
            dir_name = os.path.basename(directory)
            if "destination_path" in item:
                append_file_path = join_two_absolute_paths(the_state.data.root_directory, item["destination_path"])
            else:
                append_file_path = os.path.join(directory, dir_name + f".{item['extension']}")

            if os.path.exists(append_file_path):
                os.remove(append_file_path)
            with open(append_file_path, 'w') as append_file:
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if file_path == append_file_path:
                        continue
                    print_file_path = file_path.replace(the_state.data.root_directory, "")
                    print_append_file_path = append_file_path.replace(the_state.data.root_directory, "")
                    the_logger.debug(f"Running file appender on {print_file_path}. Appending to {print_append_file_path}. Delete originals: {delete_originals}." )
                    # Skip the append file itself
                    if file_path == append_file_path:
                        continue

                    # Append the contents of each file to the append file
                    if os.path.isfile(file_path):
                        with open(file_path, 'r') as file:
                            append_file.write(file.read())
                            append_file.write("\n")  # Adding a newline for separation

                        # Optionally delete the original file
                        # print("delete originals: " + str(delete_originals))
                        if delete_originals:
                            # print(f"deleting: {file_path}")
                            os.remove(file_path)

def geraldine_post_process(config_file_data, the_state,the_logger):
    file_appender(config_file_data, the_state, the_logger)