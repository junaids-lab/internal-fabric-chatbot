from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.core import settings

app = FastAPI(title="RDCCI Internal Fabric Chatbot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/frontend-config")
async def frontend_config() -> dict[str, object]:
    return {
        "tenantId": settings.entra_tenant_id,
        "clientId": settings.entra_frontend_client_id,
        "powerbiScopes": settings.powerbi_delegated_scopes,
    }
