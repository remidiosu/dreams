from dataclasses import dataclass
from typing import Optional


@dataclass
class ToolResult:
    success: bool
    data: Optional[dict | list] = None
    error: Optional[str] = None
    tool_name: str = ""

    def to_dict(self) -> dict:
        if self.success:
            return {
                "status": "success",
                "tool": self.tool_name,
                "data": self.data,
            }
        else:
            return {
                "status": "error",
                "tool": self.tool_name,
                "error": self.error,
            }
