import json

def load_configs():
    with open ("config/blocked.json") as f:
        blocked_list = json.load(f)["blocked"]
        
    with open ("config/words.json") as f:
        words_dict = json.load(f)["words"]
        
    return blocked_list, words_dict