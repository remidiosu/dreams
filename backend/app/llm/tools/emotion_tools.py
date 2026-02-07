from dataclasses import dataclass
from app.llm.tools.base_tool import BaseTool


@dataclass
class GetEmotionOverviewTool(BaseTool):
    name: str = "get_emotion_overview"
    description: str = "Get an overview of all emotions in the user's dream journal - most common emotions and their average intensities. Use when user asks about their emotional patterns in dreams."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {}
        }


@dataclass
class GetEmotionDreamsTool(BaseTool):
    name: str = "get_emotion_dreams"
    description: str = "Get dreams where a specific emotion was experienced. Use when user wants to explore dreams with a particular feeling."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "emotion": {
                    "type": "string",
                    "description": "The emotion to search for (e.g., 'fear', 'joy', 'anxiety')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of dreams to return (default 5)"
                }
            },
            "required": ["emotion"]
        }


@dataclass
class GetEmotionCorrelationsTool(BaseTool):
    name: str = "get_emotion_correlations"
    description: str = "Find what symbols, characters, and themes correlate with a specific emotion. Use for understanding emotional triggers in dreams."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "emotion": {
                    "type": "string",
                    "description": "The emotion to analyze"
                }
            },
            "required": ["emotion"]
        }
