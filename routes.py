from fastapi import APIRouter, HTTPException, status
from models import Email, Scenario


# in-memory stores for now — swap for shared storage layer once the team agrees on one
scenarios: dict[int, Scenario] = {}
emails: dict[int, Email] = {}

scenario_router = APIRouter(prefix="/scenarios", tags=["scenarios"])
email_router = APIRouter(prefix="/emails", tags=["emails"])


@scenario_router.post("", status_code=status.HTTP_201_CREATED)
def create_scenario(scenario: Scenario) -> Scenario:
    if scenario.scenario_id in scenarios:
        raise HTTPException(status.HTTP_409_CONFLICT, f"scenario {scenario.scenario_id} already exists")
    scenarios[scenario.scenario_id] = scenario
    for email in scenario.emails:
        emails[email.email_id] = email
    return scenario


@scenario_router.get("/{scenario_id}")
def get_scenario(scenario_id: int) -> Scenario:
    scenario = scenarios.get(scenario_id)
    if scenario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"scenario {scenario_id} not found")
    return scenario


@scenario_router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(scenario_id: int) -> None:
    scenario = scenarios.pop(scenario_id, None)
    if scenario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"scenario {scenario_id} not found")
    for email in scenario.emails:
        emails.pop(email.email_id, None)


@scenario_router.post("/{scenario_id}/emails", status_code=status.HTTP_201_CREATED)
def add_email_to_scenario(scenario_id: int, email: Email) -> Email:
    scenario = scenarios.get(scenario_id)
    if scenario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"scenario {scenario_id} not found")
    if email.email_id in emails:
        raise HTTPException(status.HTTP_409_CONFLICT, f"email {email.email_id} already exists")
    scenario.emails.append(email)
    emails[email.email_id] = email
    return email


@email_router.get("/{email_id}")
def get_email(email_id: int) -> Email:
    email = emails.get(email_id)
    if email is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"email {email_id} not found")
    return email


@email_router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email(email_id: int) -> None:
    email = emails.pop(email_id, None)
    if email is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"email {email_id} not found")
    for scenario in scenarios.values():
        scenario.emails = [e for e in scenario.emails if e.email_id != email_id]
