from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class BaseTool:
    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None
