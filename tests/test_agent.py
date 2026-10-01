from agent.coding_agent import CodingAgent
from agent.ollama_client import OllamaClient
from agent.tools import AgentTools
from agent.workspace import Workspace


class FakeModel:
    def __init__(self):
        self.responses = [
            {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "write_file",
                                "arguments": {"path": "hello.py", "content": "print('hello')\n"},
                            }
                        }
                    ],
                }
            },
            {"message": {"role": "assistant", "content": "Created hello.py."}},
        ]

    def chat(self, messages, tools):
        assert tools
        return self.responses.pop(0)


def test_agent_executes_model_file_tool_and_returns_summary(tmp_path):
    workspace = Workspace(str(tmp_path / "workspace"))
    agent = CodingAgent(AgentTools(workspace), FakeModel())

    result = agent.respond("Create a hello world Python file")

    assert workspace.read_file("hello.py") == "print('hello')\n"
    assert result["reply"] == "Created hello.py."
    assert result["actions"] == [
        {"tool": "write_file", "path": "hello.py", "success": True, "error": None}
    ]
    assert len(result["history"]) == 4


def test_ollama_client_uses_native_chat_tool_api(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b'{"message":{"role":"assistant","content":"Ready"}}'

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["payload"] = request.data
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("agent.ollama_client.urlopen", fake_urlopen)
    client = OllamaClient(base_url="http://127.0.0.1:11434", model="test-model")

    result = client.chat([{"role": "user", "content": "hello"}], [{"type": "function"}])

    assert captured["url"] == "http://127.0.0.1:11434/api/chat"
    assert b'"model": "test-model"' in captured["payload"]
    assert b'"stream": false' in captured["payload"]
    assert captured["timeout"] == 180
    assert result["message"]["content"] == "Ready"