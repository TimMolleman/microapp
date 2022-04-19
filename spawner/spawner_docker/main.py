import logging
import sys

logging.Logger.root.level = 10


def main(msg):
    """Triggers from a service bus message. It creates an Azure Container Instance ContainerGroup and Container that runs
    the worker docker image. This docker image contains a job that takes the message - which is supposed to be a name - and
    adds all the numbers in a Azure Cosmos database together for this person.

    Args:
        msg (func.ServiceBusMessage): Servicebus message sent from the app-queue
    """
    logging.debug("Debug message here")
    logging.info(sys.version_info[0], sys.version_info[1])
    
    logging.info(help('modules'))