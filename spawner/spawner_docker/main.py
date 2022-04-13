import logging
import random
import string
from typing import List

import azure.functions as func
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (ContainerGroup, Container, ContainerPort, Port, IpAddress, EnvironmentVariable,
                                                 ResourceRequirements, ResourceRequests, ContainerGroupNetworkProtocol, OperatingSystemTypes,
                                                 ImageRegistryCredential, ContainerGroupRestartPolicy)

from spawner_docker.config import azure_context, ACIConfig, ACRSettings, CosmosSettings

client = ContainerInstanceManagementClient(azure_context.credentials, azure_context.subscription_id)


def main(msg: func.ServiceBusMessage) -> None:
    """Triggers from a service bus message. It creates an Azure Container Instance ContainerGroup and Container that runs
    the worker docker image. This docker image contains a job that takes the message - which is supposed to be a name - and
    adds all the numbers in a Azure Cosmos database together for this person.

    Args:
        msg (func.ServiceBusMessage): Servicebus message sent from the app-queue
    """
    # Test test
    # Decode message
    message = msg.get_body().decode('utf-8')
    
    # Create container name for run and obtain environment variables for the worker docker image
    container_name = _get_container_name(message)
    env_vars = _create_env_vars(message, container_name)
    
    # Create container group and run image
    _create_container_group(ACIConfig().resource_group.get_secret_value(), 
                            container_name, 
                            ACIConfig().location, 
                            ACIConfig().image_name, 
                            env_vars)

    logging.info('Python ServiceBus queue trigger processed message: %s',
                 message)


def _create_env_vars(message: str, container_name: str) -> List[EnvironmentVariable]:
    """Creates a number of environment variables needed for running the job.

    Args:
        message (str): The message from the Azure Service Bus queue
        container_name (str):

    Returns:
        List[EnvironmentVariable]: List of environment variables
    """
    msg_var = EnvironmentVariable(name='MESSAGE', value=message)
    container_name_var = EnvironmentVariable(name='CONTAINER_NAME', value=container_name)
    
    # Cosmos DB variables
    cosmos_endpoint_var = EnvironmentVariable(name='COSMOS_DB_ENDPOINT', value=CosmosSettings().cosmos_db_endpoint.get_secret_value())
    cosmos_db_key_var = EnvironmentVariable(name='COSMOS_DB_KEY', secure_value=CosmosSettings().cosmos_db_key.get_secret_value())
    cosmos_app_db_var = EnvironmentVariable(name='COSMOS_APP_DB', secure_value=CosmosSettings().cosmos_app_db.get_secret_value())
    
    return [msg_var, container_name_var, cosmos_endpoint_var, cosmos_db_key_var, cosmos_app_db_var]


def _get_container_name(message: str) -> str:
    """Gets container name. It is randomly generated from the queue name + a random string.

    Args:
        message (str):

    Returns:
        str: Randomly generated container name
    """
    random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(50))
    return f'{ACIConfig().base_name_container}-{message}-{random_string}'

def _create_container_group(resource_group_name: str, name: str, location: str, image: str, env_vars: List[EnvironmentVariable]) -> None:
    """Creates the container group with single container for the job the job to run in it for Azure Container Instance.

    Args:
        resource_group_name (str):
        name (str): Name of container instance
        location (str): Location of ACI
        image (str): Image name
        env_vars (List[EnvironmentVariable]): Environment variables defined earlier.
    """
     # Setup default values
    port = 80
    restart_policy = ContainerGroupRestartPolicy(value='Never')

    # Set memory and cpu
    container_resource_requests = ResourceRequests(memory_in_gb = 1, cpu = 1)
    container_resource_requirements = ResourceRequirements(requests = container_resource_requests)
    
    # Image registry credentials
    credentials = ImageRegistryCredential(server=ACRSettings().server.get_secret_value(), 
                                          username=ACRSettings().username.get_secret_value(),
                                          password=ACRSettings().password.get_secret_value())
    
    # Create container for doing the job
    container = Container(name=name,
                          image=image,
                          resources=container_resource_requirements,
                          ports=[ContainerPort(port=port)],
                          environment_variables=env_vars)

    # Defaults for container group
    cgroup_os_type = OperatingSystemTypes.linux
    cgroup_ip_address = IpAddress(ports = [Port(protocol=ContainerGroupNetworkProtocol.tcp, port = port)], type="Public")

    # Create container group with just the single container
    cgroup = ContainerGroup(location=location,
                            containers=[container],
                            os_type=cgroup_os_type,
                            ip_address=cgroup_ip_address,
                            image_registry_credentials=[credentials],
                            restart_policy=restart_policy)

    client.container_groups.begin_create_or_update(resource_group_name, name, cgroup)
