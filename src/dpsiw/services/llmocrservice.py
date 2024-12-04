from abc import ABC, abstractmethod
import base64
import os
import click
from pdf2image import convert_from_path

from dpsiw.messages.message import LLMOpts
from dpsiw.services.fileservices import delete_file
from dpsiw.services.llmservice import LLMService, get_aoai_client_instance
from dpsiw.services.settingsservice import SettingsService, get_settings_instance
from dpsiw.tools.gpttool import GPTMessage


def encode_image(image_path) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class PDFExtractor(ABC):
    def __init__(self, client: None):
        self.client = client

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        pass

    @abstractmethod
    async def extract_text_async(self, file_path: str) -> str:
        pass


settings: SettingsService = get_settings_instance()


class LLMOCRService(PDFExtractor):
    def __init__(self, client=None):
        super().__init__(client)
        self.llmservice = LLMService(get_aoai_client_instance(is_async=True))

    def extract_text(self, file_path: str, dpi: int = 150):
        pass

    async def extract_text_async(self, file_path: str, dpi: int = 150):

        click.echo(click.style(
            f"\nExtracting text from File: {file_path}", fg="green"))

        # Get the file path
        path = os.path.dirname(file_path)
        if not path:
            path = "."
        # Convert the pages to images
        pages = convert_from_path(file_path, dpi)  # 300 DPI
        content = []
        tmp_file_path = ''
        for idx, page in enumerate(pages):
            try:
                #
                click.echo(click.style(
                    f"Processing page: {idx+1}/{len(pages)}", fg="green"))
                # Save the image
                tmp_file_path = f'{path}/temp-{idx}.png'
                page.save(tmp_file_path, 'PNG')
                # Encode the image to base 64
                base64_image = encode_image(f'{path}/temp-{idx}.png')
                # Get an image description using GPT
                PROMPT = "Transcribe what is on the image."
                messages = [
                    {"role": "system", "content": "You are an AI assistant that transcribes what is on the provided image. No prologue or epilogue."},
                    {"role": "user", "content": [
                        {"type": "text", "text": PROMPT},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"}
                         }
                    ]}
                ]
                opts = LLMOpts()
                extracted_text = await self.llmservice.raw_completion_aio(opts=opts, messages=messages)
                content.append(extracted_text)
            except Exception as e:
                click.echo(click.style(
                    f"Error extracting text from File: {file_path} Page: {idx+1}/{len(pages)} Error: {e}", fg="red"))
            finally:
                if tmp_file_path:
                    delete_file(tmp_file_path)
        extracted_text = ' '.join(content)
        click.echo(click.style(
            f"\nExtracted text from file {file_path}:\n{extracted_text[:100]}", fg="cyan"))

        return extracted_text
