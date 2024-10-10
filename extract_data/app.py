import os
import sys
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from pdfextractor import LocalPDFExtractor, AzurePDFExtractor, PDFOCRExtractor, OpenAIExtractor

load_dotenv()
endpoint = os.getenv('ENDPOINT')
api_key = os.getenv('API_KEY')
version = os.getenv('VERSION')
model = os.getenv('CHAT_MODEL')
diEndpoint = os.getenv('DI_ENDPOINT')
diKey = os.getenv('DI_API_KEY')

# Azure OpenAI
client = AzureOpenAI(azure_endpoint=endpoint,
                     api_key=api_key,
                     api_version=version)

# Azure Document Intelligence
document_intelligence_client = DocumentIntelligenceClient(
    diEndpoint, AzureKeyCredential(diKey))


script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
file = os.path.join(script_directory, "claim-form.pdf")
file1 = os.path.join(script_directory, "written-claim-form.pdf")
file2 = os.path.join(script_directory, "written-claim-form-2-pages.pdf")


def LLM(promt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": """You are an AI assistant that can extract information from medical claim forms or similar documents.
Rules:
- Identify and extract the name of the patient and the patient's date of birth
- Extract the name of the provider and the date of service

Output in the following JSON format with NO prologue or epilogue:

{
  "patient": "", // Patient's name
  "dob": "", // Patient's date of birth
  "provider": "", // Provider's name
  "dos":"" // Date of service
}"""
        },
        {
            "role": "user",
            "content": promt
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stream=False
    )

    return response.choices[0].message.content


if __name__ == '__main__':
    # extractor = LocalPDFExtractor()
    # print(f"Local PDF Extractor on file: {file}")
    # print(LLM(extractor.extract_text(file)))

    # print(f"OCR PDF Extractor on file: {file1}")
    # extractor = PDFOCRExtractor()
    # text = extractor.extract_text(file1)
    # if text:
    #     print(LLM(text))

    # print(f"Azure PDF Extractor on {file1}")
    # extractor = AzurePDFExtractor(document_intelligence_client)
    # text = extractor.extract_text(file1)
    # print(LLM(text))

    file2 = os.path.join(script_directory, "1418193.pdf")
    extractor = OpenAIExtractor()
    text = extractor.extract_text(file2)
    if text:
        print(LLM(text))
