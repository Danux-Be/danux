from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.runs import router as runs_router
from app.routes.webhooks import router as webhooks_router
from app.routes.workflows import router as workflows_router

app = FastAPI(title='Danux API', version='0.2.0')

app.include_router(health_router)
app.include_router(workflows_router)
app.include_router(webhooks_router)
app.include_router(runs_router)
