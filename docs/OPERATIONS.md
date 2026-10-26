# Operations

## Local setup

Python 3.12 and Docker are supported. Copy `.env.example` to `.env`; an OpenAI key is optional.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
uvicorn app.main:app --reload
```

The OpenAPI interface is available at `http://127.0.0.1:8000/docs`. `docker compose up --build` starts the API and Phoenix together. Compose stores the SQLite database in the named `intelligence_data` volume.

## Verification

```powershell
python scripts/verify.py
```

The verifier checks tracked and untracked publishable files for syntax, likely credentials, generated artefacts, ignored local configuration, required documentation, whitespace errors, and the test suite. It does not verify an external OpenAI account, a running Phoenix instance, or the quality of model responses.

For a running API, replay the observability scenario with:

```powershell
.\scripts\run_observability_checks.ps1
```

## Publishing

The publishing helper intentionally operates only when `intelligence-system` is its own Git repository. Create the repository and add its remote once:

```powershell
git init
git branch -M main
git remote add origin https://github.com/<your-account>/intelligence-system.git
```

Install the local quality gate after Git is initialized:

```powershell
python scripts/install_hooks.py
```

```powershell
python scripts/publish.py --preview
python scripts/publish.py
```

The preview validates the project and lists every changed file without modifying Git. The interactive command requires the exact word `PUBLISH`, then stages the listed files, verifies again, commits, and pushes the active branch. It never force-pushes.

Supply `--title` and `--description` to avoid external commit-message generation. Otherwise the script tries `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, and `GROQ_API_KEY` from `.env`, in that order; only the changed-file names and diff are sent to the selected provider.

Before making a repository public, review `git status --short`, `git diff --check`, and every new file. Removing a secret from the working tree does not remove it from Git history.
