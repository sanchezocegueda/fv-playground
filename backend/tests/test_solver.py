from pathlib import Path

import pytest

from solver import solve_cnf

FIXTURES_DIR = Path(__file__).resolve().parent.parent


def read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text()


def test_sat_fixture_is_satisfiable():
    result = solve_cnf(read_fixture("sat.cnf"))
    assert result["sat"] is True
    assert result["model"]


def test_unsat_fixture_is_unsatisfiable():
    result = solve_cnf(read_fixture("unsat.cnf"))
    assert result["sat"] is False
    assert result["model"] is None


def test_malformed_cnf_raises_value_error():
    with pytest.raises(ValueError):
        solve_cnf("not a cnf file")
