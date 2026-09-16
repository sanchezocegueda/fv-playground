from pathlib import Path

from fastapi.testclient import TestClient

from main import app

FIXTURES_DIR = Path(__file__).resolve().parent.parent

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_solve_sat_fixture():
    with open(FIXTURES_DIR / "sat.cnf", "rb") as f:
        response = client.post("/solve", files={"file": ("sat.cnf", f, "text/plain")})
    assert response.status_code == 200
    assert response.json()["sat"] is True


def test_solve_unsat_fixture():
    with open(FIXTURES_DIR / "unsat.cnf", "rb") as f:
        response = client.post("/solve", files={"file": ("unsat.cnf", f, "text/plain")})
    assert response.status_code == 200
    assert response.json()["sat"] is False


def test_solve_rejects_empty_file():
    response = client.post("/solve", files={"file": ("empty.cnf", b"", "text/plain")})
    assert response.status_code == 400


def test_solve_rejects_non_utf8_file():
    response = client.post("/solve", files={"file": ("bad.cnf", b"\xff\xfe", "text/plain")})
    assert response.status_code == 400


def test_solve_rejects_malformed_dimacs():
    response = client.post("/solve", files={"file": ("bad.cnf", b"not a cnf file", "text/plain")})
    assert response.status_code == 400
