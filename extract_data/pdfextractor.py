from abc import ABC, abstractmethod
import base64
import os


from pdf2image import convert_from_path
from pypdf import PdfReader
import pytesseract
from openai import AzureOpenAI

client = AzureOpenAI(azure_endpoint="https://aoaiziorgeus.openai.azure.com",
                     api_key="87f942a7e0ae4f849314eea2ea5527b2", api_version="2024-02-15-preview")


def encode_image(image_path) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def completion(prompt: str = "Transcribe what is on the image.", model: str = 'gpt-4o', base64_image: any = None) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an AI assistant that transcribes what is on the provided image. No prologue or epilogue."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                 }
            ]}
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


class PDFExtractor(ABC):
    def __init__(self, client: None):
        self.client = client

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        pass


class LocalPDFExtractor(PDFExtractor):
    def __init__(self, client=None):
        super().__init__(client)

    def extract_text(self, file_path: str):

        # creating a pdf reader object
        reader = PdfReader(file_path)

        if reader is None or len(reader.pages) == 0:
            return ""

        # printing number of pages in pdf file
        text = []  # Python's string builder
        for page in reader.pages:
            text.append(page.extract_text())

        return ''.join(text)


class AzurePDFExtractor(PDFExtractor):
    def __init__(self, client):
        super().__init__(client)

    def extract_text(self, file_path: str):
        # Read the PDF file
        with open(file_path, "rb") as f:
            poller = self.client.begin_analyze_document(
                "prebuilt-read",
                analyze_request=f,
                content_type="application/octet-stream")
            result = poller.result()

            # Extract text
            lines = []
            for page in result.pages:
                for line in page.lines:
                    lines.append(line.content)

            return ''.join(lines)


class PDFOCRExtractor(PDFExtractor):
    # sudo apt install tesseract-ocr poppler-utils -y
    def __init__(self, client=None):
        super().__init__(client)

    def extract_text(self, file_path: str):
        pages = convert_from_path(file_path, 300)  # 300 DPI
        sb = []
        for page in pages:
            sb.append(pytesseract.image_to_string(page))
        return ''.join(sb)


class OpenAIExtractor(PDFExtractor):
    def __init__(self, client=None):
        super().__init__(client)

    def extract_text(self, file_path: str):
        # Get the file path
        path = os.path.dirname(file_path)
        # Convert the pages to images
        pages = convert_from_path(file_path, 150)  # 300 DPI
        content = []
        for idx, page in enumerate(pages):
            # Save the image
            page.save(f'{path}/temp-{idx}.png')
            # Encode the image to base 64
            base64_image = encode_image(f'{path}/temp-{idx}.png')
            # Get an image description using GPT
            extracted_text = completion(base64_image=base64_image)
            content.append(extracted_text)

        return ''.join(content)
