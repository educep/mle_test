# External imports
from pathlib import Path

from loguru import logger

# Internal imports
from src.utils import find_journal_with_most_drugs, find_journals_with_most_mentions_of_drug

if __name__ == "__main__":
    """
    Ad-hoc analysis script for drug-journal relationship analysis.

    This script demonstrates how to use the utility functions to analyze
    relationships between drugs and journals in the drug mentions graph.
    It performs two main analyses:

    1. Finding journals with the most mentions of a specific drug
    2. Finding the journal that mentions the highest number of different drugs

    The results are logged using the loguru logger for easy visualization.
    """

    # Define the path to the drug mentions graph JSON file
    # This file contains the network representation of drug-journal relationships
    graph_path = Path("data/output/drug_mentions_graph.json")

    # Analysis 1: Find journals with the most mentions of a specific drug
    # -----------------------------------------------------------------
    # Specify the drug name to analyze
    drug_name = "epinephrine"

    # Call the utility function to find journals with most mentions of this drug
    # The function returns a tuple containing:
    # - A list of journal names (alphabetically sorted if multiple have the same count)
    # - The number of mentions in these journals
    journals, nb_mentions = find_journals_with_most_mentions_of_drug(graph_path, drug_name)

    # Log the results for documentation
    logger.info(f"Journals with most mentions of {drug_name}: {journals} ({nb_mentions} mentions)")

    # Analysis 2: Find the journal that mentions the most different drugs
    # -----------------------------------------------------------------
    # Call the utility function to find the journal with the most drug mentions
    # The function returns a tuple containing:
    # - A list of journal names (alphabetically sorted if multiple have the same count)
    # - The number of different drugs mentioned in these journals
    journals_with_most_drugs, drug_count = find_journal_with_most_drugs(graph_path)

    # Log the results for documentation
    if len(journals_with_most_drugs) == 1:
        logger.info(
            f"Journal with most drug mentions: {journals_with_most_drugs[0]} ({drug_count} drugs)"
        )
    else:
        journal_list = ", ".join(journals_with_most_drugs)
        logger.info(
            f"Journals with most drug mentions: {journal_list} (each with {drug_count} drugs)"
        )
