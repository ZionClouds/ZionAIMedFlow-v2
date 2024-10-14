import random
import uuid

import click
from dpsiw.constants import constants
from dpsiw.messages.message import DynMessage, LLMOpts, Message, ProductGenerationMD, MedicalNotesMD, SentimentMD
from dpsiw.services.azureservicebus import get_azuresb_instance
from dpsiw.services.settings import get_settings_instance


class MockProducerSB:
    def __init__(self) -> None:
        self.azuresb = get_azuresb_instance()
        self.settings = get_settings_instance()

    async def mock_message_producer(self, n: int = 1):
        if not self.azuresb:
            raise Exception("")
        ctx = 0
        while True:
            id = str(uuid.uuid4())
            random_number = random.randint(1, 1)
            message: Message = None
            match random_number:
                case 1:
                    mock_file = "https://stdipsdevcus.blob.core.windows.net/medical-notes-in/jmdoe-22678c74dc.wav"
                    message = Message(id=id,
                                      pid="jmdoe",
                                      type=constants.MEDICAL_NOTES_AGENT,
                                      metadata=MedicalNotesMD(
                                          file_url=f"{mock_file}",
                                          blob_name="medical-notes-in/jmdoe-22678c74dc.wav",
                                          file_id='22678c74dc'
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
                await self.azuresb.send_message(message.id, message.model_dump_json())
                ctx += 1

            if ctx >= n:
                break

            # sleep(.1)
