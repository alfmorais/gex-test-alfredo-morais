from fastapi import FastAPI

from src.lifespan import lifespan
from src.middlewares import correlation_id_middleware
from src.views.routers.webhook import webhook_router

app = FastAPI(lifespan=lifespan, title="Webhook Receiver API", version="1.0.0")
app.include_router(webhook_router)

app.middleware("http")(correlation_id_middleware)
