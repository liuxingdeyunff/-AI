"""Source excerpt follow-up through the currently selected provider."""
from model_studio import model, dialogue


def ask(data):
    excerpt=data["excerpt"]
    if not isinstance(excerpt,str) or not 0<len(excerpt)<=1000: raise ValueError("授权片段最多 1000 字")
    return dialogue({**data,"context":excerpt})
