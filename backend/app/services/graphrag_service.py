import asyncio
import gzip
import shutil
import pickle
import re
import time
from pathlib import Path
from typing import Optional, AsyncGenerator

import instructor
from fast_graphrag import GraphRAG
from fast_graphrag._llm import OpenAILLMService, OpenAIEmbeddingService

from app.config import settings
from app.logger import logger
from app.schemas.graph_service_data import DREAM_DOMAIN, DREAM_ENTITY_TYPES, DREAM_EXAMPLE_QUERIES, \
    QueryResult, GraphStats


class GraphRAGService:
    EMBEDDING_DIM = 768

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.working_dir = self._get_working_dir()
        self._graph: Optional[GraphRAG] = None

    def _get_working_dir(self) -> Path:
        base_dir = Path(settings.graph_storage_path) / str(self.user_id)
        base_dir.mkdir(parents=True, exist_ok=True)

        return base_dir

    def _create_llm_service(self) -> OpenAILLMService:
        return OpenAILLMService(
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            api_key=settings.gemini_api_key,
            mode=instructor.Mode.JSON,
        )

    def _create_embedding_service(self) -> OpenAIEmbeddingService:
        logger.info("Using Gemini embeddings (768-dim)")
        return OpenAIEmbeddingService(
            model=settings.text_embedding_model,
            base_url=settings.llm_base_url,
            api_key=settings.gemini_api_key,
            embedding_dim=self.EMBEDDING_DIM,
        )

    def _get_graph(self) -> GraphRAG:
        if self._graph is None:
            embedding_service = self._create_embedding_service()
            llm_service = self._create_llm_service()

            try:
                config = GraphRAG.Config(
                    llm_service=llm_service,
                    embedding_service=embedding_service,
                )

                if hasattr(config, 'embedding_dim'):
                    config.embedding_dim = self.EMBEDDING_DIM
                    logger.info(f"Set config.embedding_dim to {self.EMBEDDING_DIM}")

                if hasattr(config, 'vector_db_config'):
                    if hasattr(config.vector_db_config, 'embedding_dim'):
                        config.vector_db_config.embedding_dim = self.EMBEDDING_DIM
                    if hasattr(config.vector_db_config, 'dim'):
                        config.vector_db_config.dim = self.EMBEDDING_DIM

            except Exception as e:
                logger.warning(f"Error creating config with embedding_dim: {e}")
                config = GraphRAG.Config(
                    llm_service=llm_service,
                    embedding_service=embedding_service,
                )

            self._graph = GraphRAG(
                working_dir=str(self.working_dir),
                domain=DREAM_DOMAIN,
                example_queries="\n".join(DREAM_EXAMPLE_QUERIES),
                entity_types=DREAM_ENTITY_TYPES,
                config=config,
            )

            logger.info(f"Created GraphRAG instance for user {self.user_id}")

        return self._graph

    @property
    def graph_exists(self) -> bool:
        return len(list(self.working_dir.glob("*.pkl"))) > 0

    async def index_dream(
        self,
        dream_id: int,
        content: str,
    ) -> tuple[bool, Optional[str]]:
        try:
            logger.info(f"Starting index for dream {dream_id}")
            graph = self._get_graph()
            logger.debug(f"Content length: {len(content)} chars")

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, graph.insert, content)

            logger.info(f"Successfully indexed dream {dream_id}")
            return True, None

        except Exception as e:
            logger.error(f"Error indexing dream {dream_id}: {e}", exc_info=True)
            return False, str(e)

    async def index_dreams_batch(
        self,
        dreams: list[dict],
    ) -> tuple[int, int, list[str], list[int]]:
        success_count = 0
        failure_count = 0
        errors = []
        successful_ids = []

        for dream in dreams:
            success, error = await self.index_dream(
                dream_id=dream["id"],
                content=dream["content"],
            )

            if success:
                success_count += 1
                successful_ids.append(dream["id"])
            else:
                failure_count += 1
                errors.append(f"Dream {dream['id']}: {error}")

        return success_count, failure_count, errors, successful_ids

    async def query(
        self,
        question: str,
        with_references: bool = True,
    ) -> QueryResult:
        start_time = time.time()

        if not self.graph_exists:
            return QueryResult(
                response="I don't have any dreams indexed yet. Please add some dreams first, then I can help you explore patterns and meanings.",
                sources=[],
                query_type="empty",
                processing_time_ms=0,
            )

        try:
            graph = self._get_graph()
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: graph.query(question, with_references=with_references)
            )

            processing_time = int((time.time() - start_time) * 1000)
            sources = self._parse_sources(result) if with_references else []
            query_type = self._classify_query(question)

            return QueryResult(
                response=result.response,
                sources=sources,
                query_type=query_type,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Query error: {e}", exc_info=True)
            processing_time = int((time.time() - start_time) * 1000)
            return QueryResult(
                response="I encountered an error while searching your dreams. Please try again.",
                sources=[],
                query_type="error",
                processing_time_ms=processing_time,
            )

    async def query_stream(
        self,
        question: str,
    ) -> AsyncGenerator[str, None]:
        result = await self.query(question, with_references=False)

        words = result.response.split()
        chunk_size = 3

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            if i > 0:
                chunk = " " + chunk
            yield chunk
            await asyncio.sleep(0.02)

    def _parse_sources(self, result) -> list[dict]:
        sources = []

        if hasattr(result, 'references') and result.references:
            for ref in result.references:
                dream_id = self._extract_dream_id(str(ref))
                sources.append({
                    "dream_id": dream_id,
                    "excerpt": str(ref)[:500] if len(str(ref)) > 500 else str(ref),
                    "relevance_score": None,
                })

        if hasattr(result, 'context') and result.context:
            contexts = result.context if isinstance(result.context, list) else [result.context]
            for ctx in contexts:
                dream_id = self._extract_dream_id(str(ctx))
                if dream_id and not any(s.get("dream_id") == dream_id for s in sources):
                    sources.append({
                        "dream_id": dream_id,
                        "excerpt": str(ctx)[:500],
                        "relevance_score": None,
                    })

        return sources

    def _extract_dream_id(self, text: str) -> Optional[int]:
        match = re.search(r'\[Dream ID:\s*(\d+)\]', text)
        if match:
            return int(match.group(1))
        return None

    def _classify_query(self, question: str) -> str:
        question_lower = question.lower()

        keywords = {
            "symbol": ["symbol", "mean", "represent", "signify", "symbolize"],
            "character": ["character", "person", "who", "shadow", "anima", "animus", "figure"],
            "pattern": ["pattern", "recurring", "repeat", "trend", "over time", "frequency", "often"],
            "emotion": ["emotion", "feel", "feeling", "mood", "felt", "anxiety", "fear", "joy"],
            "theme": ["theme", "about", "meaning", "motif"],
            "archetype": ["archetype", "shadow", "anima", "animus", "wise", "trickster", "hero"],
        }

        for query_type, words in keywords.items():
            if any(word in question_lower for word in words):
                return query_type

        return "general"

    async def get_stats(self) -> GraphStats:
        if not self.graph_exists:
            return GraphStats()

        stats = GraphStats()

        graph_file = self.working_dir / "graph_igraph_data.pklz"
        if graph_file.exists():
            try:
                with gzip.open(graph_file, "rb") as f:
                    graph_data = pickle.load(f)

                if hasattr(graph_data, 'vcount'):
                    stats.entity_count = graph_data.vcount()
                if hasattr(graph_data, 'ecount'):
                    stats.relationship_count = graph_data.ecount()
            except Exception as e:
                logger.warning(f"Could not read graph_igraph_data.pklz: {e}")

        metadata_file = self.working_dir / "entities_hnsw_metadata.pkl"
        if metadata_file.exists() and stats.entity_count == 0:
            try:
                with open(metadata_file, "rb") as f:
                    metadata = pickle.load(f)
                    if isinstance(metadata, (list, dict)):
                        stats.entity_count = len(metadata)
            except Exception as e:
                logger.warning(f"Could not read entities_hnsw_metadata.pkl: {e}")

        chunks_file = self.working_dir / "chunks_kv_data.pkl"
        if chunks_file.exists():
            try:
                with open(chunks_file, "rb") as f:
                    chunks = pickle.load(f)
                    if isinstance(chunks, dict):
                        stats.chunk_count = len(chunks)
            except Exception as e:
                logger.warning(f"Could not read chunks_kv_data.pkl: {e}")

        return stats

    async def export_graph(self) -> dict:
        if not self.graph_exists:
            return {"nodes": [], "edges": [], "stats": {"node_count": 0, "edge_count": 0}}

        nodes = []
        edges = []

        graph_file = self.working_dir / "graph_igraph_data.pklz"
        if graph_file.exists():
            try:
                with gzip.open(graph_file, "rb") as f:
                    graph = pickle.load(f)

                logger.debug(f"Graph type: {type(graph)}")
                logger.debug(f"Vertex count: {graph.vcount() if hasattr(graph, 'vcount') else 'N/A'}")
                logger.debug(f"Edge count: {graph.ecount() if hasattr(graph, 'ecount') else 'N/A'}")

                if hasattr(graph, 'vs') and graph.vcount() > 0:
                    vertex_attrs = graph.vs.attributes()
                    logger.debug(f"Vertex attributes available: {vertex_attrs}")

                    for i in range(min(5, graph.vcount())):
                        v = graph.vs[i]
                        name = v.get('name', 'N/A') if hasattr(v, 'get') else (
                            v['name'] if 'name' in v.attributes() else 'N/A')
                        type_attr = v.get('type', 'N/A') if hasattr(v, 'get') else (
                            v['type'] if 'type' in v.attributes() else 'N/A')
                        desc = v.get('description', 'N/A') if hasattr(v, 'get') else (
                            v['description'] if 'description' in v.attributes() else 'N/A')
                        logger.debug(f"Vertex {i}: name='{name}', type='{type_attr}', desc='{str(desc)[:50]}...'")

                    for i, vertex in enumerate(graph.vs):
                        entity_name = vertex['name'] if 'name' in vertex.attributes() else f"Entity {i}"
                        entity_type = vertex['type'] if 'type' in vertex.attributes() else 'ENTITY'
                        entity_desc = vertex['description'] if 'description' in vertex.attributes() else ''

                        if entity_name.startswith("Entity ") or entity_name == "":
                            for attr in ['label', 'title', 'id']:
                                if attr in vertex.attributes():
                                    alt_name = vertex[attr]
                                    if alt_name and not alt_name.startswith("Entity "):
                                        entity_name = alt_name
                                        break

                        normalized_type = str(entity_type).lower().replace("_", "").strip()

                        nodes.append({
                            "id": str(i),
                            "type": normalized_type,
                            "label": str(entity_name),
                            "description": str(entity_desc)[:300] if entity_desc else "",
                            "size": 1,
                        })

                    logger.info(f"Extracted {len(nodes)} nodes from igraph vertices")

                    for i in range(min(5, len(nodes))):
                        logger.debug(
                            f"Node {i}: id={nodes[i]['id']}, type={nodes[i]['type']}, label={nodes[i]['label']}")

                    type_counts = {}
                    for n in nodes:
                        type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1
                    logger.debug(f"Node type distribution: {type_counts}")

                if hasattr(graph, 'es') and graph.ecount() > 0:
                    edge_attrs = graph.es.attributes()
                    logger.debug(f"Edge attributes: {edge_attrs}")

                    for edge in graph.es:
                        source_idx = edge.source
                        target_idx = edge.target

                        rel_type = "related"
                        weight = 1.0

                        if 'description' in edge.attributes():
                            desc = edge['description']
                            if desc and isinstance(desc, str):
                                rel_type = desc.split('.')[0][:50]

                        for attr_name in ['relationship', 'type', 'label', 'name']:
                            if attr_name in edge.attributes():
                                val = edge[attr_name]
                                if val and isinstance(val, str):
                                    rel_type = val[:50]
                                    break

                        if 'weight' in edge.attributes():
                            try:
                                weight = float(edge['weight'])
                            except (ValueError, TypeError):
                                pass

                        if source_idx < len(nodes) and target_idx < len(nodes):
                            edges.append({
                                "source": str(source_idx),
                                "target": str(target_idx),
                                "relationship": rel_type,
                                "weight": weight,
                            })

                    logger.debug(f"Extracted {len(edges)} edges from igraph")

            except Exception as e:
                logger.error(f"Could not read graph_igraph_data.pklz: {e}", exc_info=True)

        logger.info(f"Exported graph: {len(nodes)} nodes, {len(edges)} edges")
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {"node_count": len(nodes), "edge_count": len(edges)},
        }

    def _parse_entity_string(self, entity_str: str) -> dict:
        result = {"name": entity_str, "type": "entity", "description": ""}

        try:
            lines = entity_str.strip().split("\n")
            if lines:
                first_line = lines[0]
                if first_line.startswith("[") and "]" in first_line:
                    bracket_end = first_line.index("]")
                    result["type"] = first_line[1:bracket_end].lower()
                    result["name"] = first_line[bracket_end + 1:].strip()
                else:
                    result["name"] = first_line

                if len(lines) > 1:
                    desc_line = lines[1]
                    if desc_line.startswith("[DESCRIPTION]"):
                        result["description"] = desc_line.replace("[DESCRIPTION]", "").strip()
                    else:
                        result["description"] = desc_line.strip()
        except Exception:
            pass

        return result

    async def clear_graph(self) -> bool:
        try:
            if self.working_dir.exists():
                shutil.rmtree(self.working_dir)
                self.working_dir.mkdir(parents=True, exist_ok=True)
            self._graph = None

            return True
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            return False


def get_graphrag_service(user_id: int) -> GraphRAGService:
    return GraphRAGService(user_id)
