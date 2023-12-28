#!/usr/bin/env python3
import argparse
import os
from geraldine import primary
from pprint import pprint



def run():
    # Create the parser
    parser = argparse.ArgumentParser(description="Geraldine, a static component generator.")

    # Add arguments
    parser.add_argument("-i", "--info", help="Show install location", action="store_true")
    parser.add_argument("-p", "--plugins", help="List available plugins", action="store_true")
    parser.add_argument("-n", "--init", help="Create source directory for geraldine templates.", action="store_true")

    # Parse arguments
    args = parser.parse_args()

    # Execute based on arguments
    if args.info:
        for key,value in primary.get_info().items():
            print(f"{key}: {value}")
        exit()
    if args.plugins:
        print("Available plugins:")
        for item in primary.list_plugins():
            print(item) 
        exit()
    if args.init:
        print(f"Creating source folder: {primary.source_dir}")
        primary.create_geri_src()
        exit()
        
    primary.run()
    print("Build Completed Successfully")


if __name__ == "__main__":
    run()