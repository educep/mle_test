"""
This module contains tests for comparing graph structures in the pharmaceutical data pipeline.

The tests are designed to verify that graphs generated from different formats
(e.g., GML and JSON) have the same nodes and edges, ensuring consistency
across different representations of the graph data.

Functions:
    compare_graphs: Compares two graphs to check if they have the same nodes and edges.

Classes:
    TestGraphComparison: A unittest.TestCase subclass that tests the graph
    comparison functionality.

Usage:
    Run this module with unittest to execute the graph comparison tests.
    Example:
        python -m unittest tests/test_graph_comparison.py
"""


# External imports
import unittest
from pathlib import Path

# Internal imports
from src.utils import load_graph_from_gml, load_graph_from_json


def compare_graphs(graph1, graph2):
    """
    Compare two graphs to check if they have the same nodes and edges.

    Args:
        graph1: First NetworkX graph
        graph2: Second NetworkX graph

    Returns:
        dict: Comparison results with the following keys:
            - same_nodes: Boolean indicating if both graphs have the same nodes
            - same_edges: Boolean indicating if both graphs have the same edges
            - missing_nodes: Set of nodes in graph1 but not in graph2
            - extra_nodes: Set of nodes in graph2 but not in graph1
            - missing_edges: Set of edges in graph1 but not in graph2
            - extra_edges: Set of edges in graph2 but not in graph1
    """
    # Get nodes and edges from both graphs
    nodes1 = set(graph1.nodes())
    nodes2 = set(graph2.nodes())
    edges1 = set(graph1.edges())
    edges2 = set(graph2.edges())

    # Compare nodes
    same_nodes = nodes1 == nodes2
    missing_nodes = nodes1 - nodes2
    extra_nodes = nodes2 - nodes1

    # Compare edges
    same_edges = edges1 == edges2
    missing_edges = edges1 - edges2
    extra_edges = edges2 - edges1

    # Return comparison results
    return {
        "same_nodes": same_nodes,
        "same_edges": same_edges,
        "missing_nodes": missing_nodes,
        "extra_nodes": extra_nodes,
        "missing_edges": missing_edges,
        "extra_edges": extra_edges,
    }


# python -m unittest tests/graph_comparison_test.py
class TestGraphComparison(unittest.TestCase):
    """
    Test the compare_graphs function.

    This test case loads graphs from GML and JSON formats and uses the
    compare_graphs function to verify that the graphs have the same
    nodes and edges.

    Test is on files that are generate in the same run, we use this test
    to check if the graphs are the same and the code generating them is working.
    """

    def setUp(self):
        """
        Load graphs for testing.

        This method loads graphs from GML and JSON files located in the
        data/output directory, preparing them for comparison tests.
        """
        self.graph_gml = load_graph_from_gml(Path("data/output/drug_mentions_graph.gml"))
        self.graph_json = load_graph_from_json(Path("data/output/drug_mentions_graph.json"))

    def test_compare_graphs_same(self):
        """
        Test the compare_graphs function when graphs are the same.

        This test checks that the compare_graphs function correctly identifies
        that two identical graphs have the same nodes and edges.
        """
        result = compare_graphs(self.graph_gml, self.graph_json)
        self.assertTrue(result["same_nodes"])
        self.assertTrue(result["same_edges"])
        self.assertFalse(result["missing_nodes"])
        self.assertFalse(result["extra_nodes"])
        self.assertFalse(result["missing_edges"])
        self.assertFalse(result["extra_edges"])


if __name__ == "__main__":
    unittest.main()
