import { Builder, By, until, WebDriver } from 'selenium-webdriver';
import 'chromedriver';

let driver: WebDriver;

beforeAll(async () => {
  driver = await new Builder().forBrowser('chrome').build();
  await driver.get('http://localhost:5173/'); // Adjust the URL to your local development server
});

afterAll(async () => {
  await driver.quit();
});

describe('App Component', () => {
  test('renders header with title', async () => {
    const headerElement = await driver.findElement(By.css('header h1'));
    const headerText = await headerElement.getText();
    expect(headerText).toBe('PDF Approver');
  });

  test('renders PDF object with correct data attribute', async () => {
    const pdfObject = await driver.findElement(By.css('object[type="application/pdf"]'));
    const dataAttribute = await pdfObject.getAttribute('data');
    expect(dataAttribute).toBe('https://assets.ctfassets.net/l3l0sjr15nav/29D2yYGKlHNm0fB2YM1uW4/8e638080a0603252b1a50f35ae8762fd/Get_Started_With_Smallpdf.pdf');
  });

  test('renders recognized text section', async () => {
    const recognizedTextLabel = await driver.findElement(By.css('aside:first-of-type label'));
    const recognizedText = await recognizedTextLabel.getText();
    expect(recognizedText).toBe('Recognized Text');

    const pageText = await driver.findElement(By.xpath("//span[contains(text(), 'Page: 1')]"));
    expect(pageText).toBeTruthy();
  });

  test('renders approve and review buttons', async () => {
    const approveButton = await driver.findElement(By.xpath("//button[contains(text(), 'Approve')]"));
    expect(approveButton).toBeTruthy();

    const reviewButton = await driver.findElement(By.xpath("//button[contains(text(), 'Review')]"));
    expect(reviewButton).toBeTruthy();
  });

  test('renders footer with text', async () => {
    const footerElement = await driver.findElement(By.css('footer span'));
    const footerText = await footerElement.getText();
    expect(footerText).toBe('Footer');
  });
});