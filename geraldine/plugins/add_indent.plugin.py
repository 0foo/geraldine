'''
Adds indents to every line in the entire file, specified by indent_count paramter in front matter.
Useful for indenting includes templates.
'''


import os
from geraldine import util


remove_extensions=['jinja']

def add_indent_to_front(text, spaces_count=4):
    spaces = ' ' * spaces_count
    lines = text.splitlines()
    lines_with_spaces = [spaces + line for line in lines]
    return '\n'.join(lines_with_spaces)


def geraldine(processor_data):
    frontmatter = processor_data["frontmatter"]
    content = processor_data["template_content_string"]
    if not content:
        print(processor_data)
    if "indent_count" in frontmatter:
        indent_count = frontmatter["indent_count"]
    else:
        indent_count=4
    
    return add_indent_to_front(content, indent_count)

    