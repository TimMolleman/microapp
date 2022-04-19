from azure.identity import DefaultAzureCredential, ClientSecretCredential
import os
from pydantic import BaseSettings, Field, SecretStr


# Azure context creation
class AzureContext:
    def __init__(self):
        # self.credentials = DefaultAzureCredential()
        # self.credentials = ClientSecretCredential(tenant_id='f69fca54-a603-4f55-b21d-f41a64cc6591',
        #                                           client_id='e1204621-4d03-4e1e-ba40-087399b6546f',
        #                                           client_secret='AjF7Q~APPiLV_XvUjik3MZpI-sNkgFykcDwmw')
        self.credentials = DefaultAzureCredential()
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')


azure_context = AzureContext()


# Cosmos db settings
class CosmosSettings(BaseSettings):
    cosmos_db_endpoint: SecretStr = Field(..., env='COSMOS_DB_ENDPOINT')
    cosmos_db_key: SecretStr = Field(..., env='COSMOS_DB_KEY')
    cosmos_app_db: SecretStr = Field(..., env='COSMOS_APP_DB')


# Azure ACR settings
class ACRSettings(BaseSettings):
    server: SecretStr = Field(..., env='ACR_SERVER')
    username: SecretStr = Field(..., env='ACR_USERNAME')
    password: SecretStr = Field(..., env='ACR_PASSWORD')


# Azure container instances settings 
class ACIConfig(BaseSettings):
    subscription_id: SecretStr = Field(..., env='AZURE_SUBSCRIPTION_ID')
    resource_group: SecretStr = Field(..., env='AZURE_RESOURCE_GROUP')
    location: str = Field(..., env='AZURE_LOCATION')
    base_name_container: str = Field(..., env='BASE_NAME_CONTAINER')
    image_name: str = Field(..., env='IMAGE_NAME')
    

