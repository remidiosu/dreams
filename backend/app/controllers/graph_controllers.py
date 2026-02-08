import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.logger import logger
from app.database import get_db
from app.dependencies.auth import get_current_user_id
from app.repositories.graph_repository import GraphRepository
from app.services.graphrag_service import get_graphrag_service
from app.services.indexing_service import DreamIndexingService
from app.data_models.graph_data import (
    GraphStatus,
    IndexResult,
    IndexDreamResult,
    GraphExport,
    GraphNode,
    GraphEdge,
    EntityListResponse,
    EntitySummary,
    EntityDetail,
)


graph_router = APIRouter(prefix="/graph", tags=["Graph"])


@graph_router.get("/status", response_model=GraphStatus)
async def get_graph_status(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    graph_repo = GraphRepository(db)
    graphrag = get_graphrag_service(user_id)
    stats = await graph_repo.get_indexing_stats(user_id)

    entity_count = None
    relationship_count = None

    if graphrag.graph_exists:
        graph_stats = await graphrag.get_stats()
        entity_count = graph_stats.entity_count
        relationship_count = graph_stats.relationship_count

    return GraphStatus(
        total_dreams=stats["total_dreams"],
        indexed_dreams=stats["indexed_dreams"],
        pending_dreams=stats["pending_dreams"],
        last_indexed_at=stats["last_indexed_at"],
        graph_exists=graphrag.graph_exists,
        entity_count=entity_count,
        relationship_count=relationship_count,
    )


@graph_router.post("/index", response_model=IndexResult)
async def index_pending_dreams(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    start_time = time.time()
    graph_repo = GraphRepository(db)
    indexing_service = DreamIndexingService(db)
    dreams = await graph_repo.get_unindexed_dreams(user_id)

    if not dreams:
        return IndexResult(
            success=True,
            dreams_indexed=0,
            dreams_failed=0,
            errors=[],
            processing_time_ms=0,
        )

    logger.info(f"Preparing {len(dreams)} dreams for indexing (user {user_id})")
    dream_ids = [dream.id for dream in dreams]
    dreams_to_index = await indexing_service.prepare_dreams_batch(dream_ids, user_id)

    if not dreams_to_index:
        return IndexResult(
            success=True,
            dreams_indexed=0,
            dreams_failed=0,
            errors=["No dreams could be prepared for indexing"],
            processing_time_ms=int((time.time() - start_time) * 1000),
        )

    logger.info(f"Prepared {len(dreams_to_index)} dreams, starting GraphRAG indexing")
    graphrag = get_graphrag_service(user_id)

    async def save_chunk_progress(indexed_ids: list[int]):
        await graph_repo.mark_dreams_indexed(indexed_ids)
        await graph_repo.increment_user_indexed_count(user_id, len(indexed_ids))
        await db.commit()
        logger.info(f"Saved progress: {len(indexed_ids)} dreams committed to DB")

    success_count, failure_count, errors, successful_ids = await graphrag.index_dreams_batch(
        dreams_to_index,
        on_chunk_success=save_chunk_progress,
    )

    processing_time = int((time.time() - start_time) * 1000)
    logger.info(f"Indexing complete: {success_count} success, {failure_count} failed in {processing_time}ms")

    return IndexResult(
        success=failure_count == 0,
        dreams_indexed=success_count,
        dreams_failed=failure_count,
        errors=errors,
        processing_time_ms=processing_time,
    )


@graph_router.post("/index/{dream_id}", response_model=IndexDreamResult)
async def index_single_dream(
        dream_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    start_time = time.time()
    graph_repo = GraphRepository(db)
    indexing_service = DreamIndexingService(db)
    content = await indexing_service.prepare_dream_for_indexing(dream_id, user_id)

    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dream not found")

    logger.info(f"Indexing dream {dream_id} ({len(content)} chars)")
    graphrag = get_graphrag_service(user_id)
    success, error = await graphrag.index_dream(
        dream_id=dream_id,
        content=content,
    )
    if success:
        await graph_repo.mark_dream_indexed(dream_id)
        await graph_repo.increment_user_indexed_count(user_id, 1)
        await db.commit()

    processing_time = int((time.time() - start_time) * 1000)

    return IndexDreamResult(
        success=success,
        dream_id=dream_id,
        error=error,
        processing_time_ms=processing_time,
    )


@graph_router.post("/reindex", response_model=IndexResult)
async def reindex_all_dreams(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    start_time = time.time()
    graph_repo = GraphRepository(db)
    indexing_service = DreamIndexingService(db)
    graphrag = get_graphrag_service(user_id)

    logger.info(f"Clearing graph for user {user_id}")
    await graphrag.clear_graph()
    await graph_repo.reset_all_indexed_flags(user_id)

    dreams = await graph_repo.get_all_dreams_for_indexing(user_id)

    if not dreams:
        return IndexResult(
            success=True,
            dreams_indexed=0,
            dreams_failed=0,
            errors=[],
            processing_time_ms=int((time.time() - start_time) * 1000),
        )

    logger.info(f"Preparing {len(dreams)} dreams for reindexing (user {user_id})")
    dream_ids = [dream.id for dream in dreams]
    dreams_to_index = await indexing_service.prepare_dreams_batch(dream_ids, user_id)

    if not dreams_to_index:
        return IndexResult(
            success=True,
            dreams_indexed=0,
            dreams_failed=0,
            errors=["No dreams could be prepared for indexing"],
            processing_time_ms=int((time.time() - start_time) * 1000),
        )

    logger.info(f"Prepared {len(dreams_to_index)} dreams, starting GraphRAG reindexing")

    total_saved = 0
    async def save_reindex_progress(indexed_ids: list[int]):
        nonlocal total_saved
        await graph_repo.mark_dreams_indexed(indexed_ids)
        total_saved += len(indexed_ids)
        await graph_repo.update_user_indexed_count(user_id, total_saved)
        await db.commit()
        logger.info(f"Saved reindex progress: {len(indexed_ids)} dreams committed to DB")

    success_count, failure_count, errors, successful_ids = await graphrag.index_dreams_batch(
        dreams_to_index,
        on_chunk_success=save_reindex_progress,
    )

    processing_time = int((time.time() - start_time) * 1000)

    logger.info(f"Reindexing complete: {success_count} success, {failure_count} failed in {processing_time}ms")

    return IndexResult(
        success=failure_count == 0,
        dreams_indexed=success_count,
        dreams_failed=failure_count,
        errors=errors,
        processing_time_ms=processing_time,
    )


@graph_router.get("/export", response_model=GraphExport)
async def export_graph(
        user_id: int = Depends(get_current_user_id),
):
    graphrag = get_graphrag_service(user_id)

    if not graphrag.graph_exists:
        return GraphExport(nodes=[], edges=[], stats={"node_count": 0, "edge_count": 0})

    result = await graphrag.export_graph()

    nodes = [
        GraphNode(
            id=n["id"],
            type=n["type"],
            label=n["label"],
            size=n["size"],
            metadata=n.get("metadata", {}),
        )
        for n in result.get("nodes", [])
    ]

    edges = [
        GraphEdge(
            source=e["source"],
            target=e["target"],
            relationship=e["relationship"],
            weight=e["weight"],
        )
        for e in result.get("edges", [])
    ]

    return GraphExport(
        nodes=nodes,
        edges=edges,
        stats=result.get("stats", {}),
    )


@graph_router.get("/entities", response_model=EntityListResponse)
async def list_entities(
        entity_type: Optional[str] = None,
        user_id: int = Depends(get_current_user_id),
):
    graphrag = get_graphrag_service(user_id)

    if not graphrag.graph_exists:
        return EntityListResponse(data=[], total=0)

    result = await graphrag.export_graph()
    nodes = result.get("nodes", [])

    if entity_type:
        nodes = [n for n in nodes if n.get("type", "").lower() == entity_type.lower()]

    entities = [
        EntitySummary(
            name=n.get("label", n.get("id", "")),
            type=n.get("type", "entity"),
            occurrence_count=n.get("size", 1),
            connected_entities=0,  
            first_seen=None,
            last_seen=None,
        )
        for n in nodes
    ]

    return EntityListResponse(data=entities, total=len(entities))


@graph_router.get("/entity/{entity_name}", response_model=EntityDetail)
async def get_entity(
        entity_name: str,
        user_id: int = Depends(get_current_user_id),
):
    graphrag = get_graphrag_service(user_id)

    if not graphrag.graph_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No graph exists")

    result = await graphrag.export_graph()
    nodes = result.get("nodes", [])
    edges = result.get("edges", [])

    entity = None
    for n in nodes:
        if n.get("label", "").lower() == entity_name.lower() or n.get("id", "").lower() == entity_name.lower():
            entity = n
            break

    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

    entity_id = entity.get("id", entity.get("label", ""))
    connected = []

    for edge in edges:
        if edge.get("source") == entity_id:
            connected.append({
                "name": edge.get("target"),
                "type": "unknown",
                "relationship": edge.get("relationship"),
                "weight": edge.get("weight", 1.0),
            })
        elif edge.get("target") == entity_id:
            connected.append({
                "name": edge.get("source"),
                "type": "unknown",
                "relationship": edge.get("relationship"),
                "weight": edge.get("weight", 1.0),
            })

    return EntityDetail(
        name=entity.get("label", entity.get("id", "")),
        type=entity.get("type", "entity"),
        description=None,
        occurrence_count=entity.get("size", 1),
        connected_entities=connected,
        dream_appearances=[], 
    )


@graph_router.get("/preview/{dream_id}", response_model=dict)
async def preview_dream_content(
        dream_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    indexing_service = DreamIndexingService(db)

    content = await indexing_service.prepare_dream_for_indexing(dream_id, user_id)

    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dream not found")

    return {
        "dream_id": dream_id,
        "content_length": len(content),
        "content": content,
    }
