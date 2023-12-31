import os
import traceback
import logging
from geraldine import util


def run(the_state, the_logger):  
    source_dir = the_state.data.src_dir
    destination_dir = the_state.data.dest_dir
    priority_directories =  the_state.data.priority_directories

    if not os.path.exists(source_dir):
        raise Exception(f"Can't find source directory: {source_dir}")

    util.create_dir(destination_dir)
    util.clear_directory(destination_dir)

    for priority_directory in priority_directories:
        if os.path.exists(priority_directory):
            process(priority_directory,the_state,the_logger)
            the_logger.debug(f"Priority directory built: {priority_directory}")
        else:
            the_logger.debug(f"Can't find priority directory: {priority_directory}")

    process(source_dir,the_state,the_logger)
    the_logger.debug(f"Source directory processed successfully: {source_dir}")

def process(in_dir, the_state, the_logger):
    max_depth = the_state.configs.max_directory_depth
    source_dir = the_state.data.src_dir
    destination_dir = the_state.data.dest_dir
    source_dir_name = the_state.configs.geri_src_dir_name
    destination_dir_name = the_state.configs.geri_dest_dir_name
    modules = the_state.data.modules
    root_dir=the_state.data.root_directory

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
        
        # is_sym, NOTE: is this needed?
        if location.is_symlink():
            continue

        # is file
        if location.is_file():
            if util.is_image(location.path):
                util.copy_path(location.path, new_path)
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
            
            current_processing = ""
            for processor in processor_list:
                if processor in modules:
                    the_processor=modules[processor]

                    processor_data = {
                        "frontmatter":frontmatter,
                        "template_content_string" : content,
                        "src_path" : location.path,
                        "destination_path": new_path,
                        "project_root_path": root_dir,
                        "template_filename": name,
                        "source_dir_name": source_dir_name,
                        "destination_dir_name": destination_dir_name,
                        "project_root_src_dir": os.path.join(root_dir,source_dir_name),
                        "modules": modules,
                        "configs": the_state.configs.data,
                        "app_data": the_state.data.data
                    }


                    # Note 1: handle processor exceptions here, on a per file basis,
                    #       so that it only fails on a single file
                    #       and continues to iterate the directory and build everything else
                    # Note 2: Trimming down output from File Not Found exceptions, as those are relatively
                    #       easy to troubleshoot 
                    try:
                        if name != current_processing:
                            the_logger.debug(f"processing {name}" )
                            current_processing = name

                        content = the_processor.geraldine(processor_data)
                    except FileNotFoundError as e:
                        the_logger.critical(e)
                        continue
                    except Exception as e:
                        traceback.print_exc()
                        continue

                    # begin post processing
                    if hasattr(the_processor, 'remove_extensions'):
                        for remove_extension in the_processor.remove_extensions:
                            if remove_extension[0] != ".":
                                remove_extension = "." + remove_extension
                            new_path = util.remove_extension_from_path(new_path, remove_extension)
                    # post processing end
                    if not content:
                        break
                else:
                    print(processor + " module not found in: " + location.path)

            if content:
                util.write_file_with_dir(new_path, content)
            continue

        print(f"Couldn't identify node type for: {location.path}")