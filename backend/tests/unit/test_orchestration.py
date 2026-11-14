import pytest
from app.orchestration.graph import build_langgraph_pipeline, langgraph_app


def test_langgraph_structure():
    """Validates that the LangGraph pipeline is constructed with proper nodes and edges."""
    pipeline = build_langgraph_pipeline()
    graph_dict = pipeline.get_graph()

    # Verify all expected agent nodes are present in the compiled graph
    node_keys = list(graph_dict.nodes.keys())
    for expected_node in ["supervisor", "wave_1", "testing", "debugging", "contribution"]:
        assert expected_node in node_keys, f"Expected node '{expected_node}' not found in LangGraph nodes: {node_keys}"

    # Verify directed edges
    edges = [(e.source, e.target) for e in graph_dict.edges]
    assert ("__start__", "supervisor") in edges
    assert ("supervisor", "wave_1") in edges
    assert ("wave_1", "testing") in edges
    assert ("debugging", "testing") in edges
    assert ("contribution", "__end__") in edges
