import asyncio
from datetime import datetime, timezone
import uuid

import click
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dpsiw.constants import constants
from dpsiw.exceptions import CompletedException, DeadLetteredException
from dpsiw.services.azureblob import AzureBlobContainer, get_blob_name, get_file_name_and_extension
from dpsiw.services.azurespeech import AzureSTT, TranscribeOpts, Transcriber
from dpsiw.services.fileservices import delete_file, read_text_file
from dpsiw.services.llmservice import LLMService
from dpsiw.services.mgdatabase import MongoDBService, TranscriptionsRepository
from dpsiw.services.settings import Settings, get_settings_instance
from dpsiw.tools.gpttool import GPTMessage



from .agent import Agent
from dpsiw.messages.message import Message, LLMOpts

settings = get_settings_instance()

aoaiclient = None


def get_aoai_client_instance():
    """
    Get the Azure OpenAI client instance
    """
    global aoaiclient
    if aoaiclient is None:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
        aoaiclient = AzureOpenAI(azure_endpoint=settings.endpoint,
                                 azure_ad_token_provider=token_provider,
                                 #api_key=settings.api_key,
                                 api_version=settings.version)
    return aoaiclient


class MedicalNotesAgent(Agent):
    def __init__(self) -> None:
        super().__init__()
        self.message: Message = None
        self.transcript_text: str = ""
        self.specialty: str = "GP"
        self.system_prompt: str = ""
        self.medical_notes: str = ""
        self.blob_container = AzureBlobContainer(
            constants.MEDICAL_NOTES_BLOB_CONTAINER)
        self.blob_name: str = None
        self.file_name: str = None
        self.file_ext: str = None
        self.settings: Settings = get_settings_instance()
        self.physicians_repository = MongoDBService(
            collection_name=constants.COLLECTION_PHYSICIANS)
        self.log_transcription = TranscriptionsRepository()
        self.llm = LLMService(get_aoai_client_instance())

    def produce_notes(self, cid: str, pid: str, file_id: str) -> str:
        self.log_workflow(
            'INFO', cid, 'Calling the LLM to summarize', 'processing')

        llmopts = LLMOpts(
            type="azure",
            temperature=0.1,
            model=self.settings.chat_model,
        )

        messages = [
            GPTMessage(role="system", content=self.system_prompt),
            GPTMessage(role="user", content=self.transcript_text)
        ]

        self.medical_notes = self.llm.completion(llmopts, messages)

        self.log_transcription.insert(
            cid, pid, file_id, self.message.metadata.file_url, self.transcript_text, self.medical_notes, 'processed'
        )

    def pre_validate(self) -> tuple[bool, str]:
        if not self.blob_container.check_blob(self.message.metadata.file_url):
            return (False, "Invalid blob")

        if not self.blob_name or not self.file_name or not self.file_ext:
            return (False, "Invalid blob file name or extension")

        return (True, "")

    def post_validate(self) -> tuple[bool, str]:
        if bool(self.transcript_text) and bool(self.medical_notes):
            return (True, "")
        else:
            return (False, "No content or notes")

    def find_provider_template(self, cid: str, pid: str) -> None:
        """
        Find the physician's specialty and template or set to GP if not found.
        NOTE: Convention, the audio file should carry the physician's id. For example, jmdoe-consultation.wav
        """
        self.log_workflow(
            'INFO', cid, 'Looking for the physician template', 'processing')
        doc = self.physicians_repository.find_id(pid)
        if doc:
            self.specialty = doc.get('specialty', 'GP')
            self.log_workflow(
                'INFO', cid, f'Setting physician template to: {self.specialty}', 'processing')
        else:
            self.specialty = 'GP'
            self.log_workflow(
                'INFO', cid, 'Unable to find the physician template. Setting it to: GP', 'processing')

    def get_blob_information(self):
        self.blob_name = get_blob_name(self.message.metadata.file_url)
        (file_name, file_ext) = get_file_name_and_extension(
            self.message.metadata.file_url)
        self.file_name = file_name
        self.file_ext = file_ext

    @staticmethod
    def get_10_digit_id() -> str:
        """
        Get a 10 digit ID
        """
        return str(uuid.uuid4())[:6]

    def download_blob(self, cid: str) -> str:
        # Download the audio file
        self.log_workflow(
            'INFO',  cid, 'Downloading blob', 'processing')

        file_path = self.blob_container.download_blob_url(
            self.message.metadata.file_url,
            MedicalNotesAgent.get_10_digit_id() + self.file_ext
        )

        if not bool(file_path):
            self.log_workflow(
                'ERROR',  cid, 'error-Unable to download blob', 'failure')
            return  # raise Exception("Unable to download blob")

        return file_path

    def convert_audio_to_text(self, cid: str, pid: str, file_id: str, file_path: str):
        # Transcribe the audio file
        self.log_workflow(
            'INFO',  cid, f'Transcribing file: {file_path}', 'processing')

        transcribed_file = ""
        try:
            opts = TranscribeOpts(
                file_path=file_path)
            # tts: Transcriber = AzureSTT(
            #     self.settings.speech_key, self.settings.speech_region)
            tts: Transcriber = AzureSTT(
                self.settings.azSpeechResourceId, self.settings.speech_region)
            transcribed_file = tts.transcribe(opts=opts)
            self.transcript_text = read_text_file(transcribed_file)

            if not bool(self.transcript_text):
                self.log_workflow(
                    'ERROR',  cid, f'There was no transcrition generated.', 'failure')
                return

            self.log_workflow(
                'INFO',  cid, f'transcription:\n{self.transcript_text}', 'processing')
            self.log_transcription.insert(
                cid, pid, file_id, self.message.metadata.file_url, self.transcript_text, '')
            click.echo(self.transcript_text)
        except Exception as e:
            self.log_workflow(
                'ERROR',  cid, f'unable to transcribe-{e}', 'failure')
            return
        finally:
            # Delete the downloaded file
            delete_file(file_path)
            delete_file(transcribed_file)

    async def process(self, message: Message):

        click.echo(click.style(
            f"{datetime.now().isoformat()} : Received Medical Notes message", fg='yellow'))

        await asyncio.sleep(.1)

        # Receive Message and add logging
        self.message = message

        # Get a processing ID
        cid = self.message.id
        pid = self.message.pid
        file_id = self.message.metadata.file_id

        self.log_workflow(
            'INFO', cid, f'Received Medical notes: {self.message.metadata.file_url}', 'Received')

        if not bool(self.message.metadata.file_url):
            raise CompletedException(
                "the file file_url is required and it was empty.")

        self.get_blob_information()

        # Pre-validate
        (status, err) = self.pre_validate()
        if not status:
            self.log_workflow('ERROR', cid, f'error-{err}', 'failure')
            raise CompletedException('error-Invalid blob')

        self.log_workflow(
            'INFO', cid, f'Medical notes: {self.message.metadata.file_url}', 'processing')

        file_path = self.download_blob(self.message.metadata.file_url)

        self.convert_audio_to_text(cid, pid, file_id, file_path)

        self.find_provider_template(cid, pid)

        self.produce_notes(cid, pid, file_id)

        # Post-validate
        (status, error_message) = self.post_validate()
        if status:
            self.log_workflow(
                'INFO',  cid, f'Medical Notes:\n{self.medical_notes}', 'completed')
            self.log_transcription.insert(
                cid, pid, file_id, self.message.metadata.file_url, self.transcript_text, self.medical_notes, 'completed')
            click.echo(click.style(
                f"{datetime.now(timezone.utc).isoformat()}: Processing Medical notes succesful.", fg='green'), nl=False)
        else:
            self.log_workflow(
                'ERROR',  cid, f'failure-{error_message}', 'failure')
            click.echo(click.style(
                f"{datetime.now(timezone.utc).isoformat()}: Processing Medal notes failure. Please check the logs.", fg='red'), nl=False)

            # NOTE: Decide what to do with the message. Maybe re-process or maybe dead-letter it.
            raise DeadLetteredException(
                "Processing Medal notes failure. Please check the logs.")
