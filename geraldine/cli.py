#!/usr/bin/env python3
import argparse
from geraldine import primary
from pprint import pprint
from geraldine import util
import time
import sys

source_dir = primary.source_dir
dest_dir = primary.destination_dir_name

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
    elif args.command == 'init':
        print(f"Creating source folder: {primary.source_dir}")
        primary.create_geri_src()
        exit()
    # elif args.command == 'serve':
    #     try:
    #         port = args.port
    #         the_server = util.get_simple_server(source_dir, port)
    #         the_server.start_server()
    #     except KeyboardInterrupt:
    #         print("Stopping Server")
    #         the_server.stop_server()
    #     exit()
    elif args.command == 'serve':
        the_server = None  # Define the_server in the broader scope
        try:
            port = args.port
            the_server = util.get_simple_server(source_dir, port)
            the_server.start_server()

            # Keep the main thread alive or perform other tasks here
            while the_server.is_running:
                time.sleep(1)

        except KeyboardInterrupt:
            print("Stopping Server")
            if the_server is not None:
                the_server.stop_server()
        
    elif args.command == 'watch':
        try:
            primary.run()
        except Exception as e:
            print(e)
            print("Exiting")
            sys.exit(1)

        print(f"Watching directory, Press Ctrl+C to stop: {source_dir}")
        try:
            while True:
                directory_changed = util.has_directory_changed(source_dir, 2)
                if directory_changed:
                    try:
                        primary.run()
                    except Exception as e:
                        print(e)
        except KeyboardInterrupt:
            print("Stopping Watcher")

        exit()

    try:
        primary.run()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    run()