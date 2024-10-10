import click
from datetime import datetime, timezone
from dpsiw.constants import constants
from dpsiw.services.mgdatabase import MongoDBService


def init_mock_physician_data(clean: bool = False):
    """
    Initialize mock physician data
    """
    repository = MongoDBService(
        collection_name=constants.COLLECTION_PHYSICIANS)
    if clean:
        docs = repository.find_filter({})
        for doc in docs:
            repository.collection.delete_one({'_id': doc['_id']})

    repository.upsert(
        'jmdoe', {'name': 'Jane Marie Doe', 'specialty': 'GP', 'updated': datetime.now(timezone.utc).isoformat()})
    repository.upsert(
        'jsmith', {'name': 'John Smith', 'specialty': 'Cardiology', 'updated': datetime.now(timezone.utc).isoformat()})
    repository.upsert(
        'pstevenson', {'name': 'Pat Stevenson', 'specialty': 'Oncology', 'updated': datetime.now(timezone.utc).isoformat()})

    click.echo(click.style("Physician Data initialized", fg="cyan"))
    docs = repository.find_filter({})
    for doc in docs:
        click.echo(f"    {doc}")

    repository = MongoDBService(collection_name=constants.COLLECTION_TEMPLATES)
    if clean:
        docs = repository.find_filter({})
        for doc in docs:
            repository.collection.delete_one({'_id': doc['_id']})

    GP_TEMPLATE = """You are a medical AI assistant that can help analyze and summarize a transcript recorded during a physician and a patient encounter. Break the analysis and summary into:

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

    CARDIO_TEMPLATE = """You are a medical AI assistant that can help analyze and summarize a transcript recorded during a cardiologist and a patient encounter. Break the analysis and summary into:

History of Present Illness
Family History 
Social History 
Dietary Habits 
Medications 
Cardiac Procedures 
Results 
Assessment and Plan

Rules:
- Do not skip important information in the summary
- Remove the patient's name or any personal information
- Use 'the patient'
- Write in the third person

Output format:
- You must write in paragraphs
"""

    ONCO_TEMPLATE = """You are a medical AI assistant that can help analyze and summarize a transcript recorded during a cardiologist and a patient encounter. Break the analysis and summary into:

History of Present Illness
Family History 
Social History 
Dietary Habits 
Medications 
Cancer Treatment 
Results 
Assessment and Plan

Rules:
- Do not skip important information in the summary
- Remove the patient's name or any personal information
- Use 'the patient'
- Write in the third person

Output format:
- You must write in paragraphs
"""

    repository.upsert(
        'GP', {'prompt': GP_TEMPLATE, 'updated': datetime.now(timezone.utc).isoformat()})
    repository.upsert(
        'Cardiology', {'prompt': CARDIO_TEMPLATE, 'updated': datetime.now(timezone.utc).isoformat()})
    repository.upsert(
        'Oncology', {'prompt': ONCO_TEMPLATE, 'updated': datetime.now(timezone.utc).isoformat()})

    click.echo(click.style("Template Data initialized", fg="cyan"))
    docs = repository.find_filter({})
    for doc in docs:
        click.echo(f"    {doc}")

# repository.collection.delete_one({'_id': doc['_id']})
