import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

class TestPDFApprover(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")  # Bypass OS security model
        options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def test_upload_button_exists(self):
        self.driver.get("http://localhost:5173")  # Ensure this URL matches your running server
        wait = WebDriverWait(self.driver, 10)
        upload_button = wait.until(EC.presence_of_element_located((By.ID, "upload-button")))
        self.assertIsNotNone(upload_button)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
