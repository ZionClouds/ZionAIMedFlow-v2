import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class TestPDFApprover(unittest.TestCase):
    def setUp(self):
        # Set up ChromeDriver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get("http://localhost:3000")  # Update with the actual URL

    def test_upload_button_exists(self):
        # Test if the upload button exists
        upload_button = self.driver.find_element(By.ID, "upload-button")
        self.assertIsNotNone(upload_button)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
