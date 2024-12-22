import unittest
from unittest.mock import patch, Mock
from src.dpsiw.agents.agent import Agent
from src.dpsiw.messages.message import Message
from src.dpsiw.services.mgdatabase import EventsRepository
from src.dpsiw.services.servicecontainer import get_service_container_instance
from src.dpsiw.services.settingsservice import SettingsService, get_settings_instance

class TestAgent(unittest.TestCase):
    @patch('dpsiw.agents.agent.get_service_container_instance')
    @patch('dpsiw.agents.agent.get_settings_instance')
    @patch('dpsiw.agents.agent.EventsRepository')
    def setUp(self, mock_events_repository, mock_get_settings_instance, mock_get_service_container_instance):
        self.mock_events_repository = mock_events_repository.return_value
        self.mock_get_settings_instance = mock_get_settings_instance.return_value
        self.mock_get_service_container_instance = mock_get_service_container_instance.return_value
        self.agent = Agent()
        print('test')
        
    def test_log_workflow_info(self):
        self.agent.log_workflow(level='INFO', pid='1234', message='Test message', status='Success')
        self.mock_events_repository.insert.assert_called_once_with('INFO', '1234', 'Test message', 'Success')

    def test_log_workflow_error(self):
        self.agent.log_workflow(level='ERROR', pid='1234', message='Test message', status='Failed')
        self.mock_events_repository.insert.assert_called_once_with('ERROR', '1234', 'Test message', 'Failed')

    def test_log_workflow_warning(self):
        self.agent.log_workflow(level='WARNING', pid='1234', message='Test message', status='Warning')
        self.mock_events_repository.insert.assert_called_once_with('WARNING', '1234', 'Test message', 'Warning')

    def test_log_workflow_debug(self):
        self.agent.log_workflow(level='DEBUG', pid='1234', message='Test message', status='Debugging')
        self.mock_events_repository.insert.assert_called_once_with('DEBUG', '1234', 'Test message', 'Debugging')

    def test_log_workflow_default(self):
        self.agent.log_workflow(level='UNKNOWN', pid='1234', message='Test message', status='Unknown')
        self.mock_events_repository.insert.assert_called_once_with('INFO', '1234', 'Test message', 'Unknown')

    def test_process(self):
        mock_message = Mock(spec=Message)
        self.agent.process(mock_message)
        # Add assertions based on the expected behavior of the process method

    def test_save(self):
        self.agent.save()
        # Add assertions based on the expected behavior of the save method

    def test_pre_validate(self):
        result = self.agent.pre_validate()
        self.assertEqual(result, (True, ""))

    def test_post_validate(self):
        result = self.agent.post_validate()
        self.assertEqual(result, (True, ""))

if __name__ == "__main__":
    unittest.main()