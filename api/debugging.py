import json
from pydantic import BaseModel
from typing import Any
import pprint


def pretty(c: BaseModel | Any) -> str:
    if isinstance(c, BaseModel):
        return json.dumps(json.loads(c.json()), indent=2)
    return pprint.pformat(c)
