import re



def convert_tags_to_links(text):
    # Define a regular expression pattern to find all tags
    pattern = r'\{@item ([^}]+)\}'
    
    # Function to process each match
    def replace_with_link(match):
        # Split the content of the tag on '|'
        parts = match.group(1).split('|')
        # Extract the first part and replace spaces with dashes, add '.html' at the end
        item_name = parts[0].strip().replace(' ', '-').lower() + '.html'
        # Construct the URL
        url = f'/components/items/{item_name}'
        # Construct the HTML link
        link_text = parts[0] if len(parts) > 0 else "Item"
        return f'<a href="{url}">{link_text}</a>'

    # Use the sub method to replace each match with the result of replace_with_link
    return re.sub(pattern, replace_with_link, text)

def geraldine(in_data):
    content = in_data["template_content_string"]
    return convert_tags_to_links(content)