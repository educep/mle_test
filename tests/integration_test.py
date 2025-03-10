"""
This module contains integration tests for the pharmaceutical data pipeline.

The tests are designed to verify the correct extraction and processing of
publication data from JSON files, ensuring that the data matches expected
results defined using the Publication model.

Classes:
    TestIntegrationWithSampleData: A unittest.TestCase subclass that tests
    the integration of sample data extraction and validation.

Usage:
    Run this module with unittest to execute the integration tests.
    Example:
        python -m unittest tests/test_integration.py
"""


# External imports
import unittest
from pathlib import Path

from loguru import logger

# Internal imports
from src.models.schemas import Publication, PublicationType
from src.pipeline.extractors import PublicationExtractor

# import sys
# sys.path.append(Path(__file__).resolve().parent)


# python -m unittest tests/integration_test.py
class TestIntegrationWithSampleData(unittest.TestCase):
    """
    A test case for verifying the integration of sample data extraction.

    This test case uses the PublicationExtractor to load and validate
    publication data from a JSON file, comparing the results against
    expected Publication instances.
    """

    def test_integration_with_sample_data(self):
        """
        Test the extraction and validation of publication data from a JSON file.

        This test loads sample publication data using the PublicationExtractor,
        logs the extracted publications, and asserts that the extracted data
        matches the expected results defined using the Publication model.
        """
        # Load the sample data
        path_to_json = Path(__file__).resolve().parent / "data" / "pubmed_sample.json"
        logger.info(f"Extracting PubMed data from JSON: {path_to_json}")
        pubmed_json_extractor = PublicationExtractor(path_to_json)
        sample_data = pubmed_json_extractor.extract("json")
        for pub in sample_data:
            logger.info(f"Publication: {pub}")

        # Define expected results using the Publication model
        expected_results = [
            Publication(
                id="10",
                title="Clinical implications of umbilical artery Doppler changes after betamethasone administration",
                date="2020-01-01",
                journal_name="The journal of maternal-fetal & neonatal medicine",
                source_type=PublicationType.PUBMED,
            ),
            Publication(
                id="11",
                title="Effects of Topical Application of Betamethasone on Imiquimod-induced Psoriasis-like Skin Inflammation in Mice.",
                date="2020-01-01",
                journal_name="Journal of back and musculoskeletal rehabilitation",
                source_type=PublicationType.PUBMED,
            ),
            # Add more expected results as needed
        ]

        # Perform the integration test
        for expected in expected_results:
            self.assertIn(expected, sample_data)


if __name__ == "__main__":
    unittest.main()
