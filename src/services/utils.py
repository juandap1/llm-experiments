import re

def clean_json_response(response_text):
    """
    Cleans the model response to extract valid JSON.
    Removes any markdown formatting or extraneous text.
    """
    return re.sub(r"^```json\s*|\s*```$", "", response_text, flags=re.MULTILINE).strip()