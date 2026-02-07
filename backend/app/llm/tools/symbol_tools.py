from dataclasses import dataclass
from app.llm.tools.base_tool import BaseTool


@dataclass
class SearchSymbolsTool(BaseTool):
    name: str = "search_symbols"
    description: str = "Search the user's dream symbols by name or category. Use when user asks about a specific symbol or type of symbols (e.g., 'water symbols', 'animal symbols')."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Symbol name or search term (e.g., 'water', 'snake', 'house')"
                },
                "category": {
                    "type": "string",
                    "enum": ["object", "place", "action", "animal", "nature", "body", "other"],
                    "description": "Optional category filter"
                }
            },
            "required": ["query"]
        }


@dataclass
class GetSymbolDetailsTool(BaseTool):
    name: str = "get_symbol_details"
    description: str = "Get detailed information about a specific symbol including personal meanings the user has assigned, occurrence count, and related dreams. Use when user wants to understand what a symbol means to them specifically."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "symbol_name": {
                    "type": "string",
                    "description": "Name of the symbol to look up"
                }
            },
            "required": ["symbol_name"]
        }


@dataclass
class GetSymbolDreamsTool(BaseTool):
    name: str = "get_symbol_dreams"
    description: str = "Get dreams containing a specific symbol. Use when user wants to see specific dreams where a symbol appeared."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "symbol_name": {
                    "type": "string",
                    "description": "Name of the symbol"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of dreams to return (default 5)"
                }
            },
            "required": ["symbol_name"]
        }


@dataclass
class GetSymbolPatternsTool(BaseTool):
    name: str = "get_symbol_patterns"
    description: str = "Find patterns for a symbol: what other symbols it appears with, what emotions accompany it, and common themes. Use for deeper analysis of symbol meaning."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "symbol_name": {
                    "type": "string",
                    "description": "Name of the symbol to analyze"
                }
            },
            "required": ["symbol_name"]
        }
