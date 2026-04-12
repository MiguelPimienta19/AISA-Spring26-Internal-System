from fastapi import FastAPI

from routes import email_router, scenario_router

app = FastAPI(title="AISA Internal System")
app.include_router(scenario_router)
app.include_router(email_router)
