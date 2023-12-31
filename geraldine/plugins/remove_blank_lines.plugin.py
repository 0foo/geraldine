







def geraldine(processor_data):
    content = processor_data["template_content_string"]
    return "\n".join([line for line in content.split('\n') if line.strip()])
