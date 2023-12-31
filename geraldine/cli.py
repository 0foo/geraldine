#!/usr/bin/env python3
import argparse
from geraldine import processor
from pprint import pprint
from geraldine import util
import time
import sys
import os
import traceback
import logging
from geraldine.GeriStateManager import GeriStateManager


lockfile_path = os.path.join(os.getcwd(), ".geriwatch")
the_state = GeriStateManager()
dest_dir = the_state.data.dest_dir
source_dir = the_state.data.src_dir
logger_name = the_state.data.logger_name
geraldine_directory = the_state.data.geraldine_directory
custom_plugins = the_state.configs.custom_plugin_directories
config_file = the_state.config_file_path

util.create_logger(
        logger_name, 
        log_level=the_state.configs.log_level
    )
the_logger = logging.getLogger(logger_name)


def run():
    parser = argparse.ArgumentParser(prog='geri')
    subparsers = parser.add_subparsers(dest='command', help='commands')
    info_parser = subparsers.add_parser('info', help='Show locations/plugins')
    init_parser = subparsers.add_parser('init', help='Create source directory for geraldine templates.')
    watch_parser = subparsers.add_parser('watch', help='Watch geraldine source folder and rebuild on change.')
    serve_parser = subparsers.add_parser('serve', help='Start simple web development server in current directory.')
    serve_parser.add_argument("port", nargs='?', type=int, default=8000, help="Specify the port on which to run the server. Default is 8000.")
    args = parser.parse_args()

    # Execute based on the command
    if args.command == 'info':
        the_state.print()
        exit()

    # init
    elif args.command == 'init':
        if os.path.exists(geraldine_directory):
            raise Exception(f"Geraldine directory already exists: {source_dir}")

        # create source dir
        util.create_dir(source_dir)
        
        # create geraldine dir
        util.create_dir(geraldine_directory)
        # create custom plugins directories
        for custom_plugin in custom_plugins:
            util.create_dir(custom_plugin)

        # config file
        util.touch(config_file)
        the_state.write_configs()

        exit()

    # serve
    elif args.command == 'serve':
        the_server = None  # Define the_server in the broader scope
        try:
            port = args.port
            the_server = util.get_simple_server(dest_dir, port)
            the_server.start_server()

            # Keep the main thread alive or perform other tasks here
            while the_server.is_running:
                time.sleep(1)

        except KeyboardInterrupt:
            print("Stopping Server")
            if the_server is not None:
                the_server.stop_server()
            exit()

    # watch  
    elif args.command == 'watch':
        if util.file_exists(lockfile_path):
            print(f"Watcher lockfile exists, exiting: {lockfile_path}")
            exit(1)
            
        if not os.path.exists(source_dir):
            raise Exception(f"Can't find source directory: {source_dir}")
        
        util.write_file(lockfile_path, "running")
        print(f"Watcher lockfile created: {lockfile_path}")
        try:
            processor.run(the_state, the_logger)
        except Exception as e:
            util.delete_file(lockfile_path)
            raise(e)


        print(f"Watching directory: {source_dir} \nPress Ctrl+C to stop: ")
        try:
            time_counter = 0
            while True:
                directory_changed = util.has_directory_changed(source_dir, 2)
                if directory_changed:
                    processor.run(the_state, the_logger)
                    print("\n")

        except KeyboardInterrupt:
            print("\nStopping Watcher")
  
        util.delete_file(lockfile_path)
        print(f"Watcher lockfile deleted: {lockfile_path}")
        exit()

    processor.run(the_state, the_logger)


if __name__ == "__main__":
    run()