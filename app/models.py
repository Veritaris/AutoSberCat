from pydantic.main import BaseModel


class SessionData(BaseModel):
    sbercat_token: str
