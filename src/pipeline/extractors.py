# External imports
import json
import re
from pathlib import Path
from typing import List, TypedDict, cast

import pandas as pd
from loguru import logger

# Internal imports
from src.models import Drug, Publication, PublicationType


class DataExtractor:
    """
    Base class for data extraction operations in the pharmaceutical data pipeline.

    This class provides common functionality for data extraction tasks, serving as a foundation
    for specialized extractors. It implements basic file validation and error handling that can
    be reused across different types of data extraction.

    Attributes:
        input_path (Path): Path to the input file to be processed.

    Note:
        This implementation assumes that the source data is from a structured database
        and has undergone preliminary cleaning. For raw or unstructured data, additional
        preprocessing steps would be needed.
    """

    def __init__(self, input_path: Path):
        """
        Initialize the DataExtractor with a file path.

        Args:
            input_path (Path): Path to the input file to be processed.
        """
        self.input_path = input_path

    # def extract(self):
    #     """
    #     For documentation purposes only.
    #     This method should be implemented by subclasses including specific
    #     data source checks, including format, encoding, and data quality checks.
    #     Some very basic checks are implemented, but other should be implemented in
    #     subclasses in functions of goals of the specific data source.
    #     For example, the PublicationExtractor has a _clean_publication_data method
    #     that cleans the data and validates the data.
    #     Further verifications can be performed using field_validator
    #     from pydantic in schemas.py.
    #     """
    #     pass

    def validate_file_exists(self) -> bool:
        """
        Validate that the input file exists.

        Returns:
            bool: True if the file exists.

        Raises:
            FileNotFoundError: If the input file does not exist.
        """
        if not self.input_path.exists():
            logger.error(f"File not found: {self.input_path}")
            raise FileNotFoundError(f"File not found: {self.input_path}")
        return True


class DrugExtractor(DataExtractor):
    """
    Specialized extractor for pharmaceutical drug data.

    This class handles the extraction of drug information from CSV files, focusing on
    essential drug attributes like ATC codes and drug names. It inherits basic file
    validation from DataExtractor and adds drug-specific data processing.

    The extractor expects a CSV file with at least two columns:
    - 'atccode': The ATC (Anatomical Therapeutic Chemical) classification code
    - 'drug': The name of the drug
    """

    def extract(self) -> List[Drug]:
        """
        Extract drug data from a CSV file and return as a list of Drug models.

        Returns:
            List[Drug]: A list of Drug model instances.
        """
        self.validate_file_exists()
        try:
            df = pd.read_csv(self.input_path, dtype=str)
            drugs = [
                Drug(atccode=row["atccode"], name=row["drug"].strip()) for _, row in df.iterrows()
            ]
            return drugs
        except Exception as e:
            logger.error(f"Error extracting drug data: {str(e)}")
            raise


class PublicationData(TypedDict):
    id: str
    title: str
    date: str
    journal: str


class PublicationExtractor(DataExtractor):
    """
    Extractor for scientific publication data from multiple sources.

    This class handles the extraction and cleaning of publication data from both CSV
    and JSON sources. It includes robust date parsing, data validation, and cleaning
    operations specific to publication data.

    The extractor expects the following required columns in the input data:
    - 'id': Unique identifier for the publication
    - 'title': Publication title
    - 'date': Publication date (supports multiple date formats)
    - 'journal': Name of the publishing journal

    Note:
        Date parsing supports multiple formats:
        - YYYY-MM-DD
        - DD/MM/YYYY
        - D Month YYYY (e.g., "1 January 2020")
    """

    def extract(self, file_type: str) -> List[Publication]:
        """
        Extract and validate publication data from CSV or JSON sources and return as a list of Publication models.

        Returns:
            List[Publication]: A list of Publication model instances.
        """
        self.validate_file_exists()
        try:
            if file_type == "csv":
                df = pd.read_csv(self.input_path, dtype=str)
            elif file_type == "json":
                data = self._read_json_safely()
                df = pd.DataFrame(data)

            df = self._clean_publication_data(df)
            publications = [
                Publication(
                    id=str(row["id"]),
                    title=row["title"].strip(),
                    date=str(row["date"].date()),
                    journal_name=row["journal"].strip(),
                    source_type=PublicationType.PUBMED,
                )
                for _, row in df.iterrows()
            ]
            return publications
        except Exception as e:
            logger.error(f"Error extracting publication data from {self.input_path}: {str(e)}")
            raise

    def _read_json_safely(self) -> List[PublicationData]:
        """
        Safely read and parse JSON data, handling common formatting issues.

        This method attempts to read JSON data and includes error correction for
        common JSON formatting issues like trailing commas. It provides a robust
        way to handle potentially malformed JSON files.

        Returns:
            List[Dict]: List of dictionaries containing the parsed JSON data

        Raises:
            json.JSONDecodeError: If the JSON cannot be parsed even after fixes
        """
        with open(self.input_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Try parsing as-is first
        try:
            return cast(List[PublicationData], json.loads(content))
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parsing failed: {e}. Attempting fixes...")

        # Apply fixes for common JSON issues
        fixed_content = re.sub(r",(\s*[\]}])", r"\1", content)

        try:
            logger.info("JSON successfully fixed and parsed")
            return cast(List[PublicationData], json.loads(fixed_content))
        except json.JSONDecodeError as e:
            logger.error(f"Could not fix JSON: {e}")
            raise

    def _parse_date(self, date_str: str) -> pd.Timestamp:
        """
        Parse date strings in multiple formats to a standardized timestamp.

        This method attempts to parse dates in various formats, providing flexibility
        in handling different date representations in the input data.

        Args:
            date_str (str): Date string to parse

        Returns:
            pd.Timestamp: Parsed and standardized date

        Raises:
            ValueError: If the date string doesn't match any supported format
        """
        formats = [
            ("%Y-%m-%d", "YYYY-MM-DD"),
            ("%d/%m/%Y", "DD/MM/YYYY"),
            ("%d %B %Y", "D Month YYYY"),
        ]

        for fmt, _ in formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except ValueError:
                continue

        logger.error(f"Date '{date_str}' doesn't match any supported format")
        raise ValueError(f"Unsupported date format for: {date_str}")

    def _clean_publication_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate publication data.

        This method performs several data quality checks and cleaning operations:
        - Validates presence of required columns
        - Removes rows with missing or invalid IDs
        - Standardizes date formats
        - Removes duplicate entries
        - Resets the DataFrame index

        Args:
            df (pd.DataFrame): Raw publication data

        Returns:
            pd.DataFrame: Cleaned and validated publication data

        Raises:
            ValueError: If required columns are missing
        """
        required_columns = ["id", "title", "date", "journal"]

        # Validate required columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Clean and validate data
        df = df[df["id"].notna() & (df["id"] != "")]
        df["id"] = df["id"].astype(str)

        # Parse dates
        try:
            df["date"] = df["date"].apply(self._parse_date)
            logger.info(f"Successfully parsed {len(df)} dates")
        except ValueError as e:
            logger.error(f"Failed to parse some dates: {e}")
            raise

        # Remove duplicates and reset index
        df = df.drop_duplicates(subset=["id"]).reset_index(drop=True)

        logger.info(f"Cleaned publication data: {len(df)} valid records")
        return df


class ClinicalTrialExtractor(DataExtractor):
    """
    Specialized extractor for clinical trials data.

    This class handles the extraction and cleaning of clinical trials data from CSV
    files. It includes specific validation and cleaning operations relevant to
    clinical trial data.

    The extractor expects the following required columns:
    - 'id': Unique identifier for the clinical trial
    - 'scientific_title': Title of the clinical trial
    - 'date': Trial date
    - 'journal': Journal where the trial was published

    Note:
        This extractor includes additional validation for scientific titles and
        journal names, which are critical for clinical trial data quality.
    """

    def extract(self) -> List[Publication]:
        """
        Extract and validate clinical trials data from CSV and return as a list of Publication models.

        Returns:
            List[Publication]: A list of Publication model instances with CLINICAL_TRIAL type.
        """
        self.validate_file_exists()
        try:
            df = pd.read_csv(self.input_path, dtype=str)
            df = self._clean_clinical_trial_data(df)
            clinical_trials = [
                Publication(
                    id=str(row["id"]),
                    title=row["scientific_title"].strip(),
                    date=str(row["date"].date()),
                    journal_name=row["journal"].strip(),
                    source_type=PublicationType.CLINICAL_TRIAL,
                )
                for _, row in df.iterrows()
            ]
            return clinical_trials
        except Exception as e:
            logger.error(f"Error extracting clinical trials data: {str(e)}")
            raise

    def _clean_clinical_trial_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate clinical trials data.

        This method performs comprehensive data cleaning and validation:
        - Validates required columns
        - Removes rows with missing or invalid data
        - Cleans scientific titles and journal names
        - Standardizes date formats
        - Removes duplicates

        Args:
            df (pd.DataFrame): Raw clinical trials data

        Returns:
            pd.DataFrame: Cleaned and validated clinical trials data

        Raises:
            ValueError: If required columns are missing
        """
        required_columns = ["id", "scientific_title", "date", "journal"]

        # Validate columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Clean data
        df = df[
            df["id"].notna()
            & (df["id"] != "")
            & df["scientific_title"].notna()
            & (df["scientific_title"].str.strip() != "")
        ]

        # Clean text fields
        df["scientific_title"] = df["scientific_title"].str.strip()
        df["id"] = df["id"].astype(str)
        df["journal"] = df["journal"].fillna("").str.strip()

        # Remove invalid entries
        df = df[df["journal"] != ""]

        # Parse dates
        try:
            df["date"] = df["date"].apply(self._parse_date)
            logger.info(f"Successfully parsed {len(df)} dates")
        except ValueError as e:
            logger.error(f"Failed to parse some dates: {e}")
            raise

        # Remove duplicates and reset index
        df = df.drop_duplicates(subset=["id"]).reset_index(drop=True)

        logger.info(f"Cleaned clinical trials data: {len(df)} valid records")
        return df

    def _parse_date(self, date_str: str) -> pd.Timestamp:
        """
        Parse date strings in multiple formats to a standardized timestamp.

        Supports multiple date formats commonly found in clinical trial data:
        - YYYY-MM-DD
        - DD/MM/YYYY
        - D Month YYYY

        Args:
            date_str (str): Date string to parse

        Returns:
            pd.Timestamp: Parsed and standardized date

        Raises:
            ValueError: If the date string doesn't match any supported format
        """
        formats = [
            ("%Y-%m-%d", "YYYY-MM-DD"),
            ("%d/%m/%Y", "DD/MM/YYYY"),
            ("%d %B %Y", "D Month YYYY"),
        ]

        for fmt, _ in formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except ValueError:
                continue

        logger.error(f"Date '{date_str}' doesn't match any supported format")
        raise ValueError(f"Unsupported date format for: {date_str}")
