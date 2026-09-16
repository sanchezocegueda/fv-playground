from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles

from solver import solve_cnf

app = FastAPI(title="FV Playground")

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/api/health")
def health_check() -> dict:
    """Perform a health check on the server."""
    return {"status": "ok"}


@app.post("/solve")
async def solve(file: UploadFile=File()) -> dict:
    """Accept a DIMACS-CNF file and run a SAT query on it.

    Parameters:
        - file (UploadFile): A DIMACS-CNF file containing the SAT problem to be solved.

    Returns:
        - sat_results (dict): A dictionary returning whether the formula is SAT/UNSAT and SAT variable assignment (if applicable).
    """

    contents: bytes = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        cnf_contents: str = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 text")

    try:
        sat_results = solve_cnf(cnf_contents)
    except ValueError:
        raise HTTPException(status_code=400, detail="Malformed DIMACS CNF")

    return sat_results


# Mounted last so it doesn't shadow the API routes declared above. No CORS
# middleware is configured: the frontend is served from this same origin.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")



