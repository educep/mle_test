# External imports
import json
from pathlib import Path
from typing import Any, Dict, Set

import networkx as nx
import plotly.graph_objects as go
from loguru import logger

# Internal imports
from src.models import Drug, Journal, Publication, PublicationType


def load_graph_from_gml(gml_path: Path) -> nx.DiGraph:
    """
    Load a NetworkX graph from a GML file.

    Args:
        gml_path: Path to the GML file

    Returns:
        nx.DiGraph: Loaded graph
    """
    try:
        # Load graph from GML file
        graph = nx.read_gml(gml_path)

        logger.info(
            f"Graph loaded from GML with {len(graph.nodes)} nodes and {len(graph.edges)} edges"
        )
        return graph

    except Exception as e:
        logger.error(f"Error loading graph from GML: {str(e)}")
        raise


def load_graph_from_json(json_path: Path) -> nx.DiGraph:
    """
    Load a NetworkX graph from a JSON file.

    This function reconstructs a directed graph from a JSON file, recreating all nodes
    and edges with their attributes. It supports various node types, including drugs,
    publications, and journals, and establishes relationships between them.

    Args:
        json_path (Path): Path to the JSON file containing the graph data.

    Returns:
        nx.DiGraph: A reconstructed NetworkX directed graph with nodes and edges.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        Exception: For errors during graph reconstruction.
    """
    try:
        # Check if file exists
        if not json_path.exists():
            raise FileNotFoundError(f"Graph file not found: {json_path}")

        # Load JSON data
        with open(json_path) as f:
            graph_data = json.load(f)

        # Create new directed graph
        graph = nx.DiGraph()

        # Add drug nodes
        for drug in graph_data.get("drugs", []):
            # Use drug name as node ID
            graph.add_node(
                drug.get("name").lower(),
                type="drug",
                atccode=drug.get("atccode"),  # Store atccode as attribute
                # name=drug.get("name"),
            )

        # Add pubmed nodes
        for pubmed in graph_data.get("publications", {}).get("pubmed", []):
            # Use truncated title as node ID
            title = pubmed.get("title", "")
            pub_id = title[:20].lower()
            graph.add_node(
                pub_id,
                type="pubmed",
                id=pubmed.get("id"),  # Store original ID as attribute
                title=title,
                date=pubmed.get("date"),
                journal_name=pubmed.get("journal_name"),
            )

        # Add clinical trial nodes
        for trial in graph_data.get("publications", {}).get("clinical_trials", []):
            # Use truncated title as node ID
            title = trial.get("title", "")
            pub_id = title[:20].lower()
            graph.add_node(
                pub_id,
                type="clinical_trial",
                id=trial.get("id"),  # Store original ID as attribute
                title=title,
                date=trial.get("date"),
                journal_name=trial.get("journal_name"),
            )

        # Add journal nodes
        for journal in graph_data.get("journals", []):
            # Use truncated name as node ID
            journal_name = journal.get("name")
            journal_id = journal_name[:20]
            graph.add_node(
                journal_id, type="journal", name=journal_name  # Store full name as attribute
            )

        # Add relationships (edges)
        for rel in graph_data.get("relationships", []):
            # Get source and target information
            source_info = rel.get("source", {})
            target_info = rel.get("target", {})

            source_id = source_info.get("id")
            source_type = source_info.get("type")
            target_id = target_info.get("id")
            target_type = target_info.get("type")

            # Map IDs to node IDs in the graph
            if source_type == "drug":
                # Find drug node by atccode
                source_node = None
                for node, attrs in graph.nodes(data=True):
                    if attrs.get("type") == "drug" and attrs.get("atccode") == source_id:
                        source_node = node
                        break
            else:
                source_node = source_id[:20].lower() if source_id else None

            if target_type in ["pubmed", "clinical_trial"]:
                # Find publication node by ID
                target_node = None
                for node, attrs in graph.nodes(data=True):
                    if attrs.get("type") == target_type and attrs.get("id") == target_id:
                        target_node = node
                        break
            elif target_type == "journal":
                # Use truncated journal name
                target_node = target_id[:20] if target_id else None
            else:
                target_node = target_id

            # Add edge if both nodes exist
            if (
                source_node
                and target_node
                and graph.has_node(source_node)
                and graph.has_node(target_node)
            ):
                graph.add_edge(
                    source_node,
                    target_node,
                    relationship=rel.get("type"),
                    date_mention=rel.get("date_mention"),
                )

        logger.info(
            f"Graph loaded from JSON with {len(graph.nodes)} nodes and {len(graph.edges)} edges"
        )
        return graph

    except Exception as e:
        logger.error(f"Error loading graph from JSON: {str(e)}")
        raise


def find_journal_with_most_drugs(graph_path: Path) -> tuple[list[str], int]:
    """
    Find the journal(s) that mention the highest number of different drugs.

    This function analyzes a drug mentions graph to identify journals that
    reference the most distinct drugs. It returns a list of such journals,
    sorted alphabetically if there are ties, along with the count of drugs.

    Args:
        graph_path (Path): Path to the drug mentions graph JSON file.

    Returns:
        tuple: (list_of_journal_names, number_of_drugs)
               The list of journal names is alphabetically sorted if multiple
               journals have the same count.

    Raises:
        Exception: For errors during graph analysis.
    """
    try:
        # Load the graph
        graph = load_graph_from_json(graph_path)

        # Create a dictionary to count drugs per journal
        journal_drug_counts: Dict[str, Set[str]] = {}

        # Iterate through all edges
        for source, target, _ in graph.edges(data=True):
            source_type = graph.nodes[source].get("type")
            target_type = graph.nodes[target].get("type")

            # Check if this is a drug-journal relationship
            if source_type == "drug" and target_type == "journal":
                # Get the full journal name from the node attributes
                journal_name = graph.nodes[target].get("name")
                drug_atccode = graph.nodes[source].get("atccode")

                if journal_name not in journal_drug_counts:
                    journal_drug_counts[journal_name] = set()

                journal_drug_counts[journal_name].add(drug_atccode)

        # Find journal with most drugs
        if not journal_drug_counts:
            return (["No journals found"], 0)

        # Find the maximum number of drugs
        max_drug_count = max(len(drugs) for drugs in journal_drug_counts.values())

        # Get all journals with the maximum number of drugs
        top_journals = [
            journal
            for journal, drugs in journal_drug_counts.items()
            if len(drugs) == max_drug_count
        ]

        # Sort alphabetically
        top_journals.sort()

        return (top_journals, max_drug_count)

    except Exception as e:
        logger.error(f"Error finding journal with most drugs: {str(e)}")
        # Return a default value in case of error
        return (["Error processing journals"], 0)


def find_journals_with_most_mentions_of_drug(
    graph_path: Path, drug_name: str
) -> tuple[list[str], int]:
    """
    Find the journal(s) that mention a specific drug the most times.

    This function analyzes a drug mentions graph to identify journals that
    frequently mention a specified drug. It returns a list of such journals,
    sorted alphabetically if there are ties, along with the count of mentions.

    Args:
        graph_path (Path): Path to the drug mentions graph JSON file.
        drug_name (str): Name of the drug to search for.

    Returns:
        tuple: (list_of_journal_names, number_of_mentions)
               The list of journal names is alphabetically sorted if multiple
               journals have the same count.

    Raises:
        Exception: For errors during graph analysis.
    """
    try:
        # Load the graph
        graph = load_graph_from_json(graph_path)

        # Dictionary to count mentions of the specific drug per journal
        journal_mentions = {}

        # Find the drug node(s) with the specified name
        drug_nodes = []
        for node, attrs in graph.nodes(data=True):
            if attrs.get("type") == "drug" and node == drug_name:
                drug_nodes.append(node)

        if not drug_nodes:
            logger.warning(f"No drug found with name: {drug_name}")
            return (["No journals found"], 0)

        # For each drug node, count mentions in journals
        for drug_node in drug_nodes:
            # Get all edges from this drug node
            for _, target in graph.out_edges(drug_node):
                target_type = graph.nodes[target].get("type")

                # Check if the target is a journal
                if target_type == "journal":
                    journal_name = graph.nodes[target].get("name")

                    if journal_name not in journal_mentions:
                        journal_mentions[journal_name] = 1

                    journal_mentions[journal_name] += 1

        # If no journals mention this drug
        if not journal_mentions:
            return (["No journals found"], 0)

        # Find the maximum number of mentions
        max_mentions = max(journal_mentions.values())

        # Get all journals with the maximum number of mentions
        top_journals = [
            journal for journal, mentions in journal_mentions.items() if mentions == max_mentions
        ]

        # Sort alphabetically
        top_journals.sort()

        return (top_journals, max_mentions)

    except Exception as e:
        logger.error(f"Error finding journals with most mentions of drug {drug_name}: {str(e)}")
        return (["Error processing journals"], 0)


def visualize_graph(graph: nx.DiGraph, store: bool = False) -> None:
    """
    Visualize a code dependency graph interactively using Plotly.

    This function creates an interactive visualization of a NetworkX graph,
    assigning colors to nodes based on their type and displaying the graph
    using a force-directed layout.

    Args:
        graph (networkx.Graph): The dependency graph to visualize.
    """

    # Build new labels by removing the root folder from node names
    new_labels = {}
    for node in graph.nodes:
        label = str(node)
        new_labels[node] = label

    # Assign colors based on node type
    node_colors = []
    color_map = {
        "pubmed": "lightblue",
        "drug": "lightgreen",
        "clinical_trial": "orange",
        "journal": "violet",
        "unknown": "gray",
    }

    for node in graph.nodes:
        node_type = graph.nodes[node].get("type", "unknown")
        node_colors.append(color_map.get(node_type, "gray"))

    # Generate node positions using force-directed layout
    pos = nx.spring_layout(graph, seed=42)

    # Create edge traces
    edge_traces = []
    for edge in graph.edges:
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line={"width": 1, "color": "gray"},
            mode="lines",
            hoverinfo="none",
        )
        edge_traces.append(edge_trace)

    # Create node trace
    node_x, node_y, node_text, node_hover = [], [], [], []
    for node in graph.nodes:
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(new_labels[node])
        node_hover.append(f"Type: {graph.nodes[node].get('type', 'unknown')}")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        marker={
            "size": 15,
            "color": node_colors,
            "opacity": 0.8,
            "line": {"width": 2, "color": "black"},
        },
        text=node_text,
        hovertext=node_hover,
        hoverinfo="text",
        textposition="top center",
    )

    # Create interactive figure
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        title="Drug Mentions Graph",
        showlegend=False,
        hovermode="closest",
        margin={"b": 0, "l": 0, "r": 0, "t": 40},
        xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
        yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
    )

    fig.show()
    if store:
        path_ = Path(__file__).parent.parent.parent / "data" / "charts"
        # Save the figure as an HTML file
        fig.write_html(path_ / "graph.html")
        fig.write_image(path_ / "graph.png")

    return


def save_graph_to_json(graph: nx.DiGraph, output_path: Path) -> None:
    """
    Save a NetworkX graph to a JSON file in a structured format.

    Args:
        graph (nx.DiGraph): The NetworkX directed graph to save.
        output_path (Path): The file path where the JSON will be saved.
    """
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize lists to store graph components
    drugs: list[Dict[str, str]] = []  # List to store drug nodes
    pubmeds: list[Dict[str, str]] = []  # List to store pubmed publication nodes
    clinical_trials: list[Dict[str, str]] = []  # List to store clinical trial nodes
    journals: list[Dict[str, str]] = []  # List to store journal nodes
    relationships: list[Dict[str, str]] = []  # List to store relationships (edges)

    # Process nodes
    for node, attrs in graph.nodes(data=True):
        node_type = attrs.get("type")  # Determine the type of node

        if node_type == "drug":
            # Create a Drug object and append its dictionary representation
            drug = Drug(atccode=attrs.get("atccode", ""), name=node)
            drugs.append(drug.model_dump())

        elif node_type in ["pubmed", "clinical_trial"]:
            # Create a Publication object and append its dictionary representation
            publication = Publication(
                id=attrs.get("id"),
                title=attrs.get("title"),
                date=attrs.get("date"),
                journal_name=attrs.get("journal_name"),
                source_type=PublicationType.PUBMED
                if node_type == "pubmed"
                else PublicationType.CLINICAL_TRIAL,
            )
            if node_type == "pubmed":
                pubmeds.append(publication.model_dump())
            else:
                clinical_trials.append(publication.model_dump())

        elif node_type == "journal":
            # Create a Journal object and append its dictionary representation
            journal = Journal(name=attrs.get("name"))
            journals.append(journal.model_dump())

    # Process edges (relationships)
    for source, target, attrs in graph.edges(data=True):
        # Get node types to determine relationship type
        source_type = graph.nodes[source].get("type")
        target_type = graph.nodes[target].get("type")

        # Get proper IDs for JSON representation
        if source_type == "drug":
            source_id = graph.nodes[source].get("atccode")
        else:
            source_id = source

        if target_type in ["pubmed", "clinical_trial"]:
            target_id = graph.nodes[target].get("id")
        elif target_type == "journal":
            target_id = graph.nodes[target].get("name")
        else:
            target_id = target

        # Create a relationship dictionary and append it
        relationship = {
            "source": {"id": source_id, "type": source_type},
            "target": {"id": target_id, "type": target_type},
            "type": attrs.get("relationship"),
            "date_mention": attrs.get("date_mention"),
        }
        relationships.append(relationship)

    # Convert graph to dictionary representation
    graph_data: Dict[str, Any] = {
        "drugs": drugs,
        "publications": {"pubmed": pubmeds, "clinical_trials": clinical_trials},
        "journals": journals,
        "relationships": relationships,
    }

    # Save to JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2)

    logger.info(f"Graph saved to JSON: {output_path}")
