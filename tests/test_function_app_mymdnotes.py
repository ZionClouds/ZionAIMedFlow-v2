import unittest
from unittest.mock import AsyncMock, patch, Mock
import os
import uuid
from src.azurefunctions.mymdnotes.function_app import StorageTrigger, send_queue_message
from src.azurefunctions.mymdnotes.models import Message, MedicalNotesMD
from src.azurefunctions.mymdnotes.mgdatabase import EventsRepository

class TestFunctionAppMyMDNotes(unittest.IsolatedAsyncioTestCase):
    @patch("src.azurefunctions.mymdnotes.function_app.ServiceBusClient")
    async def test_send_queue_message_success(self, mock_service_bus_client):
        # Mock the Service Bus client and sender
        mock_sender = AsyncMock()
        mock_queue_client = AsyncMock()
        mock_queue_client.get_queue_sender.return_value = mock_sender
        mock_service_bus_client.from_connection_string.return_value = mock_queue_client

        # Call the function
        await send_queue_message("1234", '{"key": "value"}')

        # Assertions
        mock_service_bus_client.from_connection_string.assert_called_once_with(os.getenv("SB_CONNECTION_STRING"))
        mock_queue_client.get_queue_sender.assert_called_once_with(queue_name=os.getenv("SB_QUEUE"))
        mock_sender.send_messages.assert_called_once()

    @patch("src.azurefunctions.mymdnotes.function_app.ServiceBusClient")
    async def test_send_queue_message_failure(self, mock_service_bus_client):
        # Mock the Service Bus client to raise an exception
        mock_service_bus_client.from_connection_string.side_effect = Exception("Service Bus Error")

        # Call the function and expect it to handle the exception
        with self.assertLogs(level="ERROR") as log:
            await send_queue_message("1234", '{"key": "value"}')

        self.assertIn("Service Bus Error", log.output[0])

    @patch("src.azurefunctions.mymdnotes.function_app.send_queue_message", new_callable=AsyncMock)
    @patch("src.azurefunctions.mymdnotes.function_app.EventsRepository")
    async def test_storage_trigger_success(self, mock_events_repository, mock_send_queue_message):
        # Mock InputStream
        myblob = Mock()
        myblob.name = "provider-1234.wav"
        myblob.uri = "https://test.blob.core.windows.net/container/provider-1234.wav"
        myblob.length = 1024

        # Mock repository
        mock_event_method = AsyncMock()
        mock_events_repository.return_value.event = mock_event_method

        # Call the function
        await StorageTrigger(myblob)

        # Assertions
        mock_send_queue_message.assert_called_once()
        mock_events_repository.assert_called_once()
        mock_event_method.assert_called_once()

    @patch("src.azurefunctions.mymdnotes.function_app.send_queue_message", new_callable=AsyncMock)
    async def test_storage_trigger_invalid_filename(self, mock_send_queue_message):
        # Mock InputStream with an invalid file name
        myblob = Mock()
        myblob.name = "invalid-file-name.wav"
        myblob.uri = "https://test.blob.core.windows.net/container/invalid-file-name.wav"
        myblob.length = 1024

        # Call the function and expect it to log an error
        with self.assertLogs(level="ERROR") as log:
            await StorageTrigger(myblob)

        self.assertIn("could not be parsed", log.output[0])
        mock_send_queue_message.assert_not_called()

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
