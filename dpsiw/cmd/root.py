
import click
from click_aliases import ClickAliasedGroup

from dpsiw.constants import *
from dpsiw.services import azurequeue
from dpsiw.services.azureblob import AzureBlobContainer
from dpsiw.services.mockdatagenerators import MockGenerator
from dpsiw.services.mockproducer import MockProducer
from dpsiw.services.servicecontainer import ServiceContainer, get_service_container_instance
from dpsiw.services.settings import Settings, get_settings_instance
from dpsiw.services.azurespeech import AzureSTT, TranscribeOpts, Transcriber
from dpsiw.services.filewatcher import watch_folder
from dpsiw.services.mockpysiciandata import init_mock_physician_data
from dpsiw.workers.worker import Worker
from dpsiw.web.server import Server


# region: Dependency Injection
service_container: ServiceContainer = get_service_container_instance()

# Get an instance of the settings
settings: Settings = get_settings_instance()
service_container['settings'] = settings

# Get a queue client and service
queue_client = azurequeue.AzureQueue.get_client(
    queue_name=constants.DIPS_MESSAGES_QUEUE, connection_string=settings.queue_connection_string)
queue_service = azurequeue.AzureQueue(queue_client)
service_container[constants.SERVICE_MESSAGES_QUEUE] = queue_service

# Mock producer
producer = MockProducer(queue_service)
service_container['producer'] = producer
# endregion: Dependency Injection

# region: Commands


@ click.group(cls=ClickAliasedGroup)
def cli():
    logo = """
  _____  _____   _____     _____
 |  __ \|  __ \ / ____|   |_   _|
 | |  | | |__) | (___ ______| |_      __
 | |  | |  ___/ \___ \______| \ \ /\ / /
 | |__| | |     ____) |    _| |\ V  V /
 |_____/|_|    |_____/    |_____\_/\_/
"""
    click.echo(logo)
    click.echo(click.style(
        "Distributed Processing System for Intelligent workloads\n", fg="green"))


def create_table():
    # table_client = TableManager.get_client()
    # table_manager = TableManager(table_client)
    # table_manager.create_table()
    service_container.get('physician_repository').create_table()


@ cli.command(help="Produce mock messages", aliases=['producer'])
@ click.option('--number', '-n', default=1, help='Number of messages to produce')
def produce(number: int):
    click.echo(click.style(f"Producing {number} messages", fg="cyan"))
    # queue_client = azurequeue.AzureQueue.get_client()
    # queue_service = azurequeue.AzureQueue(queue_client)
    # queue_service.mock_message_producer()
    service_container.get('producer').mock_message_producer(number)


@ cli.command(help="Empty the messages queue", aliases=['qclear'])
def queue_clear():
    click.echo(click.style("Emptying the messages queue", fg="cyan"))
    # queue_client = azurequeue.AzureQueue.get_client()
    # queue_service = azurequeue.AzureQueue(queue_client)
    queue_service.empty_queue()
    service_container.get('messages_queue').empty_queue()


@ cli.command(help="Empty the messages queue", aliases=['qcount'])
def queue_count():
    click.echo(click.style("Counting the messages queue", fg="cyan"))
    # queue_client = azurequeue.AzureQueue.get_client()
    # queue_service = azurequeue.AzureQueue(queue_client)
    queue_service.empty_queue()
    service_container.get('messages_queue').count()


@ cli.command(help="Start one or more message processing workers", aliases=['worker'])
@ click.option('--instances', '-i', default=1, help='Number of instances.')
@ click.option('--endless', '-e', is_flag=True, help='Endless loop')
def consume(instances: int = 1, endless: bool = False):
    worker = Worker()
    worker.start(instances, endless=endless)

# @cli.command()
# def agent():
#     click.echo("Web")


@ cli.command(help="Start a file watcher", aliases=['watch'])
@ click.option('--folder', '-f', default='.', help='Path to watch')
def file_watcher(folder: str):
    click.echo(click.style(f"Watching folder {folder}", fg="cyan"))

    def delegate(path):
        click.echo(f"File {path} has been created")
    watch_folder(folder=folder, delegate=delegate)


@ cli.command(help="Start a web server", aliases=['ui'])
@ click.option('--port', '-p', default=8000, help='Port to listen on')
@ click.option('--host', '-h', default='127.0.0.1', help='Host to listen on')
def web(port: int, host: str):
    Server.start(host=host, port=port)


@ cli.command(help="Initialize mock physician and template mock data")
@ click.option('--clean', '-c', is_flag=True, help='Clean the tables')
def init_mock_data(clean: bool):
    click.echo(click.style("Initializing mock data", fg="cyan"))
    init_mock_physician_data(clean)


@ cli.command(help="List processed messages records")
def mt_ls():
    click.echo(click.style("Listing all messages in the table:", fg="cyan"))
    messages = service_container.get('messages_repository').get_all_entities()
    for message in messages:
        print(message)


@ cli.command(help="Delete the messages table")
def mt_rm():
    click.echo(click.style(f"Deleteting records on table messages", fg="cyan"))
    service_container.get('messages_repository').delete_table()


@ cli.command(help="Mock generator of products, stories and transcriptions", aliases=['mdata'])
@ click.option('--type', '-t', default='encounter', help='Can generate mock data [car, analysis, encounter]')
def mock_generator(type: str):
    generator = MockGenerator()
    match type:
        case 'car':
            generator.car_description()
        case 'analysis':
            generator.story_in_spanish()
        case 'encounter':
            generator.physician_patient_encounter()
        case _:
            pass

# @cli.command()
# def recognize_worker():
#     opts = TranscribeOpts(
#         queue_client=azurequeue.AzureQueue.get_client(queue_name='transcripts'),)
#     tts: Transcriber = QueueTranscriber()
#     tts.transcribe(opts)


@ cli.command(help="Mock transcribe a sound file", aliases=['recognize'])
def transcribe():
    opts = TranscribeOpts(
        file_path="/home/alex/github/am8850/zebra/audio/jmdoe-1.wav")
    # tts: Transcriber = MockTranscriber()
    # print(tts.transcribe(opts=opts))
    tts: Transcriber = AzureSTT(settings.speech_key)
    print(tts.transcribe(opts=opts))


def storage_test():
    settings: Settings = service_container.get('settings')
    client = AzureBlobContainer.get_blob_service_client(
        settings.blob_connection_string)
    azure_blob_container = AzureBlobContainer(
        container_name='audio', blob_service_client=client, service_container=service_container)
    azure_blob_container.create_container()
    data = b"Hello, World!"
    azure_blob_container.upload_bytes(data, "hello.txt")
    azure_blob_container.list_blobs()
# endregion: Commands


def main():
    cli()


if __name__ == "__main__":
    main()
