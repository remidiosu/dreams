from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.logger import logger
from app.schemas.tool_data import ToolResult
from app.repositories.agent_repository import AgentRepository
from app.services.graphrag_service import GraphRAGService, get_graphrag_service


class AgentTools:
    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id
        self.repo = AgentRepository(db)
        self._graphrag: Optional[GraphRAGService] = None

    @property
    def graphrag(self) -> GraphRAGService:
        if self._graphrag is None:
            self._graphrag = get_graphrag_service(self.user_id)

        return self._graphrag

    async def search_symbols(
            self,
            query: str,
            category: Optional[str] = None,
    ) -> ToolResult:
        try:
            results = await self.repo.search_symbols(
                user_id=self.user_id,
                query=query,
                category=category,
            )

            return ToolResult(
                success=True,
                data={"symbols": results, "count": len(results)},
                tool_name="search_symbols",
            )
        except Exception as e:
            logger.error(f"search_symbols error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="search_symbols",
            )

    async def get_symbol_details(self, symbol_name: str) -> ToolResult:
        try:
            result = await self.repo.get_symbol_details(
                user_id=self.user_id,
                symbol_name=symbol_name,
            )

            if result is None:
                return ToolResult(
                    success=False,
                    error=f"Symbol '{symbol_name}' not found in dream journal",
                    tool_name="get_symbol_details",
                )

            return ToolResult(
                success=True,
                data=result,
                tool_name="get_symbol_details",
            )
        except Exception as e:
            logger.error(f"get_symbol_details error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_symbol_details",
            )

    async def get_symbol_dreams(
            self,
            symbol_name: str,
            limit: int = 5,
    ) -> ToolResult:
        try:
            results = await self.repo.get_symbol_dreams(
                user_id=self.user_id,
                symbol_name=symbol_name,
                limit=limit,
            )

            return ToolResult(
                success=True,
                data={"dreams": results, "count": len(results)},
                tool_name="get_symbol_dreams",
            )
        except Exception as e:
            logger.error(f"get_symbol_dreams error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_symbol_dreams",
            )

    async def get_symbol_patterns(self, symbol_name: str) -> ToolResult:
        try:
            result = await self.repo.get_symbol_patterns(
                user_id=self.user_id,
                symbol_name=symbol_name,
            )

            if "error" in result:
                return ToolResult(
                    success=False,
                    error=result["error"],
                    tool_name="get_symbol_patterns",
                )

            return ToolResult(
                success=True,
                data=result,
                tool_name="get_symbol_patterns",
            )
        except Exception as e:
            logger.error(f"get_symbol_patterns error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_symbol_patterns",
            )

    async def search_characters(
            self,
            query: str,
            character_type: Optional[str] = None,
    ) -> ToolResult:
        try:
            results = await self.repo.search_characters(
                user_id=self.user_id,
                query=query,
                character_type=character_type,
            )

            return ToolResult(
                success=True,
                data={"characters": results, "count": len(results)},
                tool_name="search_characters",
            )
        except Exception as e:
            logger.error(f"search_characters error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="search_characters",
            )

    async def get_character_details(self, character_name: str) -> ToolResult:
        try:
            result = await self.repo.get_character_details(
                user_id=self.user_id,
                character_name=character_name,
            )

            if result is None:
                return ToolResult(
                    success=False,
                    error=f"Character '{character_name}' not found in dream journal",
                    tool_name="get_character_details",
                )

            return ToolResult(
                success=True,
                data=result,
                tool_name="get_character_details",
            )
        except Exception as e:
            logger.error(f"get_character_details error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_character_details",
            )

    async def get_archetype_analysis(self, archetype: str) -> ToolResult:
        try:
            result = await self.repo.get_archetype_analysis(
                user_id=self.user_id,
                archetype=archetype,
            )

            return ToolResult(
                success=True,
                data=result,
                tool_name="get_archetype_analysis",
            )
        except Exception as e:
            logger.error(f"get_archetype_analysis error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_archetype_analysis",
            )

    async def get_emotion_overview(self) -> ToolResult:
        try:
            result = await self.repo.get_emotion_overview(user_id=self.user_id)

            return ToolResult(
                success=True,
                data=result,
                tool_name="get_emotion_overview",
            )
        except Exception as e:
            logger.error(f"get_emotion_overview error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_emotion_overview",
            )

    async def get_emotion_dreams(
            self,
            emotion: str,
            limit: int = 5,
    ) -> ToolResult:
        try:
            results = await self.repo.get_emotion_dreams(
                user_id=self.user_id,
                emotion=emotion,
                limit=limit,
            )

            return ToolResult(
                success=True,
                data={"dreams": results, "count": len(results)},
                tool_name="get_emotion_dreams",
            )
        except Exception as e:
            logger.error(f"get_emotion_dreams error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_emotion_dreams",
            )

    async def get_emotion_correlations(self, emotion: str) -> ToolResult:
        try:
            result = await self.repo.get_emotion_correlations(
                user_id=self.user_id,
                emotion=emotion,
            )

            return ToolResult(
                success=True,
                data=result,
                tool_name="get_emotion_correlations",
            )
        except Exception as e:
            logger.error(f"get_emotion_correlations error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_emotion_correlations",
            )

    async def get_themes_overview(self) -> ToolResult:
        try:
            result = await self.repo.get_themes_overview(user_id=self.user_id)

            return ToolResult(
                success=True,
                data=result,
                tool_name="get_themes_overview",
            )
        except Exception as e:
            logger.error(f"get_themes_overview error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_themes_overview",
            )

    async def get_theme_dreams(
            self,
            theme: str,
            limit: int = 5,
    ) -> ToolResult:
        try:
            results = await self.repo.get_theme_dreams(
                user_id=self.user_id,
                theme=theme,
                limit=limit,
            )

            return ToolResult(
                success=True,
                data={"dreams": results, "count": len(results)},
                tool_name="get_theme_dreams",
            )
        except Exception as e:
            logger.error(f"get_theme_dreams error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_theme_dreams",
            )

    async def get_theme_analysis(self, theme: str) -> ToolResult:
        try:
            result = await self.repo.get_theme_analysis(
                user_id=self.user_id,
                theme=theme,
            )

            return ToolResult(
                success=True,
                data=result,
                tool_name="get_theme_analysis",
            )
        except Exception as e:
            logger.error(f"get_theme_analysis error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_theme_analysis",
            )

    async def search_dreams(
            self,
            query: str,
            limit: int = 5,
    ) -> ToolResult:
        try:
            results = await self.repo.search_dreams(
                user_id=self.user_id,
                query=query,
                limit=limit,
            )

            return ToolResult(
                success=True,
                data={"dreams": results, "count": len(results)},
                tool_name="search_dreams",
            )
        except Exception as e:
            logger.error(f"search_dreams error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="search_dreams",
            )

    async def get_recent_dreams(self, limit: int = 5) -> ToolResult:
        try:
            results = await self.repo.get_recent_dreams(
                user_id=self.user_id,
                limit=limit,
            )

            return ToolResult(
                success=True,
                data={"dreams": results, "count": len(results)},
                tool_name="get_recent_dreams",
            )
        except Exception as e:
            logger.error(f"get_recent_dreams error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_recent_dreams",
            )

    async def get_dream_details(self, dream_id: int) -> ToolResult:
        try:
            result = await self.repo.get_dream_details(
                user_id=self.user_id,
                dream_id=dream_id,
            )

            if result is None:
                return ToolResult(
                    success=False,
                    error=f"Dream {dream_id} not found",
                    tool_name="get_dream_details",
                )

            return ToolResult(
                success=True,
                data=result,
                tool_name="get_dream_details",
            )
        except Exception as e:
            logger.error(f"get_dream_details error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_dream_details",
            )

    async def get_recurring_dreams(self) -> ToolResult:
        try:
            results = await self.repo.get_recurring_dreams(user_id=self.user_id)

            return ToolResult(
                success=True,
                data={"dreams": results, "count": len(results)},
                tool_name="get_recurring_dreams",
            )
        except Exception as e:
            logger.error(f"get_recurring_dreams error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_recurring_dreams",
            )

    async def semantic_search(self, question: str) -> ToolResult:
        try:
            if not self.graphrag.graph_exists:
                return ToolResult(
                    success=False,
                    error="No dreams have been indexed yet. Cannot perform semantic search.",
                    tool_name="semantic_search",
                )

            result = await self.graphrag.query(
                question=question,
                with_references=True,
            )

            return ToolResult(
                success=True,
                data={
                    "response": result.response,
                    "sources": result.sources,
                    "query_type": result.query_type,
                },
                tool_name="semantic_search",
            )
        except Exception as e:
            logger.error(f"semantic_search error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="semantic_search",
            )

    async def get_journal_summary(self) -> ToolResult:
        try:
            result = await self.repo.get_journal_summary(user_id=self.user_id)

            return ToolResult(
                success=True,
                data=result,
                tool_name="get_journal_summary",
            )
        except Exception as e:
            logger.error(f"get_journal_summary error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name="get_journal_summary",
            )
