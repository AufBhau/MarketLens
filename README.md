# MarketLens

Market Intelligence & Strategic Decision Platform.

**Stack:** FastAPI (REST) · React (Vite + TypeScript) · Python analytics · SQLite/Postgres

## Architecture

```
React (web/)  --REST-->  FastAPI (api/)  -->  marketlens/analytics
                                              data/cases/*.yaml
```

In local single-server mode, FastAPI also serves the built React app from `web/dist`.

## Run locally (one command)

```powershell
cd C:\Users\anujs\Desktop\MarketLens
.\run.ps1
```

Open **http://127.0.0.1:8000**

What `run.ps1` does:
1. Builds the React app (`web/dist`)
2. Starts FastAPI, which serves **both** the API and the UI

Skip rebuild if you already built:

```powershell
.\run.ps1 -SkipBuild
```

> Swagger/OpenAPI UI is disabled by default (production-style).

### AI narrative polish (optional)

Uses **Mistral** to polish memo wording only (scores unchanged).

1. Add to `.env`:
```env
MISTRAL_API_KEY=your_key_here
MISTRAL_MODEL=mistral-small-latest
```
2. Restart the app
3. Open a report — memo wording is polished automatically when the key is set

### First-time setup (only once)

```powershell
cd C:\Users\anujs\Desktop\MarketLens
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd web
npm install
cd ..
```

## REST endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health check |
| GET | `/api/cases` | List demo cases |
| POST | `/api/reports/from-case` | Generate from demo |
| POST | `/api/reports/from-brief` | Generate from custom brief |
| POST | `/api/reports/scenarios` | Recompute scenarios |
| POST | `/api/reports/export-pdf` | Download consulting PDF |
| POST | `/api/reports/polish-narrative` | AI polish memo wording only |

## Optional: two-process hot reload (dev only)

Only needed if you want Vite hot reload while editing UI:

```powershell
# terminal 1
uvicorn api.main:app --reload --port 8000

# terminal 2
cd web
npm run dev
```

UI then at http://localhost:5173

## Project layout

```
api/                 FastAPI (API + serves built UI)
marketlens/          Analytics engine + schemas
web/                 React source
data/cases/          Seeded case YAML
run.ps1 / run.bat    One-command local start
```
