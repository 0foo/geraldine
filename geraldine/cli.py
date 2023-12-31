#!/usr/bin/env python3
import argparse
from geraldine import primary
from pprint import pprint
from geraldine import util
import time
import sys
import os
import traceback

source_dir = primary.source_dir
dest_dir = primary.destination_dir_name
lockfile_path = "/tmp/.geriwatch"

def run_primary():
    try:
        primary.run()
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        raise(e)
    finally:
        util.delete_file(lockfile_path)

def run():
    # Create the top-level parser
    parser = argparse.ArgumentParser(prog='geri')
    subparsers = parser.add_subparsers(dest='command', help='commands')

    # Create a subparser for the 'info' command
    info_parser = subparsers.add_parser('info', help='Show install location')

    # Create a subparser for the 'init' command
    init_parser = subparsers.add_parser('init', help='Create source directory for geraldine templates.')

      # Create a subparser for the 'init' command
    watch_parser = subparsers.add_parser('watch', help='Watch geraldine source folder and rebuild on change.')


    # Create a subparser for the 'serve' command
    serve_parser = subparsers.add_parser('serve', help='Start simple web development server in current directory.')
    serve_parser.add_argument("port", nargs='?', type=int, default=8000, help="Specify the port on which to run the server. Default is 8000.")

    # Parse the arguments
    args = parser.parse_args()

    # Execute based on the command
    if args.command == 'info':
        print("Setup info")
        for key,value in primary.get_info().items():
            print(f"\t{key}: {value}")
        print("Available plugins:")
        for item in primary.list_plugins():
            print(f"\t{item}") 
        exit()


    # init
    elif args.command == 'init':
        print(f"Creating source folder: {primary.source_dir}")
        primary.create_geri_src()
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

        run_primary()


        print(f"Watching directory, Press Ctrl+C to stop: {source_dir}")
        try:
            while True:
                directory_changed = util.has_directory_changed(source_dir, 2)
                if directory_changed:
                    run_primary()
        except KeyboardInterrupt:
            print("\nStopping Watcher")
  
        util.delete_file(lockfile_path)
        exit()

    run_primary()


if __name__ == "__main__":
    run()