import asyncio

import click
from click_aliases import ClickAliasedGroup
from dpsiw.constants import *
from dpsiw.services import azurequeue
from dpsiw.services.azureservicebus import get_azuresb_instance
from dpsiw.services.mgdatabase import MongoDBService
from dpsiw.services.mockdatagenerators import MockGenerator
from dpsiw.services.mockproducersb import MockProducerSB
from dpsiw.services.servicecontainer import ServiceContainer, get_service_container_instance
from dpsiw.services.settings import Settings, get_settings_instance
from dpsiw.services.filewatcher import watch_folder
from dpsiw.services.mockpysiciandata import init_mock_physician_data
from dpsiw.workers.sbworker import WorkerSB
from dpsiw.web.server import Server

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


async def send_async(number):
    click.echo(click.style(f"Producing {number} messages", fg="cyan"))
    producer = MockProducerSB()
    await producer.mock_message_producer(number)
    # await asyncio.sleep(1)


@ cli.command(help="Produce mock messages", aliases=['producer'])
@ click.option('--number', '-n', default=1, help='Number of messages to produce')
def produce(number: int):
    asyncio.run(send_async(number))


async def consume_async(instances: int = 1, endless: bool = False):
    await WorkerSB.start(instances, endless=endless)
    # worker.start(instances, endless=endless)
    # await asyncio.sleep(.1)


@ cli.command(help="Start one or more message consumers (workers)", aliases=['worker'])
@ click.option('--instances', '-i', default=1, help='Number of instances.')
@ click.option('--endless', '-e', is_flag=True, help='Endless loop')
def consume(instances: int = 1, endless: bool = False):
    asyncio.run(consume_async(instances, endless=endless))


async def purge_async():
    click.echo(click.style("Emptying the messages queue", fg="cyan"))
    azuresb = get_azuresb_instance()
    await azuresb.purge()


@ cli.command(help="Empty the messages queue", aliases=['qclear'])
def queue_clear():
    asyncio.run(purge_async())


@ cli.command(help="Empty the messages queue", aliases=['qcount'])
def queue_count():
    click.echo(click.style("Counting the messages queue", fg="cyan"))
    azuresb = get_azuresb_instance()
    azuresb.count_messages()


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
    # messages = service_container.get('messages_repository').get_all_entities()
    # for message in messages:
    #     print(message)
    mongo_service = MongoDBService(
        collection_name=constants.COLLECTION_TRANSCRIPTIONS)
    docs = mongo_service.find_filter({})
    for doc in docs:
        print(doc['_id'], doc['status'], doc['updated'])


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


# @ cli.command(help="Mock transcribe a sound file", aliases=['recognize'])
# def transcribe():
#     opts = TranscribeOpts(
#         file_path="/home/alex/github/am8850/zebra/audio/jmdoe-1.wav")
#     # tts: Transcriber = MockTranscriber()
#     # print(tts.transcribe(opts=opts))
#     tts: Transcriber = AzureSTT(settings.speech_key)
#     print(tts.transcribe(opts=opts))


# endregion: Commands

if __name__ == "__main__":
    cli()
