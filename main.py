import hmac
import os
import threading
import uuid
from collections import OrderedDict
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from agent.coding_agent import AgentLoopLimitError, CodingAgent
from agent.ollama_client import OllamaClient, OllamaConnectionError
from agent.tools import AgentTools
from agent.workspace import Workspace

load_dotenv()

app = FastAPI(title="Ghost Agent", version="0.1.0")
workspace = Workspace(os.getenv("GHOST_WORKSPACE", "./workspace"))
tools = AgentTools(workspace)
model = OllamaClient()
agent = CodingAgent(tools, model)
bearer = HTTPBearer(auto_error=False)
sessions: OrderedDict[str, list[dict]] = OrderedDict()
sessions_lock = threading.Lock()
MAX_SESSIONS = 100


def configured_api_key() -> str | None:
    key = os.getenv("GHOST_AGENT_API_KEY", "").strip()
    if len(key) < 32 or key == "replace-with-a-long-random-token":
        return None
    return key


class ReadRequest(BaseModel):
    path: str = Field(min_length=1, max_length=500)


class WriteRequest(BaseModel):
    path: str = Field(min_length=1, max_length=500)
    content: str = Field(max_length=1_000_000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12_000)
    conversation_id: str | None = Field(default=None, max_length=100)


def require_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> None:
    expected = configured_api_key()
    if expected is None:
        raise HTTPException(
            status_code=503,
            detail="API access is locked. Configure a random GHOST_AGENT_API_KEY of at least 32 characters.",
        )
    supplied = credentials.credentials if credentials else ""
    if not supplied or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="A valid bearer token is required")


@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health():
    return {
        "status": "online",
        "model": model.model,
        "api_key_configured": configured_api_key() is not None,
    }


@app.get("/files")
def list_files(_auth: None = Depends(require_api_key)):
    try:
        return {"files": tools.list_files()}
    except (FileNotFoundError, ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/read")
def read_file(request: ReadRequest, _auth: None = Depends(require_api_key)):
    try:
        return {"path": request.path, "content": tools.read_file(request.path)}
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/write")
def write_file(request: WriteRequest, _auth: None = Depends(require_api_key)):
    try:
        return tools.write_file(request.path, request.content)
    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/chat")
def chat(request: ChatRequest, _auth: None = Depends(require_api_key)):
    conversation_id = request.conversation_id or str(uuid.uuid4())
    with sessions_lock:
        history = list(sessions.get(conversation_id, []))

    try:
        result = agent.respond(request.message, history)
    except OllamaConnectionError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except AgentLoopLimitError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    with sessions_lock:
        sessions[conversation_id] = result["history"]
        sessions.move_to_end(conversation_id)
        while len(sessions) > MAX_SESSIONS:
            sessions.popitem(last=False)

    return {
        "conversation_id": conversation_id,
        "reply": result["reply"],
        "actions": result["actions"],
    }