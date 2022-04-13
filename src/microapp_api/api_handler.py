from fastapi import Depends, FastAPI, HTTPException
from mangum import Mangum
import uvicorn
import logging

from api_schemas import NameVariables, NumberVariables
from cosmos_db.cosmos_db import CosmosDB
from servicebus.service_bus import ServiceBus
from helpers import transform

# Init app
app = FastAPI()
logger = logging.getLogger(__name__)


# Post number
@app.post('/post_raw_number', response_model=NumberVariables, status_code=200)
async def post_number(number_variables: NumberVariables) -> NumberVariables:
    """Posts a specified item to the cosmos database. Name and number are given in post body and then posted
    to the cosmos DB. Also, a message is pushed to Azure Servicebus Queue, which subsequently triggers a aggregation
    (sum) job as a docker container in ACI from Azure Functions trigger.

    :param (NumberVariables) number_variables: Name and number to add to cosmos DB
    :return: The number variables that were also passed into the function
    """
    try:
        # First insert the new item into the Cosmos database
        cosmos_db = CosmosDB()
        item = {'name': number_variables.name, 'number': number_variables.number}
        item = transform.add_random_id_and_date(item)
        cosmos_db.insert_to_raw(item)

        # Then add message to service bus queue to start a container in ACI
        service_bus = ServiceBus()
        service_bus.send_single_message(number_variables.name)
        return number_variables

    except Exception as e:
        logger.exception(f'Something went wrong getting the model, traceback: {e}')
        raise HTTPException(status_code=500, detail='An unexpected error occurred in the application backend')


@app.get('/get_aggregated_number', status_code=200)
async def get_aggregated_number(name_variables: NameVariables = Depends()) -> int:
    """Gets raw items from cosmos DB and then adds the numbers and returns them for certain name.

    :param name_variables: Contains name for retrieving raw items corresponding to name
    :return: Aggregated number
    """
    try:
        # Get raw numbers for user given the 'name'
        cosmos_db = CosmosDB()
        raw_items = cosmos_db.retrieve_raw_items(name_variables.name)

        # Aggregate the raw items to aggregated number
        aggregated_number = transform.add_raw_numbers(raw_items)
        return aggregated_number

    except Exception as e:
        logger.exception(f'Something went wrong getting the model, traceback: {e}')
        raise HTTPException(status_code=500, detail='An unexpected error occurred in the application backend')

# Include routers and create mangum handler
handler = Mangum(app)

if __name__ == '__main__':
    # Local run setup for the FastAPI application
    uvicorn.run(app='api_handler:app', port=8000, reload=True)
