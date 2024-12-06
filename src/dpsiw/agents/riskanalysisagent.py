import asyncio
from datetime import datetime
import logging

import click
from dpsiw.constants import constants
from dpsiw.exceptions import CompletedException
from dpsiw.services.azureblob import AzureBlobContainer
from dpsiw.services.fileservices import delete_file
from dpsiw.services.llmocrservice import LLMOCRService
from dpsiw.services.llmservice import LLMService, get_aoai_client_instance
from dpsiw.services.mgdatabase import MongoDBService, OCRLogRepository, TranscriptionsRepository
from dpsiw.services.settingsservice import SettingsService, get_settings_instance
from dpsiw.tools.gpttool import GPTMessage
from .agent import Agent
from dpsiw.messages.message import LLMOpts, Message


class RiskAnalysisAgent(Agent):
    """
    OCR Agent extract text from a PDF by converting each page to an image assuming that PDF docs include both text, images, and written notes. 

    A GPT vision model is required like GPT4o.
    """

    def __init__(self) -> None:
        super().__init__()
        self.message: Message = None
        self.blob_container = AzureBlobContainer(
            constants.RISK_ANALYSIS_BLOB_CONTAINER)
        self.settings: SettingsService = get_settings_instance()
        self.riskanalysis_repository = MongoDBService(
            collection_name=constants.COLLECTION_RISKANALYSIS)
        # self.log_transcription = TranscriptionsRepository()
        self.llm = LLMService(get_aoai_client_instance(is_async=True))
        self.llmservice = LLMService(get_aoai_client_instance(is_async=True))
        self.llmocr = LLMOCRService()
        self.text: str = ""
        self.results: str = ""
        self.log = OCRLogRepository()

    async def process_text_async(self) -> str:
        # self.log_workflow(
        #    'INFO', cid, 'Calling the LLM to summarize', 'processing')

        llmopts = LLMOpts(
            type="azure",
            temperature=0.1,
            model=self.settings.chat_model,
        )

        messages = [
            GPTMessage(role="system", content="""You are an AI agent that can analyze a contract for risks. 
                       
Rules:
- Provide a summary of the contract
- List the identified risks
- No prologue          
"""),
            GPTMessage(role="user", content=self.text)
        ]

        self.results = await self.llm.completion_aio(llmopts, messages)
        click.echo(f"\nOCR Results: {self.results}")

    def analyze(self, llm_service: LLMService) -> None:
        messages: list[GPTMessage] = [
            GPTMessage(role="system",
                       content="You are an AI sentiment analysis system. Given the user input, you should provide a sentiment score between 1 and 10 with 10 being very positive. No epilogue or prologue. Provide the score only. "),
            GPTMessage(role="user", content=self.message.metadata.content)
        ]
        resp = llm_service.completion(self.message.llmopts, messages)
        self.score = int(resp)

    def pre_validate(self) -> tuple[bool, str]:
        return (self.message is not None and self.message.metadata is not None and self.message.metadata.content is not None, "there was no message content to translate")

    def post_validate(self) -> tuple[bool, str]:
        return (self.score != -1, "")

    def save(self) -> None:
        click.echo(
            f"Original Text:\n{self.message.metadata.content}\Sentiment score: {self.score}")

    async def process(self, message: Message):
        # Receiving PDF message
        self.message = message

        click.echo(click.style(
            f"{datetime.now().timestamp()} Processing {self.message.type}", fg='yellow'))
        click.echo(f"{self.message.metadata}")
        self.log.insert(self.message.id, self.message.pid, self.message.cid,
                        self.message.type, self.message.metadata.file_url, self.text, self.results, 'Message received')

        click.echo(f"Blob {self.message.metadata.file_url}")

        self.log.insert(self.message.id, self.message.pid, self.message.cid,
                        self.message.type, self.message.metadata.file_url, self.text, self.results, 'Blob downloading')

        file_path = self.blob_container.download_blob_url(
            self.message.metadata.file_url)

        if not file_path:
            self.log.insert(self.message.id, self.message.pid, self.message.cid,
                            self.message.type, self.message.metadata.file_url, self.text, self.results, 'failure - downloading blob')
            raise CompletedException('error-Invalid blob')

        self.log.insert(self.message.id, self.message.pid, self.message.cid,
                        self.message.type, self.message.metadata.file_url, self.text, self.results, 'Blob downloaded')

        print(f"File path: {file_path}")
        if file_path:

            self.log.insert(self.message.id, self.message.pid, self.message.cid,
                            self.message.type, self.message.metadata.file_url, self.text, self.results, 'processing - OCR')
            self.text = await self.llmocr.extract_text_async(file_path)
            if not self.text:
                if not file_path:
                    self.log.insert(self.message.id, self.message.pid, self.message.cid,
                                    self.message.type, self.message.metadata.file_url, self.text, self.results, 'failure - document OCR - no text')
                    raise CompletedException('error-Invalid blob')

            if self.text:
                self.log.insert(self.message.id, self.message.pid, self.message.cid,
                                self.message.type, self.message.metadata.file_url, self.text, self.results, 'processing - LLM')
                await self.process_text_async()

                if not self.results:
                    self.log.insert(self.message.id, self.message.pid, self.message.cid,
                                    self.message.type, self.message.metadata.file_url, self.text, self.results, 'failure - no LLM results generated')
                else:
                    self.log.insert(self.message.id, self.message.pid, self.message.cid,
                                    self.message.type, self.message.metadata.file_url, self.text, self.results, 'completed')

            delete_file(file_path)
