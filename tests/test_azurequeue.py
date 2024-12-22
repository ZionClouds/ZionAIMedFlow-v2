import unittest
from unittest.mock import patch, Mock
import os
import json
from azure.storage.queue import QueueClient, BinaryBase64EncodePolicy
from src.azurefunctions.ocrextractinfo.azurequeue import send_queue_message
from src.azurefunctions.ocrextractinfo.pgdatabase import BlobInfo

class TestAzureQueue(unittest.TestCase):

    @patch('src.azurefunctions.ocrextractinfo.azurequeue.QueueClient')
    @patch('src.azurefunctions.ocrextractinfo.azurequeue.os')
    def test_send_queue_message_success(self, mock_os, mock_queue_client):
        # Mock environment variable
        mock_os.getenv.return_value = 'test-connection-string'

        # Mock the QueueClient and sender
        mock_queue_client_instance = Mock()
        mock_queue_client.from_connection_string.return_value = mock_queue_client_instance

        blob_info = BlobInfo(
            id="1234",
            type="extract",
            blobName="testfile.txt",
            blobURI="https://test/bloburi",
            status="pending",
            ts="2024-12-21T17:17:20.713583+00:00",
        )

        send_queue_message(blob_info)

        # Assertions
        mock_queue_client.from_connection_string.assert_called_once_with(
            conn_str='test-connection-string',
            queue_name="pdf-queue",
            message_encode_policy=BinaryBase64EncodePolicy()
        )
        message_content = json.dumps(blob_info.to_json()).encode('ascii')
        mock_queue_client_instance.send_message.assert_called_once_with(message_content)

    @patch('src.azurefunctions.ocrextractinfo.azurequeue.QueueClient')
    @patch('src.azurefunctions.ocrextractinfo.azurequeue.os')
    def test_send_queue_message_failure(self, mock_os, mock_queue_client):
        # Mock environment variable
        mock_os.getenv.return_value = 'test-connection-string'

        # Mock the QueueClient and sender
        mock_queue_client_instance = Mock()
        mock_queue_client.from_connection_string.return_value = mock_queue_client_instance

        # Simulate an exception when sending the message
        mock_queue_client_instance.send_message.side_effect = Exception("Failed to send message")

        blob_info = BlobInfo(
            id="1234",
            type="extract",
            blobName="testfile.txt",
            blobURI="https://test/bloburi",
            status="pending",
            ts="2024-12-21T17:17:20.713583+00:00",
        )

        with self.assertLogs(level="ERROR") as log:
            send_queue_message(blob_info)

        # Assertions
        mock_queue_client.from_connection_string.assert_called_once_with(
            conn_str='test-connection-string',
            queue_name="pdf-queue",
            message_encode_policy=BinaryBase64EncodePolicy()
        )
        message_content = json.dumps(blob_info.to_json()).encode('ascii')
        mock_queue_client_instance.send_message.assert_called_once_with(message_content)
        self.assertIn("Failed to send message", log.output[0])

if __name__ == "__main__":
    unittest.main()