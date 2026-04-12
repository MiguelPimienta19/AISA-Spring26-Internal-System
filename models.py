from datetime import datetime
from pydantic import BaseModel


#want to use BaseModel because it ensures typesaftey for us and its easy to use.
#it also makes it look like a interface in typescript so nicer to read. 

class Email(BaseModel):
    subject: str
    created_at: datetime
    sender: str
    recipients: list[str]
    body: str
    email_id: int #figured we would want an email id...
    
class Scenario(BaseModel):
    emails: list[Email] = []
    scenario_id: int
    success_criteria: str | None = None
    puzzle_summary: str | None = None
