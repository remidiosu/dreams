from dataclasses import asdict
from typing import List

from fast_graphrag._storage._gdb_igraph import IGraphStorage
from fast_graphrag._types import TIndex
from fast_graphrag._utils import logger


_original_insert_edges = IGraphStorage.insert_edges
_original_are_neighbours = IGraphStorage.are_neighbours
_original_upsert_edge = IGraphStorage.upsert_edge
_original_get_edge_indices = IGraphStorage._get_edge_indices
_original_get_edge_by_index = IGraphStorage.get_edge_by_index


async def _safe_insert_edges(
    self,
    edges=None,
    indices=None,
    attrs=None,
) -> List[TIndex]:
    if indices is not None:
        indices = list(indices)
        if len(indices) == 0:
            return []

        vcount = self._graph.vcount()
        valid_indices = []
        valid_attr_indices = []
        for i, (src, tgt) in enumerate(indices):
            if src < vcount and tgt < vcount and src != tgt:
                valid_indices.append((src, tgt))
                valid_attr_indices.append(i)
            else:
                logger.warning(
                    f"Skipping edge ({src}, {tgt}): vertex out of range (vcount={vcount})"
                )

        if len(valid_indices) == 0:
            return []

        filtered_attrs = None
        if attrs and valid_attr_indices:
            filtered_attrs = {}
            for key, values in attrs.items():
                vals = list(values)
                filtered_attrs[key] = [vals[i] for i in valid_attr_indices]

        self._graph.add_edges(valid_indices, attributes=filtered_attrs)
        return list(range(self._graph.ecount() - len(valid_indices), self._graph.ecount()))

    elif edges is not None:
        edges = list(edges)
        if len(edges) == 0:
            return []

        valid_edges = []
        for edge in edges:
            try:
                self._graph.vs.find(name=edge.source)
                self._graph.vs.find(name=edge.target)
                valid_edges.append(edge)
            except ValueError:
                logger.warning(
                    f"Skipping edge '{edge.source}' -> '{edge.target}': vertex not found"
                )

        if len(valid_edges) == 0:
            return []

        self._graph.add_edges(
            ((edge.source, edge.target) for edge in valid_edges),
            attributes=type(valid_edges[0]).to_attrs(edges=valid_edges),
        )
        return list(range(self._graph.ecount() - len(valid_edges), self._graph.ecount()))

    return []


async def _safe_are_neighbours(
    self, source_node, target_node
) -> bool:
    try:
        vcount = self._graph.vcount()
        if isinstance(source_node, int) and source_node >= vcount:
            return False
        if isinstance(target_node, int) and target_node >= vcount:
            return False
        return self._graph.get_eid(source_node, target_node, directed=False, error=False) != -1
    except Exception:
        return False


async def _safe_upsert_edge(self, edge, edge_index):
    if edge_index is not None:
        if edge_index >= self._graph.ecount():
            logger.error(
                f"Trying to update edge with index {edge_index} but graph has only {self._graph.ecount()} edges."
            )
            raise ValueError(f"Index {edge_index} is out of bounds")
        already_edge = self._graph.es[edge_index]
        already_edge.update_attributes(**edge.to_attrs(edge=edge))
        return already_edge.index
    else:
        try:
            self._graph.vs.find(name=edge.source)
            self._graph.vs.find(name=edge.target)
        except ValueError as e:
            logger.warning(f"Skipping edge upsert '{edge.source}' -> '{edge.target}': {e}")
            return None
        return self._graph.add_edge(**asdict(edge)).index


async def _safe_get_edge_indices(self, source_node, target_node):
    try:
        if type(source_node) is TIndex:
            source_node = self._graph.vs.find(name=source_node).index
        if type(target_node) is TIndex:
            target_node = self._graph.vs.find(name=target_node).index

        vcount = self._graph.vcount()
        if isinstance(source_node, int) and source_node >= vcount:
            return iter([])
        if isinstance(target_node, int) and target_node >= vcount:
            return iter([])

        edges = self._graph.es.select(_source=source_node, _target=target_node)
        return (edge.index for edge in edges)
    except (ValueError, Exception) as e:
        logger.warning(f"Error getting edge indices for ({source_node}, {target_node}): {e}")
        return iter([])


async def _safe_get_edge_by_index(self, index):
    try:
        if index >= self._graph.ecount():
            return None
        edge = self._graph.es[index]
        if edge.source >= self._graph.vcount() or edge.target >= self._graph.vcount():
            return None
        return self.config.edge_cls(
            source=self._graph.vs[edge.source]["name"],
            target=self._graph.vs[edge.target]["name"],
            **edge.attributes(),
        )
    except Exception as e:
        logger.warning(f"Error getting edge by index {index}: {e}")
        return None


def apply_graphrag_igraph_patch():
    IGraphStorage.insert_edges = _safe_insert_edges
    IGraphStorage.are_neighbours = _safe_are_neighbours
    IGraphStorage.upsert_edge = _safe_upsert_edge
    IGraphStorage._get_edge_indices = _safe_get_edge_indices
    IGraphStorage.get_edge_by_index = _safe_get_edge_by_index
    logger.info("Applied igraph safety patch for fast-graphrag")
