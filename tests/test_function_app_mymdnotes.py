import unittest
from unittest.mock import AsyncMock, patch, Mock
import os
import uuid
from src.azurefunctions.mymdnotes.function_app import StorageTrigger, send_queue_message
from src.azurefunctions.mymdnotes.models import Message, MedicalNotesMD
from src.azurefunctions.mymdnotes.mgdatabase import EventsRepository

class TestFunctionApp(unittest.TestCase):

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
    async def test_storage_trigger_missing_file_id(self, mock_uuid, mock_os, mock_logging, mock_input_stream, mock_default_credential, mock_service_bus_client):
        # Mock the input stream with missing file ID
        mock_input_stream.name = 'provider--file.txt'
        mock_input_stream.length = 1024

        # Mock the UUID
        mock_uuid.uuid4.return_value = uuid.UUID('12345678123456781234567812345678')

        # Mock the os.path functions
        mock_os.path.basename.return_value = 'provider--file.txt'
        mock_os.path.splitext.return_value = ('provider--file', '.txt')

        # Mock the ServiceBusClient and sender
        mock_sender = AsyncMock()
        mock_service_bus_client.return_value.__aenter__.return_value.get_queue_sender.return_value = mock_sender

        # Call the function and expect it to log an error
        with self.assertLogs(level="ERROR") as log:
            await StorageTrigger(mock_input_stream)

        self.assertIn("could not be parsed", log.output[0])
        mock_sender.send_messages.assert_not_called()

    @patch('function_app.ServiceBusClient')
    @patch('function_app.DefaultAzureCredential')
    @patch('function_app.func.InputStream')
    @patch('function_app.logging')
    @patch('function_app.os')
    @patch('function_app.uuid')
    async def test_storage_trigger_missing_provider_name(self, mock_uuid, mock_os, mock_logging, mock_input_stream, mock_default_credential, mock_service_bus_client):
        # Mock the input stream with missing provider name
        mock_input_stream.name = '-12345-file.txt'
        mock_input_stream.length = 1024

        # Mock the UUID
        mock_uuid.uuid4.return_value = uuid.UUID('12345678123456781234567812345678')

        # Mock the os.path functions
        mock_os.path.basename.return_value = '-12345-file.txt'
        mock_os.path.splitext.return_value = ('-12345-file', '.txt')

        # Mock the ServiceBusClient and sender
        mock_sender = AsyncMock()
        mock_service_bus_client.return_value.__aenter__.return_value.get_queue_sender.return_value = mock_sender

        # Call the function and expect it to log an error
        with self.assertLogs(level="ERROR") as log:
            await StorageTrigger(mock_input_stream)

        self.assertIn("could not be parsed", log.output[0])
        mock_sender.send_messages.assert_not_called()

if __name__ == "__main__":
    unittest.main()