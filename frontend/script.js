document.getElementById("upload_form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const results = document.getElementById("results");
    results.textContent = "";

    const fileInput = document.getElementById("cnf-file");
    const file = fileInput.files[0];
    if (!file) {
        results.textContent = "Please choose a file to upload.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    let response;
    try {
        response = await fetch("/solve", {
            method: "POST",
            body: formData,
        });
    } catch (err) {
        results.textContent = "Could not reach the solver. Is the server running?";
        return;
    }

    let body;
    try {
        body = await response.json();
    } catch (err) {
        results.textContent = "Received an unexpected response from the solver.";
        return;
    }

    if (!response.ok) {
        results.textContent = `Error: ${body.detail || "unknown error"}`;
        return;
    }

    if (body.sat) {
        const assignment = body.model.join(", ");
        results.textContent = `SAT — satisfying assignment: ${assignment}`;
    } else {
        results.textContent = "UNSAT";
    }
});
