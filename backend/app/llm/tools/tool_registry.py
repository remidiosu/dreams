from typing import List, Dict, Any
from app.llm.tools.symbol_tools import SearchSymbolsTool, GetSymbolDreamsTool, GetSymbolDetailsTool, GetSymbolPatternsTool
from app.llm.tools.character_tools import SearchCharactersTool, GetCharacterDetailsTool, GetArchetypeAnalysisTool
from app.llm.tools.emotion_tools import GetEmotionDreamsTool, GetEmotionOverviewTool, GetEmotionCorrelationsTool
from app.llm.tools.theme_tools import GetThemesOverviewTool, GetThemeDreamsTool, GetThemeAnalysisTool
from app.llm.tools.dream_tools import SearchDreamsTool, GetRecentDreamsTool, GetDreamDetailsTool, GetRecurringDreamsTool
from app.llm.tools.general_tools import SemanticSearchTool, GetJournalSummaryTool


def get_tool_definitions() -> List[Dict[str, Any]]:
    tool_instances = [
        SearchSymbolsTool(),
        GetSymbolDetailsTool(),
        GetSymbolDreamsTool(),
        GetSymbolPatternsTool(),
        SearchCharactersTool(),
        GetCharacterDetailsTool(),
        GetArchetypeAnalysisTool(),
        GetEmotionOverviewTool(),
        GetEmotionDreamsTool(),
        GetEmotionCorrelationsTool(),
        GetThemesOverviewTool(),
        GetThemeDreamsTool(),
        GetThemeAnalysisTool(),
        SearchDreamsTool(),
        GetRecentDreamsTool(),
        GetDreamDetailsTool(),
        GetRecurringDreamsTool(),
        SemanticSearchTool(),
        GetJournalSummaryTool(),
    ]

    return [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters
        }
        for tool in tool_instances
    ]


TOOL_DEFINITIONS = get_tool_definitions()
