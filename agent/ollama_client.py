import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class OllamaConnectionError(RuntimeError):
    """Raised when the configured Ollama server cannot answer a request."""


class OllamaClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 180,
    ):
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self.timeout = timeout

        parsed = urlsplit(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("OLLAMA_BASE_URL must be an http:// or https:// URL")
        if parsed.username or parsed.password:
            raise ValueError("Put Ollama authentication in a secure proxy, not in OLLAMA_BASE_URL")

    def chat(self, messages: list[dict], tools: list[dict]) -> dict:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "stream": False,
            }
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read(1_000).decode("utf-8", errors="replace")
            raise OllamaConnectionError(
                f"Ollama returned HTTP {error.code}: {detail or 'request failed'}"
            ) from error
        except (URLError, TimeoutError, OSError, json.JSONDecodeError) as error:
            raise OllamaConnectionError(
                "Could not reach Ollama. Check that it is running and OLLAMA_BASE_URL is reachable."
            ) from error

        if not isinstance(result, dict) or not isinstance(result.get("message"), dict):
            raise OllamaConnectionError("Ollama returned an unexpected response")
        return result
