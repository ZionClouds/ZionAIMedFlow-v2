import unittest
from unittest.mock import AsyncMock, patch, Mock
import os
import uuid
from src.azurefunctions.mymdnotes.function_app import StorageTrigger, send_queue_message
from src.azurefunctions.mymdnotes.models import Message, MedicalNotesMD
from src.azurefunctions.mymdnotes.mgdatabase import EventsRepository
import unittest
from unittest.mock import patch, AsyncMock, MagicMock

class TestFunctionApp(unittest.TestCase):

    @patch('function_app.ServiceBusClient')
    @patch('function_app.DefaultAzureCredential')
    @patch('function_app.os')
    async def test_send_queue_message_with_connection_string(self, mock_os, mock_default_credential, mock_service_bus_client):
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key: {
            "SB_QUEUE": "test-queue",
            "SB_CONNECTION_STRING": "test-connection-string",
            "MSI_CLIENT_ID": None
        }.get(key)

        # Mock the ServiceBusClient and sender
        mock_sender = AsyncMock()
        mock_service_bus_client.from_connection_string.return_value.__aenter__.return_value.get_queue_sender.return_value = mock_sender

        # Call the function
        await send_queue_message("test-correlation-id", "test-payload")

        # Assertions
        mock_service_bus_client.from_connection_string.assert_called_once_with("test-connection-string")
        mock_sender.send_messages.assert_called_once()
        self.assertEqual(mock_sender.send_messages.call_args[0][0].correlation_id, "test-correlation-id")
        self.assertEqual(mock_sender.send_messages.call_args[0][0].body, "test-payload")

    @patch('function_app.ServiceBusClient')
    @patch('function_app.DefaultAzureCredential')
    @patch('function_app.os')
    async def test_send_queue_message_with_managed_identity(self, mock_os, mock_default_credential, mock_service_bus_client):
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key: {
            "SB_QUEUE": "test-queue",
            "SB_CONNECTION_STRING": None,
            "MSI_CLIENT_ID": "test-client-id"
        }.get(key)

        # Mock the ServiceBusClient and sender
        mock_sender = AsyncMock()
        mock_service_bus_client.return_value.__aenter__.return_value.get_queue_sender.return_value = mock_sender

        # Call the function
        await send_queue_message("test-correlation-id", "test-payload")

        # Assertions
        mock_service_bus_client.assert_called_once()
        mock_sender.send_messages.assert_called_once()
        self.assertEqual(mock_sender.send_messages.call_args[0][0].correlation_id, "test-correlation-id")
        self.assertEqual(mock_sender.send_messages.call_args[0][0].body, "test-payload")

    @patch('function_app.ServiceBusClient')
    @patch('function_app.DefaultAzureCredential')
    @patch('function_app.func.InputStream')
    @patch('function_app.logging')
    @patch('function_app.os')
    @patch('function_app.uuid')
    async def test_storage_trigger(self, mock_uuid, mock_os, mock_logging, mock_input_stream, mock_default_credential, mock_service_bus_client):
        # Mock the input stream
        mock_input_stream.name = 'provider-12345-file.txt'
        mock_input_stream.length = 1024

        # Mock the UUID
        mock_uuid.uuid4.return_value = uuid.UUID('12345678123456781234567812345678')

        # Mock the os.path functions
        mock_os.path.basename.return_value = 'provider-12345-file.txt'
        mock_os.path.splitext.return_value = ('provider-12345-file', '.txt')

        # Mock the ServiceBusClient and sender
        mock_sender = AsyncMock()
        mock_service_bus_client.return_value.__aenter__.return_value.get_queue_sender.return_value = mock_sender

        # Call the function
        await StorageTrigger(mock_input_stream)

        # Assertions
        mock_logging.info.assert_any_call("Python blob trigger function processed blob"
                                          "Name: provider-12345-file.txt"
                                          "Blob Size: 1024 bytes")
        mock_sender.send_messages.assert_called_once()
        mock_logging.info.assert_any_call("Message sent to queue: your-queue-name")

if __name__ == "__main__":
    unittest.main()