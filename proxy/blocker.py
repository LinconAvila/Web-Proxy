from urllib.parse import urlparse
from proxy.config import load_configs

def is_blocked(url: str) -> bool:
    netloc = urlparse(url).netloc
    domain = netloc.split(":")[0] 
    blocked_list, _ = load_configs()
    return domain in blocked_list