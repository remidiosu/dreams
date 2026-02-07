from dataclasses import dataclass

from app.llm.tools.base_tool import BaseTool


@dataclass
class GetThemesOverviewTool(BaseTool):
    name: str = "get_themes_overview"
    description: str = "Get an overview of all themes in the dream journal with counts. Use when user asks about recurring themes."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {}
        }


@dataclass
class GetThemeDreamsTool(BaseTool):
    name: str = "get_theme_dreams"
    description: str = "Get dreams containing a specific theme. Use when user wants to see specific dreams with a particular theme."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "theme": {
                    "type": "string",
                    "description": "The theme to search for"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of dreams to return (default 5)"
                }
            },
            "required": ["theme"]
        }


@dataclass
class GetThemeAnalysisTool(BaseTool):
    name: str = "get_theme_analysis"
    description: str = "Analyze a specific theme - find related symbols, characters, and emotions. Use for deep dive into a theme."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "theme": {
                    "type": "string",
                    "description": "The theme to analyze (e.g., 'transformation', 'pursuit', 'flying')"
                }
            },
            "required": ["theme"]
        }
