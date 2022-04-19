import os
from cosmos_db.cosmos_db import CosmosDB
from helpers import transform


def aggregate_data():
    """Aggregates data for user and upsert to cosmos db."""
    name = os.environ['MESSAGE']

    # Retrieve the number items
    cosmos_db = CosmosDB()
    raw_items = cosmos_db.retrieve_raw_items(name=name)

    # If there are items, aggregate the numbers and write to cosmos
    if raw_items:
        aggregated_number = transform.add_raw_numbers(raw_items)

        # Create item to write away
        aggregated_item = {'id': name, 'name': name, 'number': aggregated_number}
        cosmos_db.upsert_aggregated_item(aggregated_item)


if __name__ == '__main__':
    aggregate_data()
