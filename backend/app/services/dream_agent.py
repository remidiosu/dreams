from typing import AsyncGenerator
from google import genai
from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.logger import logger
from app.services.agent_tools import AgentTools
from app.services.gemini_client import generate_content_with_retry
from app.llm.tools.tool_registry import TOOL_DEFINITIONS
from app.schemas.agent_data import SYSTEM_PROMPT, ChatMessage, AgentResponse
from app.schemas.tool_data import ToolResult


class DreamAgent:
    def __init__(self, user_id: int, db: AsyncSession):
        self.user_id = user_id
        self.db = db
        self.model = settings.agent_model
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.tools = AgentTools(db, user_id)
        self.conversation_history: list[ChatMessage] = []

    def _build_tools_config(self) -> list[types.Tool]:
        function_declarations = [
            types.FunctionDeclaration(
                name=tool_def["name"],
                description=tool_def["description"],
                parameters=tool_def.get("parameters"),
            )
            for tool_def in TOOL_DEFINITIONS
        ]

        return [types.Tool(function_declarations=function_declarations)]

    def _build_contents(self, user_message: str, images: list[dict] | None = None) -> list[types.Content]:
        contents = [
            types.Content(
                role="user" if msg.role == "user" else "model",
                parts=[types.Part(text=msg.content)],
            )
            for msg in self.conversation_history
        ]

        parts: list[types.Part] = [types.Part(text=user_message)]

        if images:
            import base64
            for img in images:
                image_bytes = base64.b64decode(img["base64"])
                parts.append(types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=img["mime_type"],
                ))

        contents.append(types.Content(role="user", parts=parts))

        return contents

    def _build_config(self, tools_config: list[types.Tool], thinking_level: str = "high") -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=tools_config,
            temperature=1.0,
            thinking_config=types.ThinkingConfig(
                thinking_level=thinking_level,
            ),
        )

    async def _execute_tool(self, tool_name: str, args: dict) -> ToolResult:
        tool_map = {
            "search_symbols": self.tools.search_symbols,
            "get_symbol_details": self.tools.get_symbol_details,
            "get_symbol_dreams": self.tools.get_symbol_dreams,
            "get_symbol_patterns": self.tools.get_symbol_patterns,
            "search_characters": self.tools.search_characters,
            "get_character_details": self.tools.get_character_details,
            "get_archetype_analysis": self.tools.get_archetype_analysis,
            "get_emotion_overview": self.tools.get_emotion_overview,
            "get_emotion_dreams": self.tools.get_emotion_dreams,
            "get_emotion_correlations": self.tools.get_emotion_correlations,
            "get_themes_overview": self.tools.get_themes_overview,
            "get_theme_dreams": self.tools.get_theme_dreams,
            "get_theme_analysis": self.tools.get_theme_analysis,
            "search_dreams": self.tools.search_dreams,
            "get_recent_dreams": self.tools.get_recent_dreams,
            "get_dream_details": self.tools.get_dream_details,
            "get_recurring_dreams": self.tools.get_recurring_dreams,
            "semantic_search": self.tools.semantic_search,
            "get_journal_summary": self.tools.get_journal_summary,
        }

        if tool_name not in tool_map:
            return ToolResult(
                success=False,
                error=f"Unknown tool: {tool_name}",
                tool_name=tool_name,
            )

        try:
            return await tool_map[tool_name](**args)
        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                tool_name=tool_name,
            )

    async def chat(self, user_message: str, images: list[dict] | None = None) -> AgentResponse:
        logger.info(f"Agent chat: user_id={self.user_id}, message_length={len(user_message)}, images={len(images) if images else 0}")
        tools_config = self._build_tools_config()
        contents = self._build_contents(user_message, images=images)
        tool_calls_made = []
        sources = []

        try:
            config = self._build_config(tools_config, thinking_level="high")
            response = generate_content_with_retry(
                self.client, self.model, contents, config,
            )

            max_tool_rounds = 5
            for round_num in range(max_tool_rounds):
                function_calls = []

                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            function_calls.append(part.function_call)

                if not function_calls:
                    break

                contents.append(response.candidates[0].content)

                function_responses = []
                for fc in function_calls:
                    tool_name = fc.name
                    args = dict(fc.args) if fc.args else {}
                    logger.info(f"Executing tool: {tool_name} with args: {args}")

                    result = await self._execute_tool(tool_name, args)
                    tool_calls_made.append({
                        "tool": tool_name,
                        "args": args,
                        "success": result.success,
                    })

                    if result.success and result.data:
                        if "sources" in result.data:
                            sources.extend(result.data["sources"])

                    function_responses.append(types.Part(
                        function_response=types.FunctionResponse(
                            name=tool_name,
                            response=result.to_dict(),
                        )
                    ))

                contents.append(types.Content(role="user", parts=function_responses))

                config = self._build_config(tools_config, thinking_level="high")
                response = generate_content_with_retry(
                    self.client, self.model, contents, config,
                )

            final_response = ""
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        final_response += part.text

            history_content = f"[Image attached] {user_message}" if images else user_message
            self.conversation_history.append(ChatMessage(role="user", content=history_content))
            self.conversation_history.append(ChatMessage(role="assistant", content=final_response))
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            logger.info(f"Agent response: tools_used={len(tool_calls_made)}, response_length={len(final_response)}")

            return AgentResponse(
                message=final_response,
                tool_calls=tool_calls_made,
                sources=sources,
            )

        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return AgentResponse(
                message="I apologize, but I encountered an issue processing your request. Could you please try rephrasing your question?",
                tool_calls=tool_calls_made,
                sources=[],
            )

    async def chat_stream(self, user_message: str) -> AsyncGenerator[str, None]:
        response = await self.chat(user_message)
        words = response.message.split()
        chunk_size = 3

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            if i > 0:
                chunk = " " + chunk
            yield chunk

    def clear_history(self):
        self.conversation_history = []


def get_dream_agent(user_id: int, db: AsyncSession) -> DreamAgent:
    return DreamAgent(user_id, db)
