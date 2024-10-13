from datetime import datetime, timezone
import uuid
from pydantic import BaseModel


class MedicalNotesMD(BaseModel):
    type: str = "file"  # content, file, url
    content: str = ""
    file_path: str | None = None
    file_id: str | None = None
    file_url: str | None = None
    blob_name: str | None = None


class Message(BaseModel):
    id: str = str(uuid.uuid4())
    type: str = "MedicalNotesAgent"
    metadata: MedicalNotesMD | None = None
    created: datetime = datetime.now(timezone.utc)
