import os
from pathlib import Path


class Workspace:
    IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
    }
    SENSITIVE_FILENAMES = {
        "id_rsa",
        "id_ed25519",
        "credentials.json",
        "secrets.json",
    }
    MAX_FILE_BYTES = 1_000_000
    MAX_LISTED_FILES = 2_000

    def __init__(self, root: str):
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, path: str) -> Path:
        if not isinstance(path, str) or not path.strip():
            raise ValueError("A non-empty relative path is required")

        candidate = (self.root / path).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise ValueError("Path escapes the workspace")
        return candidate

    @classmethod
    def _is_sensitive(cls, path: Path) -> bool:
        name = path.name.lower()
        if name == ".env":
            return True
        if name in cls.SENSITIVE_FILENAMES:
            return True
        if name.startswith(".env.") and name not in {".env.example", ".env.sample"}:
            return True
        return path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}

    def list_files(self, path: str = ".") -> list[str]:
        directory = self._safe_path(path)
        if not directory.exists():
            raise FileNotFoundError(path)
        if not directory.is_dir():
            raise ValueError(f"{path} is not a directory")

        results: list[str] = []
        for current, directories, files in os.walk(directory):
            directories[:] = sorted(
                name
                for name in directories
                if name not in self.IGNORED_DIRECTORIES and not name.startswith(".")
            )
            for filename in sorted(files):
                item = Path(current) / filename
                if self._is_sensitive(item):
                    continue
                relative = item.relative_to(self.root)
                results.append(relative.as_posix())
                if len(results) >= self.MAX_LISTED_FILES:
                    return results
        return results

    def read_file(self, path: str) -> str:
        file_path = self._safe_path(path)
        if self._is_sensitive(file_path):
            raise ValueError("Access to credential and private-key files is blocked")
        if not file_path.exists():
            raise FileNotFoundError(path)
        if not file_path.is_file():
            raise ValueError(f"{path} is not a file")
        if file_path.stat().st_size > self.MAX_FILE_BYTES:
            raise ValueError(f"File exceeds the {self.MAX_FILE_BYTES}-byte read limit")
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("Only UTF-8 text files can be read") from error

    def write_file(self, path: str, content: str) -> dict[str, object]:
        if not isinstance(content, str):
            raise ValueError("File content must be text")
        if len(content.encode("utf-8")) > self.MAX_FILE_BYTES:
            raise ValueError(f"File exceeds the {self.MAX_FILE_BYTES}-byte write limit")

        file_path = self._safe_path(path)
        if self._is_sensitive(file_path):
            raise ValueError("Writing credential and private-key files is blocked")
        if file_path.exists() and not file_path.is_file():
            raise ValueError(f"{path} is not a file")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return {
            "success": True,
            "path": file_path.relative_to(self.root).as_posix(),
            "bytes_written": len(content.encode("utf-8")),
        }