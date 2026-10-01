# GUIDE.md — Detailed Local Setup and Run Guide

This guide takes you from the Replit project to a working local Ghost Agent
that talks to Ollama on the same computer. Follow the section for your operating
system.

## What you will install

- **Ollama** — downloads and runs the local language model.
- **Python 3.11 or newer** — runs the Ghost Agent web application.
- **Ghost Agent project files** — downloaded from Replit as a ZIP archive.
- **A model** — the default is `qwen2.5-coder:7b`.

Ollama's current library lists the 7B model download at about **4.7 GB**. It also
needs memory while running. If your computer is limited or the model is too
slow, try the smaller `qwen2.5-coder:3b` model, currently listed at about
**1.9 GB**. Smaller models are generally less capable.

This setup uses local inference rather than a hosted model API. It avoids
hosted API credits, but still uses your computer's CPU/GPU, memory, storage, and
electricity. Review the license and use terms for the model you choose.

## 1. Download Ghost Agent from Replit

1. Open this Ghost Agent project in Replit.
2. Open the **Files** panel.
3. Select the **three-dot menu** at the top of the file tree.
4. Choose **Download as zip**.
5. Save the ZIP file to your computer, such as the `Downloads` folder.
6. Extract the ZIP into a folder you can find again, for example:
   - Windows: `C:\Users\<your-name>\Projects\ghost-agent`
   - macOS or Linux: `~/Projects/ghost-agent`
7. Open a terminal in the extracted project folder. Confirm that the folder
   contains `main.py`, `requirements.txt`, `agent/`, `static/`, and `tests/`.

If the ZIP contains an extra outer folder, open that folder and work from the
inner folder where `main.py` and `requirements.txt` are located.

### If Replit's ZIP download does not work

Open the Replit Shell and make an archive manually:

```sh
zip -r ghost-agent.zip . \
  -x ".git/*" ".venv/*" ".pythonlibs/*" "__pycache__/*" \
     ".pytest_cache/*" ".cache/*"
```

Then find `ghost-agent.zip` in the Replit file tree, open its menu, and download
it. The ZIP does not contain Replit Secrets. You will create a separate local
`.env` file in a later step; do not copy secrets into the archive.

## 2. Install Ollama

Use Ollama's official download page: <https://ollama.com/download>. Keep Ollama
running while you use Ghost Agent.

### Windows

1. Download the Windows installer from
   <https://ollama.com/download/windows>.
2. Run `OllamaSetup.exe` and complete the installation. The installer normally
   runs Ollama in the background and makes the `ollama` command available in
   PowerShell.
3. Open a **new** PowerShell window.
4. Check that the command works:

   ```powershell
   ollama --version
   ```

Ollama's current Windows requirements include Windows 10 version 22H2 or newer.
The application installs without requiring Administrator privileges. Model
files need additional disk space.

### macOS

1. Ollama currently requires macOS 14 Sonoma or newer.
2. Download the macOS `.dmg` from <https://ollama.com/download>.
3. Open the downloaded disk image.
4. Drag **Ollama** into the **Applications** folder.
5. Open Ollama from **Applications**. If it asks to add its command-line tool
   to your PATH, approve that prompt.
6. Open Terminal and check:

   ```sh
   ollama --version
   ```

Ollama supports Apple silicon with CPU/GPU support and Intel Macs in CPU-only
mode. Model files use additional disk space.

### Linux

1. Open a terminal.
2. Run the official installer:

   ```sh
   curl -fsSL https://ollama.com/install.sh | sh
   ```

3. Check the command:

   ```sh
   ollama --version
   ```

4. If the installer did not start the Ollama service automatically, start it
   and leave that terminal open:

   ```sh
   ollama serve
   ```

If `ollama serve` reports that the address is already in use, Ollama is likely
already running. Do not start a second server.

## 3. Download and test a coding model

In PowerShell or Terminal, download the default model:

```sh
ollama pull qwen2.5-coder:7b
```

This download is several gigabytes. Wait for it to complete, then check that
Ollama has the model:

```sh
ollama list
```

Optionally start an interactive model test:

```sh
ollama run qwen2.5-coder:7b
```

Type a short coding question. When finished, exit the model prompt with:

```text
/bye
```

If you chose the smaller model instead, download it and use the exact same name
in the configuration step:

```sh
ollama pull qwen2.5-coder:3b
```

Ollama serves its local API at `http://127.0.0.1:11434` by default. Ghost Agent
uses this address; both programs need to run on the same computer for this
default to work.

## 4. Install Python

Install Python 3.11 or newer from <https://www.python.org/downloads/>. If Python
is already installed, check its version before continuing.

### Windows

1. Download a Windows installer from Python.org.
2. Run the installer. If you use its command-line launcher, make sure the
   Python Launcher is selected.
3. Open a new PowerShell window and check:

   ```powershell
   py -3 --version
   ```

The result should say Python 3.11 or newer.

### macOS

1. Download the macOS installer from Python.org, or use a Python installation
   you already maintain.
2. Open Terminal and check:

   ```sh
   python3 --version
   ```

The result should say Python 3.11 or newer.

### Linux

1. Check the Python version:

   ```sh
   python3 --version
   ```

2. If it is older than 3.11, install a newer Python version using the
   instructions for your Linux distribution, then check again.

On some Debian/Ubuntu installations, creating a virtual environment may require
the distribution's `python3-venv` package. Install that package only if Python
reports that the `venv` module or `ensurepip` is missing.

## 5. Create a Python environment and install requirements

Run these commands from the project folder containing `requirements.txt`.
They keep this project's Python packages separate from other Python projects.

### Windows PowerShell

These commands use the virtual environment's Python directly, so you do not
need to change PowerShell's script execution policy:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### macOS and Linux

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `pip` reports `externally-managed-environment`, do not install packages into
system Python. Make sure the virtual environment is active and use its Python
to install the requirements:

```sh
python -m pip install -r requirements.txt
```

## 6. Create the local settings file

The project includes `.env.example` as a template. Copy it to a private file
named `.env` in the project root.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
notepad .env
```

### macOS and Linux

```sh
cp .env.example .env
```

Then open `.env` in a text editor.

### Generate the access token

Ghost Agent requires a private API access token at least 32 characters long.
Generate one on your own computer. Do not paste it into chat or commit it to
Git.

**Windows PowerShell:**

```powershell
py -3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**macOS or Linux:**

```sh
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the printed value into `GHOST_AGENT_API_KEY=` in `.env`. Your file should
look like this, with your own generated token after the equals sign:

```dotenv
GHOST_AGENT_API_KEY=your-private-generated-value
GHOST_WORKSPACE=./workspace
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5-coder:7b
```

If you downloaded the smaller model, change the last line to:

```dotenv
OLLAMA_MODEL=qwen2.5-coder:3b
```

Save `.env`. It is excluded from Git. **Do not share the token or add `.env` to
the downloaded project archive.**

## 7. Choose which files Ghost Agent may edit

By default, Ghost Agent can only list, read, and write files under the
`./workspace` directory. This is the safer choice. Put the code you want it to
edit there.

If you want Ghost Agent to edit the extracted project itself, change this line
in `.env`:

```dotenv
GHOST_WORKSPACE=.
```

This gives the agent access to the whole current project directory, subject to
the app's path and credential-file protections. File edits are applied
immediately; there is no review-and-approve step yet. Back up important work
before using the full project as its workspace.

Do not set the workspace to your home directory, entire disk, or a folder
containing projects you do not want modified.

## 8. Start Ghost Agent

First make sure Ollama is running. On Windows and macOS, the Ollama app normally
runs in the background after it is opened. On Linux, use the running service or
leave `ollama serve` open in another terminal.

From the project directory, start the FastAPI server.

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### macOS and Linux

If you activated `.venv` in step 5:

```sh
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

If you did not activate the virtual environment, use:

```sh
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Leave this terminal open while using Ghost Agent. The `127.0.0.1` address keeps
the web server local to your computer.

## 9. Open the app and send a first request

1. Open <http://127.0.0.1:8000> in your browser.
2. Paste the same value you placed in `GHOST_AGENT_API_KEY` into the **API
   access token** box.
3. Select **Save**. The workspace file list should load.
4. Ask Ghost Agent to inspect or change a file in its workspace.
5. Check the file in your editor after the agent responds.

The browser stores the access token in session storage for the current tab
session. The interactive API documentation is at
<http://127.0.0.1:8000/docs>.

To stop Ghost Agent, return to the terminal running Uvicorn and press
**Ctrl+C**. The Ollama app or service can remain open.

## 10. Run the test suite

Run tests from the project root in a separate terminal.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

**macOS or Linux** (with `.venv` active):

```sh
python -m pytest -q
```

## Replit preview versus local use

The Replit workflow runs Ghost Agent on Replit's server. In the Replit
environment, `127.0.0.1` means the Replit server—not your personal computer.
Therefore the default Ollama address works only when you run both Ollama and
Ghost Agent locally.

For the Replit preview, `GHOST_AGENT_API_KEY` must be added as a Replit Secret
and entered in the page. Even after that, the Replit server still cannot reach
Ollama on your computer unless you set up a separate secure, authenticated
network connection. Do not expose Ollama's port `11434` directly to the public
internet. For most personal use, run both programs locally instead.

## Troubleshooting

### `ollama` is not recognized

- Windows: finish the Ollama installer, open a new PowerShell window, then run
  `ollama --version` again.
- macOS: open Ollama from Applications and approve its prompt to install the
  command-line link.
- Linux: rerun the official installer and check the terminal output.

### Ollama connection refused on port 11434

Make sure the Ollama app or service is running. On Linux, start `ollama serve`
in a separate terminal if no service is active. Check the model list:

```sh
ollama list
```

Do not start a second `ollama serve` if one is already using port 11434.

### Model not found

Pull the exact configured model:

```sh
ollama pull qwen2.5-coder:7b
```

Then confirm `OLLAMA_MODEL` in `.env` matches the tag shown by `ollama list`.

### “Could not load files” or “Access token required”

1. Confirm `.env` is named exactly `.env` and is in the project root.
2. Confirm `GHOST_AGENT_API_KEY` has at least 32 characters.
3. Paste the same value in the page and select **Save**.
4. Restart the Ghost Agent server after changing `.env`.

The Replit preview does not read a local `.env` copied to your computer. Add a
separate `GHOST_AGENT_API_KEY` Replit Secret only if you are using the Replit
preview.

### The workspace list is empty

The default workspace is `./workspace`. Put project files there, or set
`GHOST_WORKSPACE` to the intended directory and restart the server. Hidden
folders and common generated folders are omitted from the file list.

### Python says the environment is externally managed

Make sure the virtual environment exists and install through its Python. For
example, on macOS/Linux activate `.venv` first; on Windows use
`.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.

### Port 8000 is already in use

Stop the other process using the port, or start Ghost Agent on another port:

```sh
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

Then open <http://127.0.0.1:8001>.

### The model is slow or the computer runs out of memory

Close other memory-heavy applications or switch to the smaller model:

```sh
ollama pull qwen2.5-coder:3b
```

Set `OLLAMA_MODEL=qwen2.5-coder:3b` in `.env`, restart Ghost Agent, and try
again. The smaller model may give less capable coding results.

## Official references

- [Download Ollama](https://ollama.com/download)
- [Ollama for Windows](https://docs.ollama.com/windows)
- [Ollama for macOS](https://docs.ollama.com/macos)
- [Ollama for Linux](https://docs.ollama.com/linux)
- [Qwen 2.5 Coder model library](https://ollama.com/library/qwen2.5-coder)
- [Download Python](https://www.python.org/downloads/)
- [Replit: download or export a project](https://docs.replit.com/help/projects-and-files)