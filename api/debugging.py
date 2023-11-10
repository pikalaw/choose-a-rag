import json
from pydantic import BaseModel


def pretty(c: BaseModel) -> str:
    return json.dumps(json.loads(c.json()), indent=2)
