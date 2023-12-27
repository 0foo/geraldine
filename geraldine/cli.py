#!/usr/bin/env python3
import argparse
import os
import main
from pprint import pprint

# Create the parser
parser = argparse.ArgumentParser(description="Geraldine, a static component generator.")

# Add arguments
parser.add_argument("-i", "--info", help="Show install location", action="store_true")
parser.add_argument("-p", "--plugins", help="List available plugins", action="store_true")

# Parse arguments
args = parser.parse_args()

# Execute based on arguments
if args.info:
    for key,value in main.get_info().items():
        print(f"{key}: {value}")
    exit()
if args.plugins:
    print("Available plugins:")
    for item in main.list_plugins():
        print(item) 
    exit()
    
main.run()
print("Build Completed Successfully")