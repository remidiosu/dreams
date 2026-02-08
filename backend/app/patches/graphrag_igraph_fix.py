from dataclasses import asdict
from typing import List, Optional, Iterable, Tuple, Mapping, Any, Sequence, Union

from fast_graphrag._storage._gdb_igraph import IGraphStorage
from fast_graphrag._types import GTEdge, GTId, TIndex
from fast_graphrag._utils import logger


async def _safe_are_neighbours(self, source_node: Union[GTId, TIndex], target_node: Union[GTId, TIndex]) -> bool:
    vcount = self._graph.vcount()
    if isinstance(source_node, int) and source_node >= vcount:
        return False
    if isinstance(target_node, int) and target_node >= vcount:
        return False
    return self._graph.get_eid(source_node, target_node, directed=False, error=False) != -1


async def _safe_insert_edges(
    self,
    edges: Optional[Iterable[GTEdge]] = None,
    indices: Optional[Iterable[Tuple[TIndex, TIndex]]] = None,
    attrs: Optional[Mapping[str, Sequence[Any]]] = None,
) -> List[TIndex]:
    if indices is not None:
        assert edges is None, "Cannot provide both indices and edges."
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
                logger.warning(f"Skipping edge ({src}, {tgt}): vertex out of range (vcount={vcount})")

        if len(valid_indices) == 0:
            return []

        filtered_attrs = None
        if attrs:
            filtered_attrs = {}
            for key, values in attrs.items():
                vals = list(values)
                filtered_attrs[key] = [vals[i] for i in valid_attr_indices]

        self._graph.add_edges(valid_indices, attributes=filtered_attrs)
        return list(range(self._graph.ecount() - len(valid_indices), self._graph.ecount()))

    elif edges is not None:
        assert indices is None and attrs is None, "Cannot provide both indices and edges."
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
                logger.warning(f"Skipping edge '{edge.source}' -> '{edge.target}': vertex not found")

        if len(valid_edges) == 0:
            return []

        self._graph.add_edges(
            ((edge.source, edge.target) for edge in valid_edges),
            attributes=type(valid_edges[0]).to_attrs(edges=valid_edges),
        )
        return list(range(self._graph.ecount() - len(valid_edges), self._graph.ecount()))

    return []


async def _safe_upsert_edge(self, edge: GTEdge, edge_index: Union[TIndex, None]) -> TIndex:
    if edge_index is not None:
        if edge_index >= self._graph.ecount():
            logger.error(f"Edge index {edge_index} out of bounds (ecount={self._graph.ecount()})")
            raise ValueError(f"Index {edge_index} is out of bounds")
        already_edge = self._graph.es[edge_index]
        already_edge.update_attributes(**edge.to_attrs(edge=edge))
        return already_edge.index
    else:
        try:
            self._graph.vs.find(name=edge.source)
            self._graph.vs.find(name=edge.target)
        except ValueError:
            logger.warning(f"Skipping edge upsert '{edge.source}' -> '{edge.target}': vertex not found")
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
    except ValueError:
        return iter([])


def apply_graphrag_igraph_patch():
    IGraphStorage.are_neighbours = _safe_are_neighbours
    IGraphStorage.insert_edges = _safe_insert_edges
    IGraphStorage.upsert_edge = _safe_upsert_edge
    IGraphStorage._get_edge_indices = _safe_get_edge_indices
    logger.info("Applied igraph safety patch for fast-graphrag")
