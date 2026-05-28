"""LangGraph graph for the multi-RAG pipeline."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from services.rag.nodes import (
    expand_query_node,
    generate_node,
    grade_retrieval_node,
    hydrate_parents_node,
    rerank_node,
    retrieve_node,
    rewrite_node,
    safety_validate_node,
    sql_table_node,
    validate_node,
)
from services.rag.state import RAGState

_checkpointer = MemorySaver()

_MAX_RETRIES = 2


def get_checkpointer() -> MemorySaver:
    return _checkpointer


def _route_after_grade(state: RAGState) -> str:
    if state.get("needs_broader_query") and (state.get("retry_count") or 0) <= _MAX_RETRIES:
        return "retry"
    return "continue"


def _route_after_validate(state: RAGState) -> str:
    if state.get("needs_broader_query") and (state.get("retry_count") or 0) <= _MAX_RETRIES:
        return "retry"
    return "continue"


def build_graph(db):
    from sqlalchemy.ext.asyncio import AsyncSession  # local import avoids circular dep

    async def _retrieve(state: RAGState) -> RAGState:
        return await retrieve_node(db, state)

    async def _hydrate(state: RAGState) -> RAGState:
        return await hydrate_parents_node(db, state)

    async def _sql(state: RAGState) -> RAGState:
        return await sql_table_node(db, state)

    graph = StateGraph(RAGState)

    graph.add_node("rewrite", rewrite_node)
    graph.add_node("sql_tables", _sql)
    graph.add_node("expand_query", expand_query_node)
    graph.add_node("retrieve", _retrieve)
    graph.add_node("rerank", rerank_node)
    graph.add_node("grade_retrieval", grade_retrieval_node)
    graph.add_node("hydrate_parents", _hydrate)
    graph.add_node("generate", generate_node)
    graph.add_node("validate", validate_node)
    graph.add_node("safety_validate", safety_validate_node)

    graph.add_edge(START, "rewrite")
    graph.add_edge("rewrite", "sql_tables")
    graph.add_edge("sql_tables", "expand_query")
    graph.add_edge("expand_query", "retrieve")
    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "grade_retrieval")
    graph.add_edge("hydrate_parents", "generate")
    graph.add_edge("generate", "validate")
    graph.add_edge("safety_validate", END)

    graph.add_conditional_edges(
        "grade_retrieval",
        _route_after_grade,
        {"retry": "expand_query", "continue": "hydrate_parents"},
    )

    graph.add_conditional_edges(
        "validate",
        _route_after_validate,
        {"retry": "expand_query", "continue": "safety_validate"},
    )

    return graph.compile(checkpointer=_checkpointer)
