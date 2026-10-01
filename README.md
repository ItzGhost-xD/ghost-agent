# Ghost Agent

**A small, local-first coding assistant powered by Ollama.**

Ghost Agent is a FastAPI application with a browser-based chat interface. It
connects to an Ollama model running on the same computer, then lets the model
inspect and edit text files in a configured workspace.

It does not use a hosted model API, so it does not consume hosted API credits.  
Local inference still uses your computer's processor, memory, storage, and
electricity. Model quality and speed depend on the model and your hardware.

> **Status:** Early MVP. Ghost Agent can list, read, create, and replace
> workspace files. It does not run shell commands, install packages, delete
> files, or execute generated code.

## Highlights

- Ollama-compatible local model connection
- Tool-calling agent loop for workspace file operations
- Simple browser chat and file browser
- Workspace path checks and file-size limits
- Credential and private-key file access blocked
- Bearer-token protection for file and chat APIs
- Unit and API tests

## Quick start

The full instructions—including downloading the project from Replit, installing
Ollama, preparing Python, setting the local access token, and troubleshooting—
are in **[GUIDE.md](GUIDE.md)**.

In brief:

1. Install Ollama and Python 3.11 or newer.
2. Download and extract this project.
3. Pull the default model:

   ```sh
   ollama pull qwen2.5-coder:7b
   ```

4. Create a virtual environment, install requirements, and copy
   `.env.example` to `.env`.
5. Put a private random value of at least 32 characters in
   `GHOST_AGENT_API_KEY` in `.env`.
6. Start the app on the same computer as Ollama:

   ```sh
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

7. Open <http://127.0.0.1:8000> and enter that access token.

## Configuration

Copy `.env.example` to `.env` and edit the values:

| Variable | Purpose | Default |
| --- | --- | --- |
| `GHOST_AGENT_API_KEY` | Protects chat and workspace APIs. Use a private random value at least 32 characters long. | Required |
| `GHOST_WORKSPACE` | Directory the agent may inspect and edit. | `./workspace` |
| `OLLAMA_BASE_URL` | Ollama server address reachable from Ghost Agent. | `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | Model tag already downloaded in Ollama. | `qwen2.5-coder:7b` |

By default, file operations stay in `./workspace`. Set `GHOST_WORKSPACE=.` only
if you want the agent to work on the entire current project directory. Back up
important files first; edits are applied directly, without an approval screen.
The `.env` file is excluded from Git and blocked from workspace file operations.

## API

The interactive API reference is available at <http://127.0.0.1:8000/docs>.

| Route | Purpose | Authentication |
| --- | --- | --- |
| `GET /health` | Check server and model configuration | None |
| `GET /files` | List workspace files | Bearer token |
| `POST /read` | Read a workspace text file | Bearer token |
| `POST /write` | Create or replace a workspace text file | Bearer token |
| `POST /api/chat` | Send a message to the coding agent | Bearer token |

## Development

Run tests from the project root:

```sh
python -m pytest
```

## Security and limitations

- Keep Ghost Agent and Ollama on your own computer for the simplest private
  setup.
- The server binds to `127.0.0.1` in the local run command so it is not exposed
  to your network by default.
- Do not expose Ollama's port `11434` directly to the public internet.
- Replit runs on a different computer from yours. Replit's
  `127.0.0.1:11434` is not your computer's Ollama server. Connecting the Replit
  preview to local Ollama requires a separate secure, authenticated network
  path.
- The agent can edit only its configured workspace, but writes happen
  immediately. Review important changes and keep backups.
- Local use avoids hosted model API credits; it does not remove hardware,
  storage, electricity, model-license, or other usage constraints.

## Project layout

```text
agent/                 Workspace tools, Ollama client, and agent loop
static/index.html      Browser chat and workspace file browser
tests/                 Unit and API tests
workspace/             Default directory available to the agent
main.py                FastAPI application
requirements.txt       Python dependencies
.env.example           Local configuration template
DUIDE.md               Detailed setup and operating guide
```

## References

- [Ollama downloads](https://ollama.com/download)
- [Ollama model library: Qwen 2.5 Coder](https://ollama.com/library/qwen2.5-coder)
- [Replit project and file help](https://docs.replit.com/help/projects-and-files)
- [Python downloads](https://www.python.org/downloads/)