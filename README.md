# Agentic Presentation Builder

A lightweight Flask WebUI that turns a questionnaire into:

- `generation_prompt.txt` with embedded YAML
- `presentation_template.tex` derived from the supplied EMSI/TikZ reference deck
- an Overleaf workspace, a local workspace, or both
- visual compilation instructions

The application does not call an LLM, compile LaTeX, install TeX, or repair PATH. It prepares a reliable hand-off package. After an AI returns `main.tex`, the WebUI can package that file again for Overleaf or local compilation.

## Stack

- Python 3.9+
- Flask + Jinja2
- PyYAML
- Waitress
- Plain HTML, CSS and minimal JavaScript
- Standard-library ZIP generation

No Node.js, npm, database, React, TypeScript, Electron or Tauri.

## Run with a virtual environment

### macOS / Linux

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5500`.

For phone access on the same trusted network, open `http://COMPUTER-LAN-IP:5500`. Do not expose the development service directly to the public internet.

## Run with Docker Compose

```bash
docker compose up --build
```

Open `http://localhost:5500` or the host computer's LAN address from a phone.

The Compose service runs as a non-root user, drops Linux capabilities, uses a read-only filesystem, and keeps temporary exports in a small tmpfs.

## Workflow

1. Fill the six-step questionnaire.
2. Select Overleaf, Local, or Both.
3. Download the generated package.
4. Send `generation_prompt.txt`, `presentation_template.tex`, and assets to an LLM.
5. Save the returned complete source as `main.tex`.
6. Replace the temporary wrapper or use the WebUI's packaging form.
7. Follow the visual Overleaf or local instructions.

## Important EMSI asset note

The uploaded reference contained `\includegraphics{logo}` but did not include the actual EMSI logo file. The generalized template keeps EMSI as permanent branding and uses `assets/logos/emsi-logo.png`; it falls back to a clean `EMSI` text mark until the real asset is added.

## Tests

```bash
python -m unittest discover -s tests -v
```
