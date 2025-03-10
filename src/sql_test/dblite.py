"""
This file is a to-tool for testing the SQLite database  .
It is used to create the database and the tables.
It is also used to execute the SQL scripts.
"""

import datetime
import os

# External imports
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
from loguru import logger

# Internal imports
from src.sql_test.synthetic_data import fake_it


# Setup SQLite Database in a specific local directory
def get_paths() -> Tuple[Path, Path]:
    """Get the paths to the local database directory and the database file"""
    local_dir = Path(__file__).parent
    db_dir = local_dir / "local_db"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "db.sqlite3"
    return local_dir, db_path


# Setup SQLite Database
def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Create and return a database connection"""
    if db_path is None:
        _, db_path = get_paths()

    conn = sqlite3.connect(db_path)
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    # Return dictionary-like rows
    conn.row_factory = sqlite3.Row
    return conn


def request(query: str, args: Any = None, fetch: bool = True, commit: bool = False) -> Any:
    """Execute a database query with optional parameters"""
    conn = get_connection()
    cur = conn.cursor()

    if args:
        cur.execute(query, args)
    else:
        cur.execute(query)

    if fetch:
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        result = rows, columns
    else:
        result = None

    if commit:
        conn.commit()

    conn.close()
    return result


def execute_sql_file(sql_file_path: Path, db_path: Path) -> None:
    """
    Execute SQL commands from a file using sqlite3.

    Parameters:
    - sql_file_path: Path to the SQL file containing commands.
    """
    conn = get_connection(db_path)

    try:
        with open(sql_file_path, "r") as sql_file:
            sql_commands = sql_file.read()

        cursor = conn.cursor()
        try:
            cursor.executescript(sql_commands)  # Use executescript to execute multiple commands
            conn.commit()
            logger.info(f"Executed SQL script from {sql_file_path} successfully.")
        except Exception as e:
            conn.rollback()
            logger.warning(
                f"Failed to execute SQL script from {sql_file_path}. Error: {e} - Ignoring error"
            )
            # If exists already we just ignore the error
            # raise
        finally:
            cursor.close()
    finally:
        conn.close()


def __create_database_if_not_exists(db_path: Path) -> None:
    if db_path is None:
        raise ValueError("db_path is None")

    # check if the database exists
    files_exist = os.path.isfile(db_path)
    if not files_exist:
        # create the database
        conn = get_connection(db_path)
        conn.close()


# Create Users Table and authentification
# ---------------- NOT NEEDED HERE ----------------
# --------------------- PASS ----------------------


def __create_tables(db_path: Path) -> None:
    queries_dir = Path(__file__).parent / "create_tables"
    __create_database_if_not_exists(db_path)

    execute_sql_file(queries_dir / "product_nomenclature.sql", db_path)
    execute_sql_file(queries_dir / "transactions.sql", db_path)


def insert_data(conn: sqlite3.Connection, table_name: str, data: List[Dict[str, Any]]) -> None:
    """
    Insert data into a specified table in the SQLite database.

    Parameters:
    - conn: SQLite database connection object.
    - table_name: Name of the table to insert data into.
    - data: List of dictionaries containing the data to insert.
    """
    if not data:
        logger.warning("No data provided for insertion.")
        return

    columns = data[0].keys()  # Get the columns from the first dictionary in the list
    placeholders = ", ".join(["?"] * len(columns))  # Create placeholders for values
    query = f"""
    INSERT INTO {table_name} ({", ".join(columns)})
    VALUES ({placeholders})
    """
    values = [
        tuple(row[col] for col in columns) for row in data
    ]  # Extract values for each row based on the column names

    try:
        with conn:
            conn.executemany(query, values)  # Perform the bulk insert
            logger.info(f"Inserted data into {table_name} successfully.")
    except Exception as e:
        logger.error(f"Failed to insert data into {table_name}. Error: {e}")
        raise


def insert_product_nomenclature_sample_data(
    sample_data: List[Dict[str, Any]], db_path: Path
) -> None:
    # Sample data to insert into the PRODUCT_NOMENCLATURE table
    # sample_data = [
    #     {"product_id": 490756, "product_type": "MEUBLE", "product_name": "Chaise"},
    #     {"product_id": 389728, "product_type": "DECO", "product_name": "Boule de Noël"},
    #     {"product_id": 549380, "product_type": "MEUBLE", "product_name": "Canapé"},
    #     {"product_id": 293718, "product_type": "DECO", "product_name": "Mug"},
    # ]

    # Get a connection to the database
    conn = get_connection(db_path)

    try:
        # Insert the sample data into the PRODUCT_NOMENCLATURE table
        product_nomenclature_data = [
            {str(k): v for k, v in record.items()} for record in sample_data
        ]
        insert_data(conn, "PRODUCT_NOMENCLATURE", product_nomenclature_data)
    finally:
        # Close the connection
        conn.close()


def insert_transactions_sample_data(sample_data: List[Dict[str, Any]], db_path: Path) -> None:
    # Sample data to insert into the TRANSACTIONS table
    # sample_data = [
    #     {"date": "2020-01-01", "order_id": 1234, "client_id": 999, "prod_id": 490756, "prod_price": 50, "prod_qty": 1},
    #     {"date": "2020-01-01", "order_id": 1234, "client_id": 999, "prod_id": 389728, "prod_price": 3.56, "prod_qty": 4},
    #     {"date": "2020-01-01", "order_id": 3456, "client_id": 845, "prod_id": 490756, "prod_price": 50, "prod_qty": 2},
    #     {"date": "2020-01-01", "order_id": 3456, "client_id": 845, "prod_id": 549380, "prod_price": 300, "prod_qty": 1},
    #     {"date": "2020-01-01", "order_id": 3456, "client_id": 845, "prod_id": 293718, "prod_price": 10, "prod_qty": 6},
    # ]

    # Get a connection to the database
    conn = get_connection(db_path)

    try:
        # Insert the sample data into the TRANSACTIONS table
        transaction_data = [{str(k): v for k, v in record.items()} for record in sample_data]
        insert_data(conn, "TRANSACTIONS", transaction_data)
    finally:
        # Close the connection
        conn.close()


def execute_query(
    query: str, db_path: Path | None = None, fetch: bool = True, commit: bool = False
) -> Any:
    """
    Execute a query on a specified table in the SQLite database.

    Parameters:
    - query: SQL query to execute.
    - fetch: Boolean indicating whether to fetch results.
    - commit: Boolean indicating whether to commit the transaction.

    Returns:
    - If fetch is True, returns a tuple of (rows, columns).
    - If fetch is False, returns None.
    """
    conn = get_connection(db_path)  # if None, it uses the default db_path
    cur = conn.cursor()

    try:
        cur.execute(query)
        if fetch:
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result = rows, columns
        else:
            result = None

        if commit:
            conn.commit()

        logger.info("Executed query successfully.")
    except Exception as e:
        logger.error(f"Failed to execute query. Error: {e}")
        raise
    finally:
        conn.close()

    return result


def convert_to_date(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def initialise_db(local_dir: Path | None = None, from_file: bool = False) -> Path:
    if local_dir is None:
        local_dir, db_path = get_paths()
    else:
        db_path = local_dir / "local_db" / "db.sqlite3"
        # Ensure the directory exists
        os.makedirs(local_dir / "local_db", exist_ok=True)

    __create_tables(db_path)
    if from_file:
        # Make sure the data directory exists with the data files
        file_path = local_dir / "data"
        if not file_path.exists():
            raise FileNotFoundError(f"Data directory not found at {file_path}")

        # Check for each required file
        product_nomenclature_file = file_path / "product_nomenclature.csv"
        transaction_file = file_path / "transactions.csv"

        if not product_nomenclature_file.exists():
            logger.error(
                f"File not found: {product_nomenclature_file}. Please ensure the file is placed in the directory."
            )
            raise FileNotFoundError(f"File not found: {product_nomenclature_file}")

        if not transaction_file.exists():
            logger.error(
                f"File not found: {transaction_file}. Please ensure the file is placed in the directory."
            )
            raise FileNotFoundError(f"File not found: {transaction_file}")

        # Load data if files exist
        product_nomenclature_data = pd.read_csv(product_nomenclature_file).to_dict(
            orient="records"
        )
        transaction_data = pd.read_csv(transaction_file).to_dict(orient="records")
    else:
        product_nomenclature_data, transaction_data = fake_it()

    product_nomenclature_data = [
        {str(k): v for k, v in record.items()} for record in product_nomenclature_data
    ]
    transaction_data = [{str(k): v for k, v in record.items()} for record in transaction_data]

    insert_product_nomenclature_sample_data(product_nomenclature_data, db_path)
    insert_transactions_sample_data(transaction_data, db_path)
    return db_path


if __name__ == "__main__":
    db_path = initialise_db()
    logger.info(f"Database initialised: {db_path}")
    # res = execute_query("SELECT * FROM TRANSACTIONS")
    # df = pd.DataFrame(res[0], columns=res[1])
    # df["date"] = df["date"].apply(convert_to_date)
    # print(df)

    local_dir, _ = get_paths()
    sql_file_path = local_dir / "queries"
    with open(sql_file_path / "revenue_query_with_alias.sql", "r") as sql_file:
        sql_commands = sql_file.read()
    res = execute_query(sql_commands)
    df = pd.DataFrame(res[0], columns=res[1])

    with open(sql_file_path / "client_sales_query.sql", "r") as sql_file:
        sql_commands = sql_file.read()
    res = execute_query(sql_commands)
    df = pd.DataFrame(res[0], columns=res[1])
    os.remove(db_path)
    logger.info(f"Database deleted: {db_path}")
