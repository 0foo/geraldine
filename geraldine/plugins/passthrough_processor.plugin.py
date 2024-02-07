
description="A zero edit passthrough processor for testing purposes."

def geraldine(processor_data, the_state, the_logger):
    content = processor_data["template_content_string"]
    return content