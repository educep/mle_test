"""
This module contains integration tests for SQL queries used in the pharmaceutical data pipeline.

The tests are designed to verify the correctness of SQL queries by comparing
their results against pre-computed expected results stored in CSV files.

Classes:
    TestSQLQueries: A unittest.TestCase subclass that tests the execution
    and validation of SQL queries against expected results.

Usage:
    Run this module with unittest to execute the SQL integration tests.
    Example:
        python -m unittest tests/test_sql.py
"""


import os
import unittest
from pathlib import Path

# External imports
import pandas as pd
import pandas.testing as pdt
from loguru import logger

# Internal imports
from src.sql_test.dblite import execute_query, initialise_db

# import sys
# sys.path.append(Path(__file__).resolve().parent)


# python -m unittest tests/sql_queries_test.py
class TestSQLQueries(unittest.TestCase):
    """
    Integration test for the SQL queries.

    This test case initializes a test database, executes SQL queries,
    and compares the results against pre-computed expected results
    stored in CSV files.
    """

    # Declare class attributes
    test_dir: Path
    sql_dir: Path
    db_path: Path

    @classmethod
    def setUpClass(cls):
        """
        Set up the test database before any tests run.

        This method initializes the database and prepares it for testing
        by creating necessary tables and loading initial data.
        """
        cls.test_dir = Path(__file__).resolve().parent
        cls.sql_dir = cls.test_dir.parent / "src" / "sql_test" / "queries"
        cls.db_path = initialise_db(local_dir=cls.test_dir, from_file=True)
        logger.info("Database initialized for testing.")

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the test database after all tests have run.

        This method removes the database file to ensure no residual data
        affects subsequent test runs.
        """
        if cls.db_path.exists():
            os.remove(cls.db_path)
            logger.info("Database file removed after testing.")

    def test_revenue_query(self):
        """
        Test the revenue query against expected results.

        This test executes the revenue query, retrieves the results,
        and compares them to the expected results stored in a CSV file.
        """
        sql_file_path = self.sql_dir / "revenue_query_with_alias.sql"
        with open(sql_file_path, "r") as sql_file:
            sql_commands = sql_file.read()

        res = execute_query(sql_commands, self.db_path)
        df = pd.DataFrame(res[0], columns=res[1])
        test_csv = self.test_dir / "data" / "revenue_query_with_alias.csv"
        df_test = pd.read_csv(test_csv)

        try:
            pdt.assert_frame_equal(df, df_test)
            logger.info("Revenue query DataFrame comparison passed.")
        except AssertionError as e:
            logger.error("Revenue query DataFrame comparison failed:", e)
            self.fail("Revenue query DataFrame comparison failed.")

    def test_client_sales_query(self):
        """
        Test the client sales query against expected results.

        This test executes the client sales query, retrieves the results,
        and compares them to the expected results stored in a CSV file.
        """
        sql_file_path = self.sql_dir / "client_sales_query.sql"
        with open(sql_file_path, "r") as sql_file:
            sql_commands = sql_file.read()

        res = execute_query(sql_commands, self.db_path)
        df = pd.DataFrame(res[0], columns=res[1])
        test_csv = self.test_dir / "data" / "client_sales_query.csv"
        df_test = pd.read_csv(test_csv)

        try:
            pdt.assert_frame_equal(df, df_test)
            logger.info("Client sales query DataFrame comparison passed.")
        except AssertionError as e:
            logger.error("Client sales query DataFrame comparison failed:", e)
            self.fail("Client sales query DataFrame comparison failed.")


if __name__ == "__main__":
    unittest.main()
