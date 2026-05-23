from urlib.parse import urlparse
from proxy.config import load_configs

def is_blocked (url: str) -> bool:
    domain = urlparse(url).netloc
    
    blocked_list, _ = load_configs()
    
    return domain in blocked_list