import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from src.azurefunctions.ocrextractinfo.pgdatabase import BlobInfo, db_insert

class TestPgDatabase(unittest.TestCase):
    def test_blobinfo_to_json(self):
        blob_info = BlobInfo(
            id="1234",
            type="extract",
            blobName="testfile.txt",
            blobURI="https://test/bloburi",
            status="pending",
            ts="2024-12-21T17:17:20.713583+00:00",
        )
        expected_json = {
            "id": "1234",
            "type": "extract",
            "blobName": "testfile.txt",
            "blobURI": "https://test/bloburi",
            "status": "pending",
            "ts": "2024-12-21T17:17:20.713583+00:00",
        }
        self.assertEqual(blob_info.to_json(), expected_json)

    def test_blobinfo_from_json(self):
        json_data = {
            "id": "1234",
            "type": "extract",
            "blobName": "testfile.txt",
            "blobURI": "https://test/bloburi",
            "status": "pending",
            "ts": "2024-12-21T17:17:20.713583+00:00",
        }
        blob_info = BlobInfo.from_json(json_data)
        self.assertEqual(blob_info.id, "1234")
        self.assertEqual(blob_info.type, "extract")
        self.assertEqual(blob_info.blobName, "testfile.txt")
        self.assertEqual(blob_info.blobURI, "https://test/bloburi")
        self.assertEqual(blob_info.status, "pending")
        self.assertEqual(blob_info.ts, "2024-12-21T17:17:20.713583+00:00")

    @patch("src.azurefunctions.ocrextractinfo.pgdatabase.psycopg2.connect")
    def test_db_insert_success(self, mock_connect):
        # Mock the connection and cursor
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        blob_info = BlobInfo(
            id="1234",
            type="extract",
            blobName="testfile.txt",
            blobURI="https://test/bloburi",
            status="pending",
            ts="2024-12-21T17:17:20.713583+00:00",
        )

        db_insert(blob_info)

        # Assertions
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("src.azurefunctions.ocrextractinfo.pgdatabase.psycopg2.connect")
    def test_db_insert_failure(self, mock_connect):
        # Mock connection to raise an error
        mock_connect.side_effect = Exception("Database connection error")

        blob_info = BlobInfo(
            id="1234",
            type="extract",
            blobName="testfile.txt",
            blobURI="https://test/bloburi",
            status="pending",
            ts="2024-12-21T17:17:20.713583+00:00",
        )

        with self.assertLogs(level="ERROR") as log:
            db_insert(blob_info)

        self.assertIn("Error inserting data into the table", log.output[0])

if __name__ == "__main__":
    unittest.main()
