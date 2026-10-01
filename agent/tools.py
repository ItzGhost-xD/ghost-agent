from .workspace import Workspace


class AgentTools:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    @staticmethod
    def schemas() -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List text files inside the project workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Workspace-relative directory, or . for the root.",
                            }
                        },
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read a UTF-8 text file inside the project workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Workspace-relative file path."}
                        },
                        "required": ["path"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Create or replace a UTF-8 text file inside the project workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Workspace-relative file path."},
                            "content": {"type": "string", "description": "Complete new file contents."},
                        },
                        "required": ["path", "content"],
                        "additionalProperties": False,
                    },
                },
            },
        ]

    def read_file(self, path: str):
        return self.workspace.read_file(path)

    def list_files(self, path: str = "."):
        return self.workspace.list_files(path)

    def write_file(self, path: str, content: str):
        return self.workspace.write_file(path, content)

    def execute(self, name: str, arguments: dict) -> dict:
        if not isinstance(arguments, dict):
            return {"error": "Tool arguments must be an object"}

        try:
            if name == "list_files":
                return {"files": self.workspace.list_files(arguments.get("path", "."))}
            if name == "read_file":
                return {"path": arguments["path"], "content": self.read_file(arguments["path"])}
            if name == "write_file":
                return self.write_file(arguments["path"], arguments["content"])
            return {"error": f"Unknown tool: {name}"}
        except (KeyError, FileNotFoundError, OSError, ValueError) as error:
            return {"error": str(error)}