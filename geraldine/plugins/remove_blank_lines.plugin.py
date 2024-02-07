description="Very simply removes blank lines from within the data passed into it."

def geraldine(processor_data, the_state, the_logger):
    content = processor_data["template_content_string"]
    return "\n".join([line for line in content.split('\n') if line.strip()])
