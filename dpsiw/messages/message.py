from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict
import uuid
from pydantic import BaseModel


class LLMOpts(BaseModel):
    endpoint: str | None = ""
    api_key: str | None = ""
    version: str = "2024-02-15-preview"
    type: str = 'azure'
    system_message: str = "You are an AI assistant."
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int | None = None
    stream: bool = False


class SentimentMD(BaseModel):
    content: str | list[str] | None


class TTSMDType(Enum):
    Content = "content"
    File = "file"
    Url = "url"


class MedicalNotesMD(BaseModel):
    type: str = "file"  # content, file, url
    content: str = ""
    file_path: str | None = None
    file_id: str | None = None
    file_url: str | None = None
    blob_name: str | None = None


class TTSMD(BaseModel):
    filePath: str | None = None
    fileUrl: str | None = None
    language: str = 'en-US'


class ProductGenerationMD(BaseModel):
    content: str


class Message(BaseModel):
    id: str = str(uuid.uuid4())
    pid: str = 'jmdoe'
    cid: str | None = None  # correlation ID
    type: str = "transcription"
    metadata: SentimentMD | MedicalNotesMD | ProductGenerationMD | None = None
    llmopts: LLMOpts | None = None
    created: datetime = datetime.now(timezone.utc)


class DynMessage(BaseModel):
    id: str = str(uuid.uuid4())
    cid: str | None = None  # correlation ID
    type: str = "transcription"
    metadata: Dict | None = None
    llmopts: LLMOpts | None = None
    created: datetime = datetime.now(timezone.utc)
