import dataclasses
import json
from datetime import datetime, date
from enum import Enum
from typing import Any


def json_serializer(obj: Any) -> str:
    """JSON serializer for objects not serializable by default json code"""

    # https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    # if isinstance(obj, list):
    #     return f"[{[str(o) for o in obj]}]"
    if hasattr(obj, "__dict__"):
        return json.dumps(obj.__dict__, default=json_serializer)
    return str(obj)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)  # type: ignore[arg-type]
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, (datetime, date)):
            return o.isoformat().replace("+00:00", ".000Z")
        if hasattr(o, "to_dict"):
            return o.to_dict()
        return super().default(o)
