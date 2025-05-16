from pydantic import BaseModel

class Brand(BaseModel):
    name: str
    description: str | None