import os
from time import sleep
import uuid

from azure.storage.queue import QueueClient
import azure.cognitiveservices.speech as speechsdk
from dpsiw.services.fileservices import append_text_file, delete_file, get_file_name_and_extension
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from dpsiw.services.settingsservice import get_settings_instance


settings = get_settings_instance()


class AzSpeechHandler:
    def __init__(self, file_path: str = "/home/alex/github/am8850/zebra/audio/jmdoe-20240822-uuid.txt"):
        self.file_path = file_path
        delete_file(self.file_path)

    @staticmethod
    def conversation_transcriber_recognition_canceled_cb(evt: speechsdk.SessionEventArgs):
        print('Canceled event')

    @staticmethod
    def conversation_transcriber_session_stopped_cb(evt: speechsdk.SessionEventArgs):
        print('SessionStopped event')

    def conversation_transcriber_transcribed_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):
        print('TRANSCRIBED:')
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print('\tText={}'.format(evt.result.text))
            print('\tSpeaker ID={}'.format(evt.result.speaker_id))
            append_text_file(
                self.file_path, f"{evt.result.speaker_id}\n{evt.result.text}\n\n")
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(
                evt.result.no_match_details))

    def transcriber(self, evt) -> str:
        print('TRANSCRIBED:')
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print('\tText={}'.format(evt.result.text))
            print('\tSpeaker ID={}'.format(evt.result.speaker_id))
            append_text_file(
                self.file_path, f"{evt.result.speaker_id}\n{evt.result.text}\n\n")
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(
                evt.result.no_match_details))

    def conversation_transcriber_session_started_cb(self, evt: speechsdk.SessionEventArgs):
        print('SessionStarted event')


class TranscribeOpts:
    """
    TranscribeOpts(**kargs): Transcriber options
    Parameters:
        file_path: str | None = None
        queue_client: QueueClient | None = None
        url: str | None = None
        reconrding_language: str = 'en-US'
        output_destination: str = 'file'
    """

    def __init__(self, **kargs) -> None:
        self.file_path: str | None = kargs.get('file_path', None)
        self.queue_client: QueueClient | None = kargs.get('queue_client', None)
        self.url: str | None = kargs.get('url', None)
        self.recording_language: str = kargs.get(
            'reconrding_language', 'en-US')
        self.output_destination: str = kargs.get('output_destination', 'file')

    def __str__(self) -> str:
        return f"TranscribeOpts(file_path={self.file_path}, queue_client={self.queue_client}, url={self.url}, reconrding_language={self.recording_language}, output_destination={self.output_destination})"


class TranscriptionResults:
    def __init__(self, **kargs) -> None:
        self.text: str | None = kargs.get('text', None)
        self.url: str | None = kargs.get('url', None)
        self.file_path: str | None = kargs.get('file_path', None)

    def __str__(self) -> str:
        txt = self.text if self.text else "None"
        txt = txt.replace("\n", " ")
        return f"TranscriptionResults(text={txt}, url={self.url}, file_path={self.file_path})"


class Transcriber:
    def transcribe(self, opts: TranscribeOpts | None = None) -> TranscriptionResults | None:
        pass


class MockTranscriber(Transcriber):
    def transcribe(self, opts: TranscribeOpts | None = None) -> TranscriptionResults | None:
        mock_file_path = opts.file_path[:-4] + ".txt"
        with open(mock_file_path, 'r') as f:
            text = f.read()
        return TranscriptionResults(text=text, file_path=mock_file_path)


class QueueTranscriber(Transcriber):
    def transcribe(self, opts: TranscribeOpts | None = None) -> TranscriptionResults | None:
        if not opts.queue_client:
            raise Exception("Queue client not initialized")
        # properties = opts.queue_client.get_queue_properties()
        # count = properties.approximate_message_count
        # print("Message count: " + str(count))
        # logging.basicConfig(level=logging.INFO)
        print("starting transcriber queue")
        while True:
            messages = opts.queue_client.receive_messages(messages_per_page=5)
            for msg in messages:
                print(f"Consuming message: {msg}")
            sleep(10)


class AzureSTT(Transcriber):
    """
    Azure Speech to text service
    """

    def __init__(self, mock: bool = False) -> None:
        self.mock = mock

    def transcribe(self, opts: TranscribeOpts | None = None) -> str:

        if self.mock:
            # local_folder = os.path.dirname(os.path.abspath(__file__))
            # segments = local_folder.split("/")
            # file = segments[:5] + "/audio/jmdoe-1-mock.txt"

            # # read the file
            # text = ''
            # with open(file, 'r') as f:
            #     text = f.read()
            # TODO: return the text
            return ""

        # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
        if not self.mock:
            # speech_config = speechsdk.SpeechConfig(
            #     subscription=self.speech_key, region=self.service_region)
            speech_config: speechsdk.SpeechConfig = None
            if settings.is_dev:
                speech_config = speechsdk.SpeechConfig(
                    subscription=settings.speech_key, region=settings.speech_region)
            else:
                token_provider = get_bearer_token_provider(
                    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
                authorizationToken = "aad#" + settings.azSpeechResourceId + "#" + token_provider()
                speech_config = speechsdk.SpeechConfig(
                    auth_token=authorizationToken, region=settings.speech_region)

            speech_config.speech_recognition_language = opts.recording_language

            audio_config = speechsdk.audio.AudioConfig(filename=opts.file_path)
            conversation_transcriber = speechsdk.transcription.ConversationTranscriber(
                speech_config=speech_config, audio_config=audio_config)

            transcribing_stop = False

            def stop_cb(evt: speechsdk.SessionEventArgs):
                # """callback that signals to stop continuous recognition upon receiving an event `evt`"""
                print('CLOSING on {}'.format(evt))
                nonlocal transcribing_stop
                transcribing_stop = True

            # Connect callbacks to the events fired by the conversation transcriber
            # conversation_transcriber.transcribed.connect(
            #     conversation_transcriber_transcribed_cb)
            (_, file_ext) = get_file_name_and_extension(opts.file_path)
            # transcription_file_path = opts.file_path.replace(file_ext, ".txt")
            # transcription_file_path = str(uuid.uuid4())[10:] + ".txt"
            transcription_file_path = str(
                uuid.uuid4()).upper().replace("-", '')[:10] + ".txt"
            handler = AzSpeechHandler(transcription_file_path)
            conversation_transcriber.transcribed.connect(
                lambda evt: handler.transcriber(evt))
            conversation_transcriber.session_started.connect(
                handler.conversation_transcriber_session_started_cb)
            conversation_transcriber.session_stopped.connect(
                handler.conversation_transcriber_session_stopped_cb)
            conversation_transcriber.canceled.connect(
                handler.conversation_transcriber_recognition_canceled_cb)

            # stop transcribing on either session stopped or canceled events
            conversation_transcriber.session_stopped.connect(stop_cb)
            conversation_transcriber.canceled.connect(stop_cb)
            conversation_transcriber.start_transcribing_async()

            # Waits for completion.
            while not transcribing_stop:
                sleep(.5)

            conversation_transcriber.stop_transcribing_async()

            return transcription_file_path
        # return TranscriptionResults(text="Transcription complete", file_path=opts.file_path)
