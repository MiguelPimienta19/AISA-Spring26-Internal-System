from typing import Dict, TYPE_CHECKING
from app.models.todo import TodoResponse

if TYPE_CHECKING:
    from app.models.email import Email, Scenario

todos_db: Dict[str, TodoResponse] = {}

calendars: Dict[str, dict] = {}

scenarios: Dict[int, "Scenario"] = {}
emails: Dict[int, "Email"] = {}
