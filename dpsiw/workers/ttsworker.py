from azure.storage.queue import QueueClient
from dpsiw.agents import *
from dpsiw.workers.worker import Worker


class TTSWorker(Worker):
    def __init__(self, queue_client: QueueClient = None, action: any = None):
        super().__init__(queue_client, action)
