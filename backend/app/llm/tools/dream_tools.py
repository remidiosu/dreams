from dataclasses import dataclass
from app.llm.tools.base_tool import BaseTool


@dataclass
class SearchDreamsTool(BaseTool):
    name: str = "search_dreams"
    description: str = "Search dreams by text in narrative, title, or interpretation. Use for finding specific dreams."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search text"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of dreams to return (default 5)"
                }
            },
            "required": ["query"]
        }


@dataclass
class GetRecentDreamsTool(BaseTool):
    name: str = "get_recent_dreams"
    description: str = "Get the user's most recent dreams. Use when user refers to recent dreams or wants context."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of dreams to return (default 5)"
                }
            }
        }


@dataclass
class GetDreamDetailsTool(BaseTool):
    name: str = "get_dream_details"
    description: str = "Get full details of a specific dream including all symbols, characters, emotions, and themes. Use when discussing a particular dream."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "dream_id": {
                    "type": "integer",
                    "description": "ID of the dream"
                }
            },
            "required": ["dream_id"]
        }


@dataclass
class GetRecurringDreamsTool(BaseTool):
    name: str = "get_recurring_dreams"
    description: str = "Get all dreams marked as recurring. Use when user asks about recurring dreams or patterns."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {}
        }
