import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class SimpleSeleniumTest(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")  # Bypass OS security model
        options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def test_success(self):
        self.driver.get("https://www.zionclouds.com")  # Open any simple website
        print("Test ran successfully!")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
