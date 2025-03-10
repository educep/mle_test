# External imports
from typing import List

import networkx as nx
import pandas as pd
from loguru import logger

# Internal imports
from src.models import Drug, Journal, Publication, PublicationType


class DrugMentionGraphTransformer:
    """
    Transformer for building a graph of drug mentions in publications using NetworkX.

    This transformer creates a directed graph where:
    - Nodes are drugs, publications (PubMed/clinical trials), and journals
    - Edges represent relationships between nodes with attributes like date_mention

    Attributes:
        graph (nx.DiGraph): The directed graph representing drug mentions.
    """

    def __init__(self) -> None:
        """
        Initialize the transformer with an empty graph.

        This constructor sets up an empty directed graph using NetworkX, ready to
        be populated with nodes and edges representing drug mentions.
        """
        self.graph = nx.DiGraph()

    def build_graph(
        self,
        drugs: List[Drug],
        pubmed_publications: List[Publication],
        clinical_trials_publications: List[Publication],
    ) -> nx.DiGraph:
        """
        Build a directed graph representing drug mentions in publications.

        This method processes data from drugs, PubMed publications, and clinical
        trials to construct a graph where nodes represent entities and edges
        represent relationships between them.

        Args:
            drugs (List[Drug]): List of Drug objects.
            pubmed_publications (List[Publication]): List of Publication objects from PubMed.
            clinical_trials_publications (List[Publication]): List of Publication objects from clinical trials.

        Returns:
            nx.DiGraph: Directed graph of drug mentions.

        Raises:
            Exception: If an error occurs during graph construction.
        """
        try:
            # Combine all publications
            all_publications = pubmed_publications + clinical_trials_publications

            # For readability: Extract journals from publications
            journals = self._extract_journals(all_publications)

            # Add all nodes to the graph
            self._add_nodes_to_graph(drugs, all_publications, journals)

            # Connect drugs to publications and journals
            self._connect_drugs_to_publications(drugs, all_publications)

            logger.info(
                f"Graph built successfully with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges"
            )

            return self.graph

        except Exception as e:
            logger.error(f"Error building graph: {str(e)}")
            raise

    def _process_drugs(self, drugs_df: pd.DataFrame) -> List[Drug]:
        """
        Process drug data and create Drug objects.

        This method iterates over a DataFrame of drug data, creating Drug
        objects for each entry, which are then used as nodes in the graph.

        Args:
            drugs_df (pd.DataFrame): DataFrame containing drug data.

        Returns:
            List[Drug]: List of Drug objects.
        """
        drugs = []
        for _, row in drugs_df.iterrows():
            drug = Drug(
                atccode=row["atccode"],  # we will use this attribute in __eq__ and __hash__
                name=row["drug"].strip(),
            )
            drugs.append(drug)

        logger.info(f"Processed {len(drugs)} drugs")
        return drugs

    def _process_publications(
        self, df: pd.DataFrame, source_type: PublicationType, title_column: str
    ) -> List[Publication]:
        """
        Process publication data and create Publication objects.

        This method iterates over a DataFrame of publication data, creating
        Publication objects for each entry, which are then used as nodes in
        the graph.

        Args:
            df (pd.DataFrame): DataFrame containing publication data.
            source_type (PublicationType): Type of the publication (PubMed or clinical trial).
            title_column (str): Column name for the publication title.

        Returns:
            List[Publication]: List of Publication objects.
        """
        publications = []

        for _, row in df.iterrows():
            # Skip rows with empty IDs or titles
            if (
                pd.isna(row["id"])
                or row["id"] == ""
                or pd.isna(row[title_column])
                or row[title_column] == ""
            ):
                continue

            publication = Publication(
                id=str(row["id"]),
                title=row[title_column].strip(),
                date=str(row["date"]),
                journal_name=row["journal"].strip(),
                source_type=source_type,
            )
            publications.append(publication)

        logger.info(f"Processed {len(publications)} {source_type} publications")
        return publications

    def _extract_journals(self, publications: List[Publication]) -> List[Journal]:
        """
        Extract unique journals from publications.

        This method identifies unique journal names from a list of publications
        and creates Journal objects for each unique name.

        Args:
            publications (List[Publication]): List of Publication objects.

        Returns:
            List[Journal]: List of unique Journal objects.
        """
        journal_set = set()

        for pub in publications:
            if pub.journal_name and pub.journal_name.strip():
                journal_set.add(pub.journal_name)

        journals = [Journal(name=name) for name in journal_set]
        logger.info(f"Extracted {len(journals)} unique journals")
        return journals

    def _add_nodes_to_graph(
        self, drugs: List[Drug], publications: List[Publication], journals: List[Journal]
    ) -> None:
        """
        Add all nodes to the graph with appropriate attributes.

        This method adds Drug, Publication, and Journal nodes to the graph,
        setting relevant attributes for each node type.

        Args:
            drugs (List[Drug]): List of Drug objects.
            publications (List[Publication]): List of Publication objects.
            journals (List[Journal]): List of Journal objects.
        """
        # Add drug nodes
        for drug in drugs:
            self.graph.add_node(
                drug.name.lower(),  # Use lowercase name as node ID
                type="drug",
                atccode=drug.atccode,  # Store atccode as attribute
            )

        # Add publication nodes - use truncated title as ID
        for pub in publications:
            pub_id = pub.title[:20].lower()  # Truncate title to 20 chars for node ID
            self.graph.add_node(
                pub_id,
                type=pub.source_type,
                id=pub.id,  # Store original ID as attribute
                title=pub.title,  # Store full title as attribute
                date=str(pub.date),
                journal_name=pub.journal_name,
            )

        # Add journal nodes - use truncated name as ID
        for journal in journals:
            journal_id = journal.name[:20]
            self.graph.add_node(
                journal_id, type="journal", name=journal.name  # Store full name as attribute
            )

    def _connect_drugs_to_publications(
        self, drugs: List[Drug], publications: List[Publication]
    ) -> None:
        """
        Connect drugs to publications and journals based on mentions.

        This method creates edges between Drug nodes and Publication/Journal
        nodes in the graph, based on the presence of drug names in publication
        titles and journal names.

        Args:
            drugs (List[Drug]): List of Drug objects.
            publications (List[Publication]): List of Publication objects.
        """
        # Track which journals have been connected to which drugs
        drug_journal_connections = set()

        for drug in drugs:
            drug_id = drug.name.lower()

            for pub in publications:
                # Check if drug is mentioned in publication title
                if drug.name.lower() in pub.title.lower():
                    # This is a naive approach, we should use a more sophisticated approach
                    # to connect drugs to publications, example:
                    # 'Amphetamine' in 'Dextroamphetamine' would give True
                    # Connect drug to publication - use truncated title consistently
                    pub_id = pub.title[:20].lower()
                    self.graph.add_edge(
                        drug_id,
                        pub_id,
                        relationship="Référencé dans",
                        date_mention=pub.date,
                    )

                    # Connect drug to journal (if not already connected)
                    journal_id = pub.journal_name[:20]
                    connection_key = (drug_id, journal_id)

                    if connection_key not in drug_journal_connections:
                        self.graph.add_edge(
                            drug_id,
                            journal_id,
                            relationship="Référencé dans",
                            date_mention=pub.date,
                        )
                        drug_journal_connections.add(connection_key)
