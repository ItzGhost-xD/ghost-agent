import pytest

from agent.tools import AgentTools
from agent.workspace import Workspace


def test_workspace_reads_and_writes_utf8_files(tmp_path):
    workspace = Workspace(str(tmp_path / "workspace"))
    result = workspace.write_file("src/hello.py", "print('héllo')\n")

    assert result == {
        "success": True,
        "path": "src/hello.py",
        "bytes_written": len("print('héllo')\n".encode("utf-8")),
    }
    assert workspace.read_file("src/hello.py") == "print('héllo')\n"


def test_workspace_rejects_path_traversal(tmp_path):
    workspace = Workspace(str(tmp_path / "workspace"))

    with pytest.raises(ValueError, match="escapes"):
        workspace.write_file("../outside.txt", "no")


def test_workspace_does_not_follow_symlink_outside_root(tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace = Workspace(str(workspace_root))
    outside = tmp_path / "outside.txt"
    outside.write_text("private", encoding="utf-8")
    (workspace_root / "external.txt").symlink_to(outside)

    with pytest.raises(ValueError, match="escapes"):
        workspace.read_file("external.txt")


def test_workspace_skips_hidden_and_generated_directories(tmp_path):
    workspace = Workspace(str(tmp_path / "workspace"))
    workspace.write_file("visible.py", "pass")
    workspace.write_file(".git/config", "ignored")
    workspace.write_file("__pycache__/module.pyc", "ignored")
    workspace.write_file("node_modules/pkg/index.js", "ignored")

    assert workspace.list_files() == ["visible.py"]


def test_workspace_blocks_credential_files(tmp_path):
    workspace = Workspace(str(tmp_path / "workspace"))
    (workspace.root / ".env").write_text("SECRET=value", encoding="utf-8")
    workspace.write_file(".env.example", "KEY=replace-me")

    assert workspace.list_files() == [".env.example"]
    with pytest.raises(ValueError, match="credential"):
        workspace.read_file(".env")


def test_workspace_rejects_binary_and_oversized_files(tmp_path):
    workspace = Workspace(str(tmp_path / "workspace"))
    (workspace.root / "binary.bin").write_bytes(b"\xff")
    (workspace.root / "large.txt").write_bytes(b"a" * (workspace.MAX_FILE_BYTES + 1))

    with pytest.raises(ValueError, match="UTF-8"):
        workspace.read_file("binary.bin")
    with pytest.raises(ValueError, match="read limit"):
        workspace.read_file("large.txt")


def test_tools_expose_only_workspace_file_operations(tmp_path):
    tools = AgentTools(Workspace(str(tmp_path / "workspace")))

    assert {item["function"]["name"] for item in tools.schemas()} == {
        "list_files",
        "read_file",
        "write_file",
    }
    assert tools.execute("delete_file", {"path": "anything"}) == {
        "error": "Unknown tool: delete_file"
    }