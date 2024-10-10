import random
from time import sleep
import uuid

import click
from dpsiw.constants import constants
from dpsiw.messages.message import DynMessage, LLMOpts, Message, ProductGenerationMD, MedicalNotesMD, SentimentMD
from azure.storage.queue import QueueClient

from dpsiw.services.settings import get_settings_instance

ASTRO = '''La luna era un lugar solitario y desolado, sin vida ni sonidos, solo rocas y polvo. Pero un día, un pequeño perro llamado Astro fue enviado allí en una misión espacial. Astro era un perro valiente y curioso, con un pelaje gris y ojos brillantes.
Al principio, Astro se sintió perdido y solo en la luna. No había nadie con quien jugar ni nada que hacer. Pero pronto descubrió que la luna tenía sus propios secretos y maravillas. Podía saltar muy alto debido a la baja gravedad y corría por las llanuras lunares con una velocidad increíble.
Astro hizo amigos con los astronautas que venían a visitar la luna y les mostraba los lugares más increíbles. Les enseñaba a saltar y a correr en la luna y les contaba historias de su vida en la Tierra.
Un día, Astro descubrió un cráter lleno de agua congelada. Era un lugar mágico y Astro decidió hacerlo su hogar. Allí podía correr y jugar sin fin, y los astronautas venían a visitarlo todos los días.
Astro se convirtió en el perro más famoso de la luna y su historia inspiró a muchos otros perros a soñar con aventuras en el espacio. Y aunque la luna seguía siendo un lugar solitario, Astro sabía que nunca estaría solo, porque tenía su hogar en el cráter y sus amigos astronautas que siempre venían a visitarlo.
Espero que disfrutes esta historia. ¡Si necesitas algo más, no dudes en preguntar!'''


class MockProducer:
    def __init__(self, client: QueueClient) -> None:
        self.client = client
        self.settings = get_settings_instance()

    def mock_message_producer(self, n: int = 1):
        if not self.client:
            raise Exception("Queue client not initialized")
        ctx = 0
        while True:
            id = str(uuid.uuid4())
            random_number = random.randint(1, 1)
            message: Message = None
            match random_number:
                case 1:
                    # fileid = uuid.uuid4()
                    # message = Message(id=id, type="Transcription", metadata=TranscriptionMD(
                    #     filePath=f"{id}-{fileid}.wav"))
                    mock_file = "https://stdipsdevcus.blob.core.windows.net/medical-notes-in/jmdoe-4c6eda49cc.wav"
                    message = Message(id=id,
                                      pid="jmdoe",
                                      type=constants.MEDICAL_NOTES_AGENT,
                                      metadata=MedicalNotesMD(
                                          file_url=f"{mock_file}",
                                          blob_name="medical-notes-in/jmdoe-4c6eda49cc.wav",
                                          file_id='4c6eda49cc'
                                      ),
                                      llmopts=LLMOpts(
                                          type="azure",
                                          model="gpt-4o",
                                          temperature=0.1,),
                                      )
                case 2:
                    message = Message(id=id, type="SentimentAnalysis",
                                      metadata=SentimentMD(content="The TriPhone 360 is a game-changing smartphone that has exceeded my expectations in every way, with its stunning display, lightning-fast performance, and revolutionary 360-degree camera making it an absolute pleasure to use! Overall, I'm thoroughly impressed and would highly recommend the TriPhone 360 to anyone looking for a top-notch mobile experience."),
                                      llmopts=LLMOpts(
                                          type="azure",
                                          model="gpt-4o",
                                          endpoint=self.settings.endpoint,
                                          api_key=self.settings.api_key,
                                          version=self.settings.version),
                                      )
                case 3:
                    system_message = "You are an AI product description generator for used automobiles.\nThe user will provide a simple description and you need to generate the most appealing sales description you can to drive sales.\nNo prologue."
                    message = Message(id=id, type="ProductGeneration",
                                      metadata=ProductGenerationMD(
                                          content="2018 Silver Ford Explorer Platinum V6 for USD $20000"),
                                      llmopts=LLMOpts(
                                          type="azure",
                                          model="gpt-4o",
                                          temperature=0.7,
                                          endpoint=self.settings.endpoint,
                                          api_key=self.settings.api_key,
                                          version=self.settings.version,
                                          system_message=system_message),
                                      )
                case 4:
                    message = DynMessage(id=id, type="ProductGeneration",
                                         metadata={"content": "2018 Silver Ford Explorer Platinum V6 for $20000", "price": 20000})
                case _:
                    pass
            if message:
                click.echo(click.style(
                    f"Producing message: ", fg="yellow"), nl=False)
                click.echo(click.style(
                    f"{message.type}", fg="yellow", bold=True))
                click.echo(f"{message}")
                self.client.send_message(message.model_dump_json())
                ctx += 1

            if ctx >= n:
                break

            # sleep(.1)
