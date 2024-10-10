from pydantic import BaseModel


class Metadata(BaseModel):
    template: str = "general"
