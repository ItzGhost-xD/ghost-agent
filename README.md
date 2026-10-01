# Ghost Agent

Ghost Agent is a small coding assistant that uses an Ollama model you run and
control. It can list, read, create, and replace UTF-8 text files in its
workspace. It does not run shell commands, install packages, delete files, or
access paths outside that workspace.

No hosted model API is built in, so Ghost Agent does not consume hosted model
credits. Local inference still uses your computer's CPU/GPU, memory, storage,
and electricity, and model quality depends on the model and hardware.

## Run locally with Ollama

Run Ollama on the same computer as Ghost Agent. Install a coding model once:

```sh
ollama pull qwen2.5-coder:7b
```

Install Python requirements and create a private local environment file:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Replace `GHOST_AGENT_API_KEY` in `.env` with a long, randomly generated value.
For example, generate one locally with:

```sh
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Keep `.env` private; it is excluded from Git. Then start the server on the local
machine only:

```sh
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000>, enter the API access token, and chat. The browser
keeps that token for the current tab session only.

By default, Ghost Agent can only see files under `./workspace`. Put the project
you want it to edit there, or set `GHOST_WORKSPACE` in `.env` to another
directory. Keep the workspace as narrow as practical.

You can choose another model by changing `OLLAMA_MODEL`. Set `OLLAMA_BASE_URL`
if Ollama listens on a different address. The server must be able to reach
that address.

## Replit

The Replit server runs on a different computer from yours. Its
`127.0.0.1:11434` is the Replit environment, not Ollama on your personal
computer. To use the local model with Replit's preview, you would need to
configure a secure, authenticated network path to Ollama. Do not expose the
Ollama port directly to the public internet. The simpler private setup is to
run both Ollama and Ghost Agent locally on your computer.

For a Replit preview, add `GHOST_AGENT_API_KEY` as a Replit Secret before using
the file or chat APIs. Set `OLLAMA_BASE_URL` only to an Ollama endpoint that
the Replit server can securely reach. API routes fail closed when the access
token is not configured.

## Checks

```sh
python -m pytest
```

The interactive API documentation is available at `/docs`.