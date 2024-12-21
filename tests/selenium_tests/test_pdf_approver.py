# import unittest
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager

# class TestPDFApprover(unittest.TestCase):
#     def setUp(self):
#         options = Options()
#         options.add_argument("--headless")  # Run in headless mode
#         options.add_argument("--no-sandbox")  # Bypass OS security model
#         options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
#         self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#     def test_upload_button_exists(self):
#         self.driver.get("http://localhost:5173")  # Ensure this URL matches your running server
#         wait = WebDriverWait(self.driver, 10)
#         upload_button = wait.until(EC.presence_of_element_located((By.ID, "upload-button")))
#         self.assertIsNotNone(upload_button)

#     def tearDown(self):
#         self.driver.quit()

# if __name__ == "__main__":
#     unittest.main()

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

class TestPDFApproverApp(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get("http://localhost:5173")  # Update URL as needed

    def test_header_exists(self):
        # Check if the header contains the text 'PDF Approver'
        header = self.driver.find_element(By.CSS_SELECTOR, "header h1")
        self.assertEqual(header.text, "PDF Approver")

    def test_pdf_viewer(self):
        # Check if the PDF viewer <object> element exists
        pdf_viewer = self.driver.find_element(By.CSS_SELECTOR, "object[type='application/pdf']")
        self.assertEqual(pdf_viewer.get_attribute("data"), "https://assets.ctfassets.net/l3l0sjr15nav/29D2yYGKlHNm0fB2YM1uW4/8e638080a0603252b1a50f35ae8762fd/Get_Started_With_Smallpdf.pdf")

    def test_recognized_text_section(self):
        # Check if the Recognized Text section exists
        label = self.driver.find_element(By.CSS_SELECTOR, "aside:first-child label")
        self.assertEqual(label.text, "Recognized Text")
        textareas = self.driver.find_elements(By.CSS_SELECTOR, "aside:first-child textarea")
        self.assertGreater(len(textareas), 0)  # Ensure at least one textarea is present

    def test_review_information_section(self):
        # Check if input fields exist in the Review Information section
        patient_name = self.driver.find_element(By.XPATH, "//label[text()=\"Patient's name\"]/following-sibling::input")
        self.assertIsNotNone(patient_name)

        dob = self.driver.find_element(By.XPATH, "//label[text()='Date of bith']/following-sibling::input")
        self.assertEqual(dob.get_attribute("placeholder"), "mm/dd/yyy")

        provider_name = self.driver.find_element(By.XPATH, "//label[text()=\"Provider's name\"]/following-sibling::input")
        self.assertIsNotNone(provider_name)

        dos = self.driver.find_element(By.XPATH, "//label[text()='Date of service']/following-sibling::input")
        self.assertEqual(dos.get_attribute("placeholder"), "mm/dd/yyy")

    def test_buttons(self):
        # Check if Approve and Review buttons are present
        approve_button = self.driver.find_element(By.XPATH, "//button[text()='Approve']")
        review_button = self.driver.find_element(By.XPATH, "//button[text()='Review']")
        self.assertIsNotNone(approve_button)
        self.assertIsNotNone(review_button)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
