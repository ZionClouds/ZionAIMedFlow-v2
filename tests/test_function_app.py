import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from src.azurefunctions.ocrextractinfo.function_app import StorageTrigger, queue_trigger
from src.azurefunctions.ocrextractinfo.pgdatabase import BlobInfo

class TestFunctionApp(unittest.TestCase):
    @patch("src.azurefunctions.ocrextractinfo.function_app.datetime")
    @patch("src.azurefunctions.ocrextractinfo.function_app.send_queue_message")
    @patch("src.azurefunctions.ocrextractinfo.function_app.db_insert")
    def test_storage_trigger_transcribe(self, mock_db_insert, mock_send_queue_message, mock_datetime):
        # Mock datetime
        mock_datetime.now.return_value = datetime(2024, 12, 21, 17, 17, 20, 713583, tzinfo=timezone.utc)

        # Mock InputStream
        myblob = Mock()
        myblob.name = "testfile.txt"
        myblob.uri = "https://test/bloburi"
        myblob.length = 1024

        # Call the function
        with patch("src.azurefunctions.ocrextractinfo.function_app.uuid.uuid4", return_value="1234"):
            StorageTrigger(myblob)

        # Validate BlobInfo
        expected_blob_info = BlobInfo(
            id="1234",
            type="transcribe",  # Updated to match the function's behavior
            blobName="testfile.txt",
            blobURI="https://test/bloburi",
            status="pending",
            ts="2024-12-21T17:17:20.713583+00:00",
        )

        # Assertions
        mock_send_queue_message.assert_called_once_with(expected_blob_info)
        mock_db_insert.assert_called_once_with(expected_blob_info)

    @patch("src.azurefunctions.ocrextractinfo.function_app.BlobInfo.from_json")
    def test_queue_trigger(self, mock_from_json):
        # Mock QueueMessage
        azqueue = Mock()
        azqueue.get_body.return_value = b'{"id": "1234", "type": "extract", "blobName": "testfile.txt", "blobURI": "https://test/bloburi", "status": "pending", "ts": "2024-12-21T12:00:00Z"}'

        # Mock BlobInfo
        blob_info = BlobInfo(
            id="1234",
            type="extract",
            blobName="testfile.txt",
            blobURI="https://test/bloburi",
            status="pending",
            ts="2024-12-21T12:00:00Z",
        )
        mock_from_json.return_value = blob_info

        # Call the function
        queue_trigger(azqueue)

        # Assertions
        azqueue.get_body.assert_called_once()
        mock_from_json.assert_called_once_with({
            "id": "1234",
            "type": "extract",
            "blobName": "testfile.txt",
            "blobURI": "https://test/bloburi",
            "status": "pending",
            "ts": "2024-12-21T12:00:00Z"
        })

if __name__ == "__main__":
    unittest.main()
