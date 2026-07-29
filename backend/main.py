from fastapi import FastAPI, UploadFile, File
from solver import solve_cnf

app = FastAPI(title="FV Playground")


@app.get("/")
def health_check() -> dict:
    """Perform a health check on the server."""
    return {"status": "ok"}

@app.post("/file_upload")
async def file_upload(file: UploadFile=File()) -> dict:
    """Accept a file upload and return basic metadata about it.
    
    Parameters:
        - file (UploadFile): The file to be uploaded
    
    Returns: 
        - metadata (dict): JSON with file metadata

            
    """
    contents = await file.read()
    metadata = {
        "file_name": file.filename,
        "file_size": len(contents)
    }

    return metadata

@app.post("/solve")
async def solve(file: UploadFile=File()) -> dict:
    """Accept a DIMACS-CNF file and run a SAT query on it.
    
    Parameters:
        - file (UploadFile): A DIMACS-CNF file containing the SAT problem to be solved.

    Returns:
        - sat_results (dict): A dictionary returning whether the formula is SAT/UNSAT and SAT variable assignment (if applicable).
    """

    contents: bytes = await file.read()
    cnf_contents: str = contents.decode("utf-8")

    sat_results = solve_cnf(cnf_contents)

    return sat_results



