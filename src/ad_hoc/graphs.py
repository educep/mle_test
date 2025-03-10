# External imports
from pathlib import Path

# Internal import
from src.utils import load_graph_from_gml, load_graph_from_json, visualize_graph

if __name__ == "__main__":
    graph_path = Path("data/output/drug_mentions_graph.gml")
    graph_gml = load_graph_from_gml(graph_path)
    visualize_graph(graph_gml)
    # nx.draw(graph_gml, with_labels=True)
    # import matplotlib.pyplot as plt
    # plt.show()

    graph_path = Path("data/output/drug_mentions_graph.json")
    graph_json = load_graph_from_json(graph_path)
    visualize_graph(graph_json)
