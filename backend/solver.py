
from pysat.formula import CNF
from pysat.solvers import Glucose3


def solve_cnf(cnf_contents: str) -> dict:
    """Parse DIMACS-CNF file contents and then run a SAT query on it.

    Parameters:
        - contents (str): DIMACS-CNF file contents.
    
    Returns: 
        - result (dict): JSON with SAT/UNSAT and SAT variable assignments (if it exists).

    Function that accepts a DIMACS-CNF file and returns a SAT/UNSAT plus SAT variable assignment (if it exists)."""

    formula = CNF()
    formula.from_string(cnf_contents)


    with Glucose3(bootstrap_with=formula) as g:
        sat = g.solve()
        model = g.get_model() if sat else None

    sat_results = {
        "sat": sat,
        "model": model
    }

    return sat_results