import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from src.azurefunctions.ocrextractinfo.function_app import StorageTrigger, queue_trigger
from src.azurefunctions.ocrextractinfo.pgdatabase import BlobInfo

class TestFunctionApp(unittest.TestCase):
    @patch("src.azurefunctions.ocrextractinfo.function_app.send_queue_message")
    @patch("src.azurefunctions.ocrextractinfo.function_app.db_insert")
    def test_storage_trigger_extract(self, mock_db_insert, mock_send_queue_message):
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
            job_type="extract",
            name="testfile.txt",
            uri="https://test/bloburi",
            status="pending",
            created_on=datetime.now(timezone.utc).isoformat(),
        )

        # Assertions
        mock_send_queue_message.assert_called_once_with(expected_blob_info)
        mock_db_insert.assert_called_once_with(expected_blob_info)

    @patch("src.azurefunctions.ocrextractinfo.function_app.BlobInfo.from_json")
    def test_queue_trigger(self, mock_from_json):
        # Mock QueueMessage
        azqueue = Mock()
        azqueue.get_body.return_value = b'{"id": "1234", "job_type": "extract"}'

        # Mock BlobInfo
        blob_info = Mock()
        mock_from_json.return_value = blob_info

        # Call the function
        queue_trigger(azqueue)

        # Assertions
        azqueue.get_body.assert_called_once()
        mock_from_json.assert_called_once_with({"id": "1234", "job_type": "extract"})

if __name__ == "__main__":
    unittest.main()
