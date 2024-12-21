import unittest
from unittest.mock import Mock, patch
from src.azurefunctions.ocrextractinfo.azurequeue import send_queue_message
from src.azurefunctions.ocrextractinfo.pgdatabase import BlobInfo

class TestAzureQueue(unittest.TestCase):
    @patch("src.azurefunctions.ocrextractinfo.azurequeue.QueueServiceClient")
    def test_send_queue_message_success(self, mock_queue_service_client):
        # Mock the queue client and sender
        mock_queue_client = Mock()
        mock_sender = Mock()
        mock_queue_service_client.from_connection_string.return_value = mock_queue_client
        mock_queue_client.get_queue_client.return_value = mock_sender

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
        mock_queue_service_client.from_connection_string.assert_called_once()
        mock_queue_client.get_queue_client.assert_called_once()
        mock_sender.send_message.assert_called_once_with(blob_info.to_json())

    @patch("src.azurefunctions.ocrextractinfo.azurequeue.QueueServiceClient")
    def test_send_queue_message_failure(self, mock_queue_service_client):
        # Mock connection to raise an error
        mock_queue_service_client.from_connection_string.side_effect = Exception("Queue service error")

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

        self.assertIn("Error sending message to queue", log.output[0])

if __name__ == "__main__":
    unittest.main()
