# External imports
import random
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
from loguru import logger


def fake_it(store_data: bool = False) -> Tuple[List[Dict], List[Dict]]:
    """
    Generate synthetic data for PRODUCT_NOMENCLATURE and TRANSACTIONS tables.
    For better results in for production testing: https://docs.sdk.ydata.ai/latest/
    Returns:
        Tuple containing two lists of dictionaries:
        - product_nomenclature_data: List of dictionaries with product metadata.
        - transaction_data: List of dictionaries with transaction details.
    """

    # Define synthetic data for the PRODUCT_NOMENCLATURE table
    product_nomenclature_data = [
        {"product_id": 1, "product_type": "MEUBLE", "product_name": "Chair"},
        {"product_id": 2, "product_type": "MEUBLE", "product_name": "Table"},
        {"product_id": 3, "product_type": "MEUBLE", "product_name": "Sofa"},
        {"product_id": 4, "product_type": "DECO", "product_name": "Lamp"},
        {"product_id": 5, "product_type": "DECO", "product_name": "Painting"},
        {"product_id": 6, "product_type": "DECO", "product_name": "Rug"},
    ]

    # Convert to DataFrame
    if store_data:
        product_nomenclature_df = pd.DataFrame(product_nomenclature_data)
        product_nomenclature_df.to_csv("./data/product_nomenclature.csv", index=False)
        logger.info("Product nomenclature data stored in ./data/product_nomenclature.csv")

    # Define the date range for generating transaction data
    start_date = datetime(2018, 12, 1)
    end_date = datetime(2020, 1, 31)

    # Initialize an empty list to store transaction data
    transaction_data = []
    transaction_id = 1  # Initialize transaction ID counter
    current_date = start_date  # Start from the initial date

    # Generate transaction data with 3 transactions per month
    while current_date <= end_date:
        for _ in range(3):  # Create 3 transactions for each month
            transaction_data.append(
                {
                    "transaction_id": transaction_id,  # Unique identifier for the transaction
                    "date": current_date.strftime(
                        "%Y-%m-%d"
                    ),  # Transaction date in YYYY-MM-DD format
                    "order_id": random.randint(1000, 9999),  # Randomly generated order ID
                    "client_id": random.randint(1, 50),  # Randomly generated client ID
                    "prod_id": random.choice(range(1, 7)),  # Randomly select a product ID
                    "prod_price": round(
                        random.uniform(5, 500), 2
                    ),  # Randomly generated product price
                    "prod_qty": random.randint(1, 10),  # Randomly generated product quantity
                }
            )
            transaction_id += 1  # Increment transaction ID for the next entry

        # Move to the first day of the next month
        next_month = current_date.month % 12 + 1
        next_year = current_date.year if next_month != 1 else current_date.year + 1
        current_date = datetime(next_year, next_month, 1)

    # Convert to DataFrame
    # Convert to DataFrame
    if store_data:
        transactions_df = pd.DataFrame(transaction_data)
        transactions_df.to_csv("./data/transactions.csv", index=False)
        logger.info("Transactions data stored in ./data/transactions.csv")

    # Return the generated synthetic data for both tables
    return product_nomenclature_data, transaction_data


if __name__ == "__main__":
    fake_it(store_data=True)
