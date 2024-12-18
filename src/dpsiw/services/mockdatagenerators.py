
import random
import re
import click
from openai import AzureOpenAI, OpenAI


from dpsiw.messages.message import LLMOpts
from dpsiw.services.settingsservice import SettingsService, get_settings_instance
from dpsiw.tools.gpttool import GPTMessage, GPTTool


CAR_DESCRIPION_PROMPT = """Write 10 sentences of random used car data including the year, color, make, model, miles, condition, and price. Randomize models, years, miles and conditions. Generate the sentence only with No prologue.

Example:
1. 2011 silver Nissan Altima with 95,000 miles in good condition for $9,000.
2. 2016 gray Hyundai Elantra with 60,000 miles in excellent condition for $11,500.
"""
SPANISH_STORY_PROMPT = "In three paragraphs, generate a random story in Spanish."

PHYSCIANS_NAMES = [
    {"name": "Dr. Emma Taylor", "specialty": "Cardiology"},
    {"name": "Dr. Michael Patel", "specialty": "Dermatology"},
    {"name": "Dr. Sophia Lee", "specialty": "Endocrinology"},
    {"name": "Dr. David Kim", "specialty": "Gastroenterology"},
    {"name": "Dr. Olivia Brown", "specialty": "Hematology"},
    {"name": "Dr. Ava Morales", "specialty": "Neurology"},
    {"name": "Dr. Ethan Hall", "specialty": "Ophthalmology"},
    {"name": "Dr. Julia Martin", "specialty": "Pediatrics"},
    {"name": "Dr. Liam Chen", "specialty": "Psychiatry"},
    {"name": "Dr. Charlotte Davis", "specialty": "Surgery"}
]

PATIENT_LIST = [
    {"name": "Ryan Thompson", "age": "42", "gender": "male"},
    {"name": "Maya Ramos", "age": "25", "gender": "female"},
    {"name": "Julian Lee", "age": "38", "gender": "male"},
    {"name": "Ava Kim", "age": "29", "gender": "female"},
    {"name": "Michael Brown", "age": "55", "gender": "male"},
    {"name": "Sophia Patel", "age": "32", "gender": "female"},
    {"name": "Daniel Hall", "age": "48", "gender": "male"},
    {"name": "Lauren Taylor", "age": "26", "gender": "female"},
    {"name": "Kevin White", "age": "58", "gender": "male"}
]


PHYSICIAN_PATIENT_ENCOUNTER_PROMPT = """Generate a transcription from a recording for a conversation between <DOCTOR>, <SPECIALTY>, and patient: <PATIENT>, <GENDER> and <AGE> years old. The transcription should include the history of present illness, family history, dietary habits, medications history, physical examination description, results, and treatment plan. 

Transcription example:

Dr: Hello, I am Doctor <LAST_NAME>. How are you feeling today?
Patient: Hello doctor. Today I came in because recently I have been feeling more tired than usual.
Dr. When did you start feeling this way?
Patient: I started feeling this way about a week ago.

Transcription format: '''
Doctor: <FULL NAME>
Patient: <FULL NAME>

Dr: <TEXT> 
Patient: <TEXT>
'''


No prologue. Write the transcription only and don't provide section titles.
"""


class MockGenerator:
    def __init__(self, client: OpenAI | AzureOpenAI = None, settings: SettingsService = None) -> None:
        self.client = client
        self.settings = settings or get_settings_instance()
        if self.client is None:
            self.client = AzureOpenAI(
                azure_endpoint=self.settings.endpoint, api_key=self.settings.api_key, api_version=self.settings.version)
        self.gpt_tool = GPTTool(self.client)

    def car_description(self) -> str:
        opts = LLMOpts(
            model=self.settings.chat_model,
            temperature=0.7,
            max_tokens=1024,
            stream=False
        )
        messages: list[GPTMessage] = [
            GPTMessage(role="user", content=CAR_DESCRIPION_PROMPT)
        ]
        result = self.gpt_tool.completion(opts, messages)
        lines = result.split('\n')
        # random line between 1 and 10
        rnd = random.randint(1, len(lines))
        line = re.sub(r'^\d+\.', '', lines[rnd-1]).strip()
        print(line)
        return line

    def story_in_spanish(self) -> str:
        opts = LLMOpts(
            model=self.settings.chat_model,
            temperature=1,
            max_tokens=1024,
            stream=False
        )
        messages: list[GPTMessage] = [
            GPTMessage(role="user", content=SPANISH_STORY_PROMPT)
        ]
        result = self.gpt_tool.completion(opts, messages)
        click.echo(result)
        return result

    def physician_patient_encounter(self) -> str:
        opts = LLMOpts(
            model=self.settings.chat_model,
            temperature=.3,
            max_tokens=2048,
            stream=False
        )

        dr_idx = random.randint(1, len(PHYSCIANS_NAMES))
        pt_idx = random.randint(1, len(PATIENT_LIST))

        prompt = PHYSICIAN_PATIENT_ENCOUNTER_PROMPT.replace(
            "<DOCTOR>", PHYSCIANS_NAMES[dr_idx-1]["name"]).replace("<PATIENT>", PATIENT_LIST[pt_idx-1]["name"]).replace(
                "<AGE>", PATIENT_LIST[pt_idx-1]["age"]).replace("<GENDER>", PATIENT_LIST[pt_idx-1]["gender"]).replace("<SPECIALTY>", PHYSCIANS_NAMES[dr_idx-1]["specialty"])

        messages: list[GPTMessage] = [
            GPTMessage(role="user", content=prompt)
        ]

        result = self.gpt_tool.completion(opts, messages)
        click.echo(result)
        return result
