from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os


class ServiceBus:
    def __init__(self):
        conn_str = os.environ['SERVICEBUS_CONNECTION_STR']
        self.queue_name = os.environ['SERVICEBUS_QUEUE_NAME']
        self.client = ServiceBusClient.from_connection_string(conn_str=conn_str, logging_enable=True)

    def send_single_message(self, message: str) -> None:
        """Send a single message to the queue. It should be a string

        :param (str) message: Message to send to queue, usually a name
        """
        with self.client.get_queue_sender(self.queue_name) as sender:
            message = ServiceBusMessage(message)
            sender.send_messages(message)
