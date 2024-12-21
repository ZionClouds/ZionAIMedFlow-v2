from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
        self.driver.get("http://localhost:3000")  # Replace with your app's URL
        upload_button = self.driver.find_element(By.ID, "upload-button")
        self.assertIsNotNone(upload_button)

    def tearDown(self):
        self.driver.quit()
