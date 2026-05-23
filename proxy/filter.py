import re
from proxy.config import load_configs

def filter_content(html: str) -> tuple[str, bool]:
    _, words_dict = load_configs()

    modified_html = html
    was_filtered  = False

    for word, replacement in words_dict.items():
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        if pattern.search(modified_html):
            modified_html = pattern.sub(replacement, modified_html)
            was_filtered  = True

    return modified_html, was_filtered