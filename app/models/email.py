from datetime import datetime
from pydantic import BaseModel


class Email(BaseModel):
    subject: str
    created_at: datetime
    sender: str
    recipients: list[str]
    body: str
    email_id: int


class Scenario(BaseModel):
    emails: list[Email] = []
    scenario_id: int
    success_criteria: str | None = None
    puzzle_summary: str | None = None
