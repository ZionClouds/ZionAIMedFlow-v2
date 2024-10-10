from abc import ABC, abstractmethod
from azure.storage.queue import QueueClient


class BaseWorker(ABC):
    """
    Base worker class to listen to messages on a queue and process them
    """

    def __init__(self, queue_client: QueueClient = None, action=None) -> None:
        self.queue_client: QueueClient = None
        self.action: any = None

    @abstractmethod
    def process(self, endless: bool = False):
        """
        Process messages from the queue
        """
        pass

    @abstractmethod
    def start(self, instances: int = 1, endless: bool = False):
        """
        Start the worker
        """
        pass
