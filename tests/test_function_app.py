import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from azurefunctions import function_app
from azurefunctions.pgdatabase import BlobInfo

class TestFunctionApp(unittest.TestCase):
    @patch("azurefunctions.function_app.send_queue_message")
    @patch("azurefunctions.function_app.db_insert")
    def test_storage_trigger_extract(self, mock_db_insert, mock_send_queue_message):
        # Mock InputStream
        myblob = Mock()
        myblob.name = "testfile.txt"
        myblob.uri = "http://test/bloburi"
        myblob.length = 1024

        # Call the function
        with patch("azurefunctions.function_app.uuid.uuid4", return_value="1234"):
            function_app.StorageTrigger(myblob)

        # Validate BlobInfo
        expected_blob_info = BlobInfo(
            id="1234",
            job_type="extract",
            name="testfile.txt",
            uri="http://test/bloburi",
            status="pending",
            created_on=datetime.now(timezone.utc).isoformat(),
        )

        # Assertions
        mock_send_queue_message.assert_called_once_with(expected_blob_info)
        mock_db_insert.assert_called_once_with(expected_blob_info)

    @patch("azurefunctions.function_app.BlobInfo.from_json")
    def test_queue_trigger(self, mock_from_json):
        # Mock QueueMessage
        azqueue = Mock()
        azqueue.get_body.return_value = b'{"id": "1234", "job_type": "extract"}'

        # Mock BlobInfo
        blob_info = Mock()
        mock_from_json.return_value = blob_info

        # Call the function
        function_app.queue_trigger(azqueue)

        # Assertions
        azqueue.get_body.assert_called_once()
        mock_from_json.assert_called_once_with({"id": "1234", "job_type": "extract"})

if __name__ == "__main__":
    unittest.main()
