from datetime import datetime, timezone

import click
from openai import AzureOpenAI
from dpsiw.constants import constants
from dpsiw.exceptions import CompletedException
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
        aoaiclient = AzureOpenAI(azure_endpoint=settings.endpoint,
                                 api_key=settings.api_key,
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
        self.llmopts: LLMOpts = None

    def get_system_prompt(self):
        # TODO: based on the specialty, get the system prompt
        #         match self.specialty:
        #             case "GP":
        #                 self.system_prompt = """You are a medical AI assistant that can help analyze and summarize a transcript recorded during a physician and a patient encounter. Break the analysis and summary into:

        # History of Present illness
        # Family History
        # Social History
        # Dietary Habits
        # Medications
        # Procedure
        # Results
        # Assessment and plan

        # Rules:
        # - Do not skip important information in the summary
        # - Remove the patient's name or any personal information
        # - Use 'the patient'
        # - Write in the third person

        # Output format:
        # - You must write in paragraphs
        # """
        #             case _:
        #                 self.system_prompt = "Please provide the medical notes for this patient"

        self.system_prompt = """You are a medical AI assistant that can help analyze and summarize a transcript recorded during a physician and a patient encounter. Break the analysis and summary into:

History of Present illness
Family History
Social History
Dietary Habits
Medications
Procedure
Results
Assessment and plan

Rules:
- Do not skip important information in the summary
- Remove the patient's name or any personal information
- Use 'the patient'
- Write in the third person

Output format:
- You must write in paragraphs
"""

    def produce_notes(self, llm: LLMService) -> str:
        messages: list[GPTMessage] = [
            GPTMessage(role="system",
                       content=self.system_prompt),
            GPTMessage(role="user", content=self.transcript_text)
        ]
        self.medical_notes = llm.completion(self.llmopts, messages)

    def pre_validate(self) -> tuple[bool, str]:
        if not bool(self.message.metadata.file_url):
            return (False, "No file_path was provided")

        if not self.blob_container.check_blob(self.message.metadata.file_url):
            return (False, "Invalid blob")

        if not bool(self.blob_name) or not bool(self.file_name) or not bool(self.file_ext):
            return (False, "Invalid blob file namd or ext")

        return (True, "")

    def post_validate(self) -> tuple[bool, str]:
        if bool(self.transcript_text) and bool(self.medical_notes):
            return (True, "")
        else:
            return (False, "No content or notes")

    def process(self, message: Message):

        # Get a processing ID
        cid = message.id
        pid = message.pid
        file_id = message.metadata.file_id

        # Receive Message and add logging
        self.message = message

        click.echo(click.style(
            f"{datetime.now().isoformat()} : Processing Medical Notes", fg='yellow'))
        click.echo(f"{self.message}")
        self.log_workflow(
            'INFO', cid, f'Medical notes: {self.message.metadata.file_url}', 'processing')

        if not bool(self.message.metadata.file_url):
            raise CompletedException("No file_path was provided")

        # Get the blob name, file name and extension
        self.blob_name = get_blob_name(self.message.metadata.file_url)
        (file_name, file_ext) = get_file_name_and_extension(
            self.message.metadata.file_url)
        self.file_name = file_name
        self.file_ext = file_ext

        # Pre-validate
        (status, err) = self.pre_validate()
        if not status:
            self.log_workflow('ERROR', cid, f'error-{err}', 'failure')
            return
        self.log_transcription.insert(
            cid, pid, file_id, self.message.metadata.file_url, '', '')

        # Find the physician's specialty and template or set to GP if not found
        # NOTE: Convetion, the audio file should carry the physician's id. For example, jmdoe-consultation.wav
        self.log_workflow(
            'INFO',  cid, 'Looking for the physician template', 'processing')
        doc = self.physicians_repository.find_id(pid)
        if doc:
            self.specialty = doc['specialty']
            self.log_workflow(
                'INFO',  cid, f'Setting physician template to: {self.specialty}', 'processing')
        else:
            self.specialty = 'GP'
            self.log_workflow(
                'INFO',  cid, f'Unable to find the physician template. Setting it to: GP', 'processing')
        self.get_system_prompt()

        # Download the audio file
        self.log_workflow(
            'INFO',  cid, 'Downloading blob', 'processing')

        file_path = self.blob_container.download_blob_url(
            self.message.metadata.file_url)

        if not bool(file_path):
            self.log_workflow(
                'ERROR',  cid, 'error-Unable to download blob', 'failure')
            return  # raise Exception("Unable to download blob")

        # Transcribe the audio file
        self.log_workflow(
            'INFO',  cid, f'Transcribing file: {file_path}', 'processing')

        transcribed_file = ""
        try:
            opts = TranscribeOpts(
                file_path=file_path)
            tts: Transcriber = AzureSTT(
                self.settings.speech_key, self.settings.speech_region)
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

        llm = LLMService(get_aoai_client_instance())
        self.llmopts = LLMOpts(
            type="azure",
            temperature=0.1,
            model=self.settings.chat_model,
        )
        self.produce_notes(llm)

        (status, error_message) = self.post_validate()
        if status:
            self.log_workflow(
                'INFO',  cid, f'Medical Notes:\n{self.medical_notes}', 'completed')
            self.log_transcription.insert(
                cid, pid, file_id, self.message.metadata.file_url, self.transcript_text, self.medical_notes, 'completed')
            click.echo(click.style(
                f"{datetime.now(timezone.utc).isoformat()}: Medical notes completed ", fg='green'), nl=False)
        else:
            self.log_workflow(
                'ERROR',  cid, f'failure-{error_message}', 'failure')
            click.echo(click.style(
                f"{datetime.now(timezone.utc).isoformat()} failure ", fg='red'), nl=False)

            # raise Exception("Unable to download blob")
