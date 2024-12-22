// FILE: ZionAIMedFlow/src/frontends/pdfapprover/src/App.test.tsx

import { Builder, By, until, WebDriver } from 'selenium-webdriver';
import 'chromedriver';

let driver: WebDriver;

beforeAll(async () => {
  driver = await new Builder().forBrowser('chrome').build();
  await driver.get('http://localhost:3000'); // Adjust the URL to your local development server
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

    const textArea = await driver.findElement(By.css('textarea'));
    const textAreaValue = await textArea.getAttribute('value');
    expect(textAreaValue).toBe('Get Started With Smallpdf');
  });

  test('renders review information section', async () => {
    const reviewInfoLabel = await driver.findElement(By.css('aside:nth-of-type(2) h2'));
    const reviewInfoText = await reviewInfoLabel.getText();
    expect(reviewInfoText).toBe('Review Information');

    const patientNameLabel = await driver.findElement(By.xpath("//label[contains(text(), 'Patient\'s name')]"));
    expect(patientNameLabel).toBeTruthy();

    const dateOfBirthLabel = await driver.findElement(By.xpath("//label[contains(text(), 'Date of bith')]"));
    expect(dateOfBirthLabel).toBeTruthy();

    const providerNameLabel = await driver.findElement(By.xpath("//label[contains(text(), 'Provider\'s name')]"));
    expect(providerNameLabel).toBeTruthy();

    const dateOfServiceLabel = await driver.findElement(By.xpath("//label[contains(text(), 'Date of service')]"));
    expect(dateOfServiceLabel).toBeTruthy();

    const aiNotesLabel = await driver.findElement(By.xpath("//label[contains(text(), 'AI Notes')]"));
    expect(aiNotesLabel).toBeTruthy();
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