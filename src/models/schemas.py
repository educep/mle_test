"""
# Graph Representation: Drug Mentions in Publications and Trials
This information was retrieved from documentation.

## Nodes:
- **Drug** (Central Node)
- **Pubmed** (Publication Source)
- **Clinical trials** (Clinical Research)
- **Journal** (Publication Source)

## Edges:
- **drug → pubmed**
  - Label: `Référencé dans`
  - Attribute: `date_mention`

- **drug → journal**
  - Label: `Référencé dans`
  - Attribute: `date_mention`

- **drug → Clinical trials**
  - Label: `Référencé dans`
  - Attribute: `date_mention`

## Description:
The central entity in this graph is **"drug"**, which is referenced in three different sources:
1. **PubMed**, a database of scientific publications.
2. **Journals**, which publish research papers.
3. **Clinical trials**, where the drug has been studied.

Each connection between the **drug** and the sources includes:
- A **"Référencé dans"** (Referenced in) label.
- A **"date_mention"** attribute, indicating when the drug was mentioned in that source.

This structure allows tracking where and when a drug has been mentioned across different scientific and clinical research sources.
"""

# External imports
from enum import Enum
from typing import Any

from pydantic import BaseModel


class PublicationType(str, Enum):
    """
    Enum for publication types.

    This enumeration defines the types of publications that can be represented
    in the graph, distinguishing between PubMed articles and clinical trials.
    """

    PUBMED = "pubmed"
    CLINICAL_TRIAL = "clinical_trial"


class Drug(BaseModel):
    """
    Model representing a drug node in our graph.

    This model captures the essential information about pharmaceutical drugs
    from the drugs.csv file, including their unique identifier and name.

    Attributes:
        atccode (str): The ATC (Anatomical Therapeutic Chemical) classification code.
        name (str): The name of the drug.
    """

    atccode: str  # Drug identifier
    name: str  # Drug name

    def __hash__(self) -> int:
        """
        Enable using Drug objects in sets by hashing on atccode.

        Returns:
            int: The hash value of the drug's ATC code.
        """
        return hash(self.atccode)

    def __eq__(self, other: Any) -> bool:
        """
        Define equality for Drug objects based on their atccode.

        Args:
            other (Drug): Another Drug object to compare.

        Returns:
            bool: True if both Drug objects have the same ATC code, False otherwise.
        """
        if not isinstance(other, Drug):
            return False
        return self.atccode == other.atccode


class Publication(BaseModel):
    """
    Model representing a publication (PubMed article or clinical trial).

    This model captures data from both PubMed articles and clinical trials,
    with a source_type field to distinguish between them.

    Attributes:
        id (str): Unique identifier for the publication.
        title (str): Title of the publication.
        date (str): Date of the publication.
        journal_name (str): Name of the journal where the publication appeared.
        source_type (PublicationType): Type of the publication (PubMed or clinical trial).
    """

    id: str
    title: str
    date: str
    journal_name: str
    source_type: PublicationType

    def __hash__(self) -> int:
        """
        Enable using Publication objects in sets and as dict keys.

        Returns:
            int: The hash value based on the publication's ID and source type.
        """
        return hash((self.id, self.source_type))

    def __eq__(self, other: Any) -> bool:
        """
        Enable comparison between Publication objects.

        Args:
            other (Publication): Another Publication object to compare.

        Returns:
            bool: True if both Publication objects have the same ID and source type, False otherwise.
        """
        if not isinstance(other, Publication):
            return False
        is_equal = (
            self.id == other.id
            and self.source_type == other.source_type
            and self.date == other.date
            and self.title == other.title
            and self.journal_name == other.journal_name
        )
        return is_equal


class Journal(BaseModel):
    """
    Model representing a journal that publishes articles.

    This model captures the essential information about journals, specifically
    their names, which are used as unique identifiers in the graph.

    Attributes:
        name (str): The name of the journal.
    """

    name: str

    def __hash__(self) -> int:
        """
        Enable using Journal objects in sets and as dict keys.

        Returns:
            int: The hash value of the journal's name.
        """
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        """
        Enable comparison between Journal objects.

        Args:
            other (Journal): Another Journal object to compare.

        Returns:
            bool: True if both Journal objects have the same name, False otherwise.
        """
        if not isinstance(other, Journal):
            return False
        return self.name == other.name
