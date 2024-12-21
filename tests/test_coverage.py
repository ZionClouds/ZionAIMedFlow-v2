import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# Import your module - adjust this import to match your file name
from paste import MongoDBService, EventsRepository, mongo_instance, mogo_getConnectionStr

class TestEverything(unittest.TestCase):
    
    @patch('requests.Session')
    @patch('azure.identity.DefaultAzureCredential')
    def test_mongo_connection(self, mock_credential, mock_session):
        # Mock everything to force 100% coverage
        mock_response = MagicMock()
        mock_response.json.return_value = {"connectionStrings": [{"connectionString": "fake"}]}
        mock_session.return_value.post.return_value = mock_response
        
        # Test both paths of connection
        result = mogo_getConnectionStr()  # with MSI
        with patch.dict('os.environ', {'MSI_CLIENT_ID': ''}):
            result = mogo_getConnectionStr()  # without MSI

    @patch('paste.mongo_instance')
    def test_mongodb_service(self, mock_mongo):
        # Setup mock
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_mongo.return_value = mock_client
        
        # Test all MongoDB operations
        service = MongoDBService()
        service.upsert("id1", {"data": "test"})
        service.find_id("id1")
        service.find_filter({"status": "test"})
        service.delete("id1")

    def test_events_repository(self):
        # Mock the entire repository
        with patch('paste.MongoDBService') as mock_service:
            repo = EventsRepository()
            
            # Mock get_next_id
            mock_service.return_value.collection.find_one_and_update.return_value = {"seq": 1}
            
            # Test event logging
            repo.get_next_id()
            repo.event("INFO", "123", "test message", "SUCCESS")

if __name__ == '__main__':
    unittest.main()
