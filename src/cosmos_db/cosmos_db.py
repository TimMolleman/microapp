from azure.cosmos import CosmosClient
import os
from typing import Dict, List


class CosmosDB:
    def __init__(self):
        self.db_client = self._init_client()

        # Container connectors
        self.raw_container = self.db_client.get_container_client('raw-data')
        self.aggregated_container = self.db_client.get_container_client('aggregated-data')

    def insert_to_raw(self, item: dict) -> None:
        """Insert item into raw container. Contains name and number, adds id and datetime.

        :param item: Item to insert into raw container
        """
        # Connect to container and create item in it
        self.raw_container.create_item(item)

    def retrieve_raw_items(self, name: str) -> List[Dict[str, int]]:
        """Retrieve the raw items from the raw container for a certain name.

        :param name:
        :return: A list of dictionaries with e.g. 'number': 5
        """
        query = f'SELECT r.number FROM r WHERE r.name = \'{name}\''

        items = list(self.raw_container.query_items(query=query, enable_cross_partition_query=True))
        return items

    def upsert_aggregated_item(self, item: dict) -> None:
        """Upsert aggregated number into the aggregated cosmos database table.

        :param dict item: Item with aggregated number
        """
        self.aggregated_container.upsert_item(body=item)

    @staticmethod
    def _init_client():
        return (CosmosClient(url=os.environ['COSMOS_DB_ENDPOINT'], credential=os.environ['COSMOS_DB_KEY'])
                .get_database_client(database=os.environ['COSMOS_APP_DB']))
