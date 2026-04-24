from typing import Dict
from app.models.todo import TodoResponse
from app.models.email import Email, Scenario
from app.models.calendar import CalendarResponse

todos_db: Dict[str, TodoResponse] = {}

calendars: Dict[str, CalendarResponse] = {}

scenarios: Dict[int, Scenario] = {}
emails: Dict[int, Email] = {}
