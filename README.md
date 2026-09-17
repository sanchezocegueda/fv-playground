# fv-playground

Formal Verification Playground — upload a SAT problem in DIMACS CNF format and get
back SAT/UNSAT plus a satisfying assignment.

**Live demo:** https://sanchezocegueda.github.io/fv-playground/

## How it works

- Upload a `.cnf` file. The page immediately parses it client-side and shows the
  number of variables, number of clauses, and a preview of the first 5 clauses
  (using `x_i` / `¬x_i` notation).
- Click **Solve** to send the file to the backend, which runs it through
  [PySAT](https://pysathq.github.io/)'s Glucose3 solver and returns SAT/UNSAT and,
  if satisfiable, a variable assignment.

## Architecture

| Component | Tech | Hosting |
|---|---|---|
| Frontend | Plain HTML/CSS/JS, no build step | GitHub Pages |
| Backend | FastAPI + PySAT (Glucose3) | Render |

The frontend and backend are deployed to separate origins, so the backend allows
cross-origin requests from the GitHub Pages origin via CORS (see
`backend/main.py`). Locally, the same FastAPI app also serves the frontend
directly (via `StaticFiles`) so everything runs from a single process with no
CORS needed.

## Project structure

```
backend/
  main.py               FastAPI app: /api/health, POST /solve
  solver.py              DIMACS-CNF parsing + solving via PySAT
  requirements.txt       Runtime dependencies
  requirements-dev.txt   + pytest, httpx (for tests)
  sat.cnf, unsat.cnf      Sample DIMACS files for manual testing
  tests/                 pytest unit + API tests
frontend/
  index.html
  script.js               File parsing/preview, fetch("/solve"), result rendering
  style.css
render.yaml               Render Blueprint for the backend
.github/workflows/
  tests.yml               Runs pytest on push/PR
  deploy-pages.yml        Publishes frontend/ to GitHub Pages on push
```

## Running locally

```
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://localhost:8000/ in a browser — the frontend and API are served
from the same process.

Try it against the included fixtures:

```
curl -F "file=@sat.cnf" localhost:8000/solve      # {"sat":true,"model":[...]}
curl -F "file=@unsat.cnf" localhost:8000/solve    # {"sat":false,"model":null}
```

## Running tests

```
cd backend
pip install -r requirements-dev.txt
pytest
```

## Deployment

- **Backend**: deployed to Render as a Blueprint (`render.yaml`), tracking the
  `main` branch. Render's free tier spins down after ~15 minutes of inactivity,
  so the first request after a period of idle time may take 30-60 seconds
  (cold start).
- **Frontend**: deployed to GitHub Pages via `.github/workflows/deploy-pages.yml`
  on every push to `main`.
