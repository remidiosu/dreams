from dataclasses import dataclass
from app.llm.tools.base_tool import BaseTool


@dataclass
class SearchCharactersTool(BaseTool):
    name: str = "search_characters"
    description: str = "Search dream characters by name. Use when user asks about a person or figure from their dreams."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Character name or search term"
                },
                "character_type": {
                    "type": "string",
                    "enum": ["known_person", "unknown_person", "self", "animal", "mythical", "abstract"],
                    "description": "Optional type filter"
                }
            },
            "required": ["query"]
        }


@dataclass
class GetCharacterDetailsTool(BaseTool):
    name: str = "get_character_details"
    description: str = "Get detailed information about a dream character including archetypes assigned, personal significance, and all appearances. Use for understanding a recurring character."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "character_name": {
                    "type": "string",
                    "description": "Name of the character"
                }
            },
            "required": ["character_name"]
        }


@dataclass
class GetArchetypeAnalysisTool(BaseTool):
    name: str = "get_archetype_analysis"
    description: str = "Get all characters and dreams associated with a Jungian archetype (shadow, anima, animus, wise_old_man, trickster, hero, mother, father, child, self). Use for archetypal pattern analysis."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "archetype": {
                    "type": "string",
                    "description": "The archetype to analyze (e.g., 'shadow', 'anima', 'trickster')"
                }
            },
            "required": ["archetype"]
        }
