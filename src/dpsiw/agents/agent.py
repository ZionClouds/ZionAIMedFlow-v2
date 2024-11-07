import logging

from dpsiw.messages.message import Message
from dpsiw.services.mgdatabase import EventsRepository
from dpsiw.services.servicecontainer import get_service_container_instance
from dpsiw.services.settings import Settings, get_settings_instance


class Agent:
    """
    Base class for all agents
    """

    def __init__(self) -> None:
        self.message: Message = None
        self.service_container = get_service_container_instance()
        self.settings: Settings = get_settings_instance()
        self.events_repository = EventsRepository()

    def log_workflow(self, level: str = 'INFO', pid: str = '', message: str = '', status: str = '') -> None:
        """
        This method is used to log the status of the workflow
        """
        match level:
            case 'INFO':
                logging.info(f'{pid} - {message} - {status}')
            case 'ERROR':
                logging.error(f'{pid} - {message} - {status}')
            case 'WARNING':
                logging.warning(f'{pid} - {message} - {status}')
            case 'DEBUG':
                logging.debug(f'{pid} - {message} - {status}')
            case _:
                logging.info(f'{pid} - {message} - {status}')
        self.events_repository.insert(level, pid, message, status)

    def process(self, message: Message) -> None:
        """
        This does the work on the message received from the worker
        """
        pass

    def save(self) -> None:
        """
        This method is called after processing the message
        """
        pass

    def pre_validate(self) -> tuple[bool, str]:
        """
        This method is called before processing the message
        """
        return (True, "")

    def post_validate(self) -> tuple[bool, str]:
        """
        This method is called after processing the message
        """
        return (True, "")
