# External imports
from pathlib import Path
from typing import Any, Dict, List, Optional

import networkx as nx
import pandas as pd
from loguru import logger

from src.models import Drug, Publication

# Internal imports
from src.pipeline.extractors import ClinicalTrialExtractor, DrugExtractor, PublicationExtractor
from src.pipeline.transformers import DrugMentionGraphTransformer
from src.utils import save_graph_to_json, visualize_graph


# Task 1: Extract drug data
def extract_drugs(drug_path: Path = Path("data/input/drugs.csv")) -> List[Drug]:
    """
    Extract drug data from CSV file.

    Args:
        drug_path: Path to the drugs CSV file

    Returns:
        List of Drug models
    """
    logger.info(f"Extracting drug data from {drug_path}")
    drug_extractor = DrugExtractor(drug_path)
    return drug_extractor.extract()


# Task 2: Extract PubMed data from CSV
def extract_pubmed_csv(pubmed_csv_path: Path = Path("data/input/pubmed.csv")) -> pd.DataFrame:
    """
    Extract PubMed data from CSV file.

    Args:
        pubmed_csv_path: Path to the PubMed CSV file

    Returns:
        DataFrame containing PubMed data from CSV
    """
    logger.info(f"Extracting PubMed data from CSV: {pubmed_csv_path}")
    pubmed_csv_extractor = PublicationExtractor(pubmed_csv_path)
    return pubmed_csv_extractor.extract("csv")


# Task 3: Extract PubMed data from JSON
def extract_pubmed_json(pubmed_json_path: Path = Path("data/input/pubmed.json")) -> pd.DataFrame:
    """
    Extract PubMed data from JSON file.

    Args:
        pubmed_json_path: Path to the PubMed JSON file

    Returns:
        DataFrame containing PubMed data from JSON
    """
    logger.info(f"Extracting PubMed data from JSON: {pubmed_json_path}")
    pubmed_json_extractor = PublicationExtractor(pubmed_json_path)
    return pubmed_json_extractor.extract("json")


# Task 4: Extract clinical trials data
def extract_clinical_trials(
    clinical_trials_path: Path = Path("data/input/clinical_trials.csv"),
) -> pd.DataFrame:
    """
    Extract clinical trials data from CSV file.

    Args:
        clinical_trials_path: Path to the clinical trials CSV file

    Returns:
        DataFrame containing clinical trials data
    """
    logger.info(f"Extracting clinical trials data from {clinical_trials_path}")
    clinical_trials_extractor = ClinicalTrialExtractor(clinical_trials_path)
    return clinical_trials_extractor.extract()


# Task 5: Combine PubMed data from different sources
def combine_pubmed_data(
    pubmed_csv_list: List[Publication], pubmed_json_list: List[Publication]
) -> List[Publication]:
    """
    Combine PubMed data from different sources.

    Args:
        pubmed_csv_list: List of Publication models from CSV
        pubmed_json_list: List of Publication models from JSON

    Returns:
        Combined list of Publication models
    """
    logger.info("Combining PubMed data from CSV and JSON sources")
    return pubmed_csv_list + pubmed_json_list


# Task 6: Build drug mention graph
def build_drug_mention_graph(
    drugs: List[Drug],
    pubmed_publications: List[Publication],
    clinical_trials_publications: List[Publication],
) -> nx.DiGraph:
    """
    Build a graph of drug mentions in publications.

    Args:
        drugs: List of Drug models
        pubmed_publications: List of Publication models from PubMed
        clinical_trials_publications: List of Publication models from clinical trials

    Returns:
        NetworkX DiGraph representing drug mentions
    """
    logger.info("Building drug mention graph")
    transformer = DrugMentionGraphTransformer()
    return transformer.build_graph(
        drugs=drugs,
        pubmed_publications=pubmed_publications,
        clinical_trials_publications=clinical_trials_publications,
    )


# Task 7: Save graph to JSON
def save_graph_json(
    graph: nx.DiGraph, output_path: Path = Path("data/output/drug_mentions_graph.json")
) -> Path:
    """
    Save the drug mention graph to JSON format.

    Args:
        graph: NetworkX DiGraph to save
        output_path: Path where to save the JSON file

    Returns:
        Path to the saved JSON file
    """
    logger.info(f"Saving graph to JSON: {output_path}")
    save_graph_to_json(graph, output_path)
    return output_path


# Task 8: Save graph to GML
def save_graph_gml(
    graph: nx.DiGraph, output_path: Path = Path("data/output/drug_mentions_graph.gml")
) -> Path:
    """
    Save the drug mention graph to GML format.

    Args:
        graph: NetworkX DiGraph to save
        output_path: Path where to save the GML file

    Returns:
        Path to the saved GML file
    """
    logger.info(f"Saving graph to GML: {output_path}")
    nx.write_gml(graph, output_path)
    return output_path


def validate_drug_data(drug_data):
    try:
        drug = Drug(atccode=drug_data["atccode"], name=drug_data["drug"])
        return drug
    except Exception as e:
        logger.error(f"Invalid drug data: {e}")
        return None


def run_pipeline(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute the main data pipeline as a chain of tasks.

    This function orchestrates the execution of all pipeline tasks in sequence.
    Each task depends on the output of previous tasks, forming a directed acyclic graph (DAG).

    Args:
        config: Optional configuration dictionary with custom file paths

    Returns:
        Dictionary containing the outputs of each task
    """
    try:
        # Initialize paths from config or use defaults
        paths = {
            "drugs": Path("data/input/drugs.csv"),
            "pubmed_csv": Path("data/input/pubmed.csv"),
            "pubmed_json": Path("data/input/pubmed.json"),
            "clinical_trials": Path("data/input/clinical_trials.csv"),
            "graph_json": Path("data/output/drug_mentions_graph.json"),
            "graph_gml": Path("data/output/drug_mentions_graph.gml"),
        }

        if config:
            # Override default paths with config values if provided
            for key, value in config.items():
                if key in paths and value:
                    paths[key] = Path(value)

        # Execute pipeline tasks in sequence
        logger.info("Starting drug mentions pipeline")

        # Task 1: Extract drug data
        drugs_list = extract_drugs(paths["drugs"])

        # Task 2-4: Extract publication data in parallel
        pubmed_csv_list = extract_pubmed_csv(paths["pubmed_csv"])
        pubmed_json_list = extract_pubmed_json(paths["pubmed_json"])
        clinical_trials_list = extract_clinical_trials(paths["clinical_trials"])

        # Task 5: Combine PubMed data
        pubmed_list = combine_pubmed_data(pubmed_csv_list, pubmed_json_list)

        # Task 6: Build drug mention graph
        graph = build_drug_mention_graph(drugs_list, pubmed_list, clinical_trials_list)

        # Visualize graph
        visualize_graph(graph, store=False)

        # Task 7-8: Save graph in different formats
        json_path = save_graph_json(graph, paths["graph_json"])
        gml_path = save_graph_gml(graph, paths["graph_gml"])

        logger.info("Pipeline completed successfully")

        # Return the outputs of each task
        return {
            "drugs": drugs_list,
            "pubmed": pubmed_list,
            "clinical_trials": clinical_trials_list,
            "graph": graph,
            "json_path": json_path,
            "gml_path": gml_path,
        }

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise


if __name__ == "__main__":
    run_pipeline()
