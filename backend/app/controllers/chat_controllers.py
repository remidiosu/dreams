import asyncio
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.logger import logger
from app.database import get_db
from app.dependencies.auth import get_current_user_id
from app.repositories.chat_repository import ChatRepository
from app.repositories.dream_repository import DreamRepository
from app.services.dream_agent import DreamAgent, get_dream_agent, ChatMessage
from app.data_models.chat_data import (
    ChatCreate,
    ChatUpdate,
    ChatResponse,
    ChatListResponse,
    ChatWithMessagesResponse,
    MessageCreate,
    MessageResponse,
    DreamSource,
)


chat_router = APIRouter(prefix="/chat", tags=["Chat"])

_agent_cache: dict[str, DreamAgent] = {}
_agent_cache_lock = asyncio.Lock()


def _get_agent_cache_key(user_id: int, chat_id: int) -> str:
    return f"{user_id}:{chat_id}"


@chat_router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
        data: ChatCreate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    chat = await chat_repo.create_chat(user_id, data.name)
    message_count = 0

    return ChatResponse(
        id=chat.id,
        name=chat.name,
        message_count=message_count,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
    )


@chat_router.get("", response_model=ChatListResponse)
async def list_chats(
        per_page: int = Query(20, ge=1, le=100),
        cursor: Optional[int] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    chats, has_more = await chat_repo.list_chats(user_id, per_page, cursor)

    chat_responses = []
    for chat in chats:
        message_count = await chat_repo.get_message_count(chat.id)
        chat_responses.append(
            ChatResponse(
                id=chat.id,
                name=chat.name,
                message_count=message_count,
                created_at=chat.created_at,
                updated_at=chat.updated_at,
            )
        )

    return ChatListResponse(
        data=chat_responses,
        has_more=has_more,
        next_cursor=chats[-1].id if has_more and chats else None,
    )


@chat_router.get("/{chat_id}", response_model=ChatWithMessagesResponse)
async def get_chat(
        chat_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    result = await chat_repo.get_chat_with_messages(chat_id, user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    chat, messages = result

    message_responses = []
    for msg in messages:
        sources = []
        for excerpt_data in msg.source_excerpts or []:
            sources.append(DreamSource(
                dream_id=excerpt_data.get("dream_id"),
                dream_title=excerpt_data.get("dream_title"),
                dream_date=excerpt_data.get("dream_date", ""),
                excerpt=excerpt_data.get("excerpt", ""),
                relevance_score=excerpt_data.get("relevance_score"),
            ))

        message_responses.append(
            MessageResponse(
                id=msg.id,
                role=msg.role.value,
                content=msg.content,
                sources=sources,
                query_type=msg.query_type.value if msg.query_type else None,
                processing_time_ms=msg.processing_time_ms,
                created_at=msg.created_at,
            )
        )

    return ChatWithMessagesResponse(
        id=chat.id,
        name=chat.name,
        messages=message_responses,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
    )


@chat_router.put("/{chat_id}", response_model=ChatResponse)
async def update_chat(
        chat_id: int,
        data: ChatUpdate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    chat = await chat_repo.update_chat(chat_id, user_id, data.name)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    message_count = await chat_repo.get_message_count(chat.id)

    return ChatResponse(
        id=chat.id,
        name=chat.name,
        message_count=message_count,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
    )


@chat_router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
        chat_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    deleted = await chat_repo.delete_chat(chat_id, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    cache_key = _get_agent_cache_key(user_id, chat_id)
    async with _agent_cache_lock:
        if cache_key in _agent_cache:
            del _agent_cache[cache_key]

    return None


@chat_router.post("/{chat_id}/message", response_model=MessageResponse)
async def send_message(
        chat_id: int,
        data: MessageCreate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    start_time = time.time()
    chat_repo = ChatRepository(db)
    dream_repo = DreamRepository(db)

    if not await chat_repo.chat_exists(chat_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    user_message = await chat_repo.add_message(
        chat_id=chat_id,
        role="user",
        content=data.content,
    )

    cache_key = _get_agent_cache_key(user_id, chat_id)
    async with _agent_cache_lock:
        if cache_key not in _agent_cache:
            agent = get_dream_agent(user_id, db)
            result = await chat_repo.get_chat_with_messages(chat_id, user_id)
            if result:
                _, messages = result
                for msg in messages[:-1]:
                    agent.conversation_history.append(
                        ChatMessage(role=msg.role.value, content=msg.content)
                    )

            _agent_cache[cache_key] = agent
        else:
            agent = _agent_cache[cache_key]
            agent.db = db
            agent.tools.db = db
            agent.tools.repo.db = db

    images = [img.model_dump() for img in data.images] if data.images else None
    logger.info(f"Processing message for chat {chat_id}, user {user_id}")
    try:
        response = await agent.chat(data.content, images=images)
    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)

        class FallbackResponse:
            message = "I apologize, but I encountered an issue. Could you please try again?"
            tool_calls = []
            sources = []

        response = FallbackResponse()

    processing_time = int((time.time() - start_time) * 1000)
    enriched_sources = []
    source_dream_ids = []

    for source in response.sources:
        dream_id = source.get("dream_id")
        if dream_id:
            source_dream_ids.append(dream_id)
            dream = await dream_repo.get_by_id(dream_id, user_id)
            if dream:
                enriched_sources.append({
                    "dream_id": dream_id,
                    "dream_title": dream.title,
                    "dream_date": str(dream.dream_date),
                    "excerpt": source.get("excerpt", ""),
                    "relevance_score": source.get("relevance_score"),
                })

    query_type = "conversation"
    if response.tool_calls:
        tool_names = [tc.get("tool", "") for tc in response.tool_calls]
        if any("symbol" in t for t in tool_names):
            query_type = "symbol"
        elif any("character" in t or "archetype" in t for t in tool_names):
            query_type = "character"
        elif any("emotion" in t for t in tool_names):
            query_type = "emotion"
        elif any("theme" in t for t in tool_names):
            query_type = "theme"
        elif any("semantic" in t for t in tool_names):
            query_type = "pattern"
        elif any("dream" in t for t in tool_names):
            query_type = "general"

    assistant_message = await chat_repo.add_message(
        chat_id=chat_id,
        role="assistant",
        content=response.message,
        source_dream_ids=source_dream_ids,
        source_excerpts=enriched_sources,
        query_type=query_type,
        processing_time_ms=processing_time,
    )

    sources = [
        DreamSource(
            dream_id=s["dream_id"],
            dream_title=s.get("dream_title"),
            dream_date=s.get("dream_date", ""),
            excerpt=s.get("excerpt", ""),
            relevance_score=s.get("relevance_score"),
        )
        for s in enriched_sources
    ]

    return MessageResponse(
        id=assistant_message.id,
        role="assistant",
        content=response.message,
        sources=sources,
        query_type=query_type,
        processing_time_ms=processing_time,
        created_at=assistant_message.created_at,
    )


@chat_router.post("/{chat_id}/message/stream")
async def send_message_stream(
        chat_id: int,
        data: MessageCreate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    if not await chat_repo.chat_exists(chat_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    await chat_repo.add_message(
        chat_id=chat_id,
        role="user",
        content=data.content,
    )

    async def generate_stream():
        start_time = time.time()
        full_response = []

        try:
            cache_key = _get_agent_cache_key(user_id, chat_id)
            if cache_key not in _agent_cache:
                agent = get_dream_agent(user_id, db)
                _agent_cache[cache_key] = agent
            else:
                agent = _agent_cache[cache_key]
                agent.db = db
                agent.tools.db = db
                agent.tools.repo.db = db

            async for chunk in agent.chat_stream(data.content):
                full_response.append(chunk)
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"

            processing_time = int((time.time() - start_time) * 1000)
            yield f"data: {json.dumps({'type': 'done', 'processing_time_ms': processing_time})}\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': 'An error occurred while processing your message.'})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@chat_router.post("/{chat_id}/clear-history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_context(
        chat_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)

    if not await chat_repo.chat_exists(chat_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    cache_key = _get_agent_cache_key(user_id, chat_id)
    if cache_key in _agent_cache:
        _agent_cache[cache_key].clear_history()

    return None

@chat_router.post("/query", response_model=MessageResponse)
async def quick_query(
        data: MessageCreate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    start_time = time.time()
    agent = get_dream_agent(user_id, db)
    images = [img.model_dump() for img in data.images] if data.images else None

    try:
        response = await agent.chat(data.content, images=images)
    except Exception as e:
        logger.error(f"Quick query error: {e}", exc_info=True)

        class FallbackResponse:
            message = "I apologize, but I encountered an issue. Could you please try again?"
            tool_calls = []
            sources = []

        response = FallbackResponse()

    processing_time = int((time.time() - start_time) * 1000)
    query_type = "conversation"
    if response.tool_calls:
        tool_names = [tc.get("tool", "") for tc in response.tool_calls]
        if any("symbol" in t for t in tool_names):
            query_type = "symbol"
        elif any("character" in t or "archetype" in t for t in tool_names):
            query_type = "character"
        elif any("emotion" in t for t in tool_names):
            query_type = "emotion"
        elif any("theme" in t for t in tool_names):
            query_type = "theme"
        elif any("semantic" in t for t in tool_names):
            query_type = "pattern"

    sources = [
        DreamSource(
            dream_id=s.get("dream_id"),
            dream_title=s.get("dream_title"),
            dream_date=s.get("dream_date", ""),
            excerpt=s.get("excerpt", ""),
            relevance_score=s.get("relevance_score"),
        )
        for s in response.sources
    ]

    return MessageResponse(
        id=0,
        role="assistant",
        content=response.message,
        sources=sources,
        query_type=query_type,
        processing_time_ms=processing_time,
        created_at=None,
    )

@chat_router.get("/agent/info", response_model=dict)
async def get_agent_info():
    from app.config import settings

    return {
        "name": "Dream Analyst Agent",
        "model": settings.agent_model,
        "description": "Jungian dream analyst with access to your dream journal",
        "capabilities": [
            "Natural conversation about dreams and their meanings",
            "Search and analyze symbols from your dream history",
            "Explore character patterns and archetypes",
            "Track emotional patterns across dreams",
            "Identify recurring themes and their evolution",
            "Semantic search across all dream narratives",
            "Personalized insights based on YOUR associations",
        ],
        "tools": [
            {"name": "search_symbols", "description": "Search symbols by name or category"},
            {"name": "get_symbol_details", "description": "Get detailed symbol analysis"},
            {"name": "get_symbol_patterns", "description": "Find symbol co-occurrences and correlations"},
            {"name": "search_characters", "description": "Search dream characters"},
            {"name": "get_character_details", "description": "Get character analysis with archetypes"},
            {"name": "get_archetype_analysis", "description": "Analyze Jungian archetypes (shadow, anima, etc.)"},
            {"name": "get_emotion_overview", "description": "Overview of emotions in dreams"},
            {"name": "get_emotion_correlations", "description": "Find emotion triggers and patterns"},
            {"name": "get_themes_overview", "description": "List all themes with frequency"},
            {"name": "get_theme_analysis", "description": "Deep dive into specific themes"},
            {"name": "search_dreams", "description": "Text search across dreams"},
            {"name": "get_recent_dreams", "description": "Get recent dream entries"},
            {"name": "get_dream_details", "description": "Full details of a specific dream"},
            {"name": "get_recurring_dreams", "description": "Find recurring dreams"},
            {"name": "semantic_search", "description": "AI-powered semantic search via GraphRAG"},
            {"name": "get_journal_summary", "description": "Summary of dream journal stats"},
        ],
    }
