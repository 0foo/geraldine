#!/usr/bin/env python3
import argparse
from geraldine import primary
from pprint import pprint
from geraldine import util


source_dir = primary.source_dir

def run():
    # Create the top-level parser
    parser = argparse.ArgumentParser(prog='geri')
    subparsers = parser.add_subparsers(dest='command', help='commands')

    # Create a subparser for the 'info' command
    info_parser = subparsers.add_parser('info', help='Show install location')

    # Create a subparser for the 'init' command
    init_parser = subparsers.add_parser('init', help='Create source directory for geraldine templates.')

      # Create a subparser for the 'init' command
    watch_parser = subparsers.add_parser('watch', help='Watch geraldine source folder and rebuild changes.')


    # Create a subparser for the 'serve' command
    serve_parser = subparsers.add_parser('serve', help='Start simple web development server in current directory.')
    serve_parser.add_argument("port", nargs='?', type=int, default=8000, help="Specify the port on which to run the server. Default is 8000.")

    # Parse the arguments
    args = parser.parse_args()

    # Execute based on the command
    if args.command == 'info':
        print("Setup info")
        for key,value in primary.get_info().items():
            print(f"{key}: {value}")
        print("Available plugins:")
        for item in primary.list_plugins():
            print(item) 
        exit()
    elif args.command == 'init':
        print(f"Creating source folder: {primary.source_dir}")
        primary.create_geri_src()
        exit()
    elif args.command == 'serve':
        port = args.port
        util.start_simple_server(port) 
        exit()
    elif args.command == 'watch':
        MyHandler = util.get_watcher_handler(source_dir)
        util.watcher(source_dir, MyHandler)  
        exit()

    primary.run()
    print("Build Completed Successfully")


if __name__ == "__main__":
    run()