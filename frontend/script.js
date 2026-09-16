function formatLiteral(lit) {
    const v = Math.abs(lit);
    return lit < 0 ? `¬x${v}` : `x${v}`;
}

function parseDimacsPreview(text) {
    const clauses = [];
    let maxVarSeen = 0;

    for (const rawLine of text.split("\n")) {
        const line = rawLine.trim();
        if (!line || line.startsWith("c") || line.startsWith("p")) {
            continue;
        }

        const tokens = line.split(/\s+/).map((t) => parseInt(t, 10)).filter((n) => !Number.isNaN(n));
        if (tokens.length && tokens[tokens.length - 1] === 0) {
            tokens.pop();
        }
        if (!tokens.length) {
            continue;
        }

        clauses.push(tokens);
        for (const lit of tokens) {
            maxVarSeen = Math.max(maxVarSeen, Math.abs(lit));
        }
    }

    if (!clauses.length) {
        return { ok: false };
    }

    return { ok: true, clauses, maxVarSeen };
}

function renderFileInfo(result) {
    const fileInfo = document.getElementById("file-info");
    const message = document.getElementById("file-info-message");
    const stats = document.querySelector("#file-info .stats");
    const preview = document.getElementById("file-info-preview");

    fileInfo.hidden = false;

    if (!result.ok) {
        stats.hidden = true;
        preview.hidden = true;
        message.hidden = false;
        message.textContent = "Couldn't preview this file — it doesn't look like valid DIMACS CNF. You can still click Solve.";
        return;
    }

    message.hidden = true;
    stats.hidden = false;
    preview.hidden = false;

    document.getElementById("file-info-vars").textContent = result.maxVarSeen;
    document.getElementById("file-info-clauses").textContent = result.clauses.length;

    const shown = result.clauses.slice(0, 5).map((clause) => clause.map(formatLiteral).join(" ∨ "));
    if (result.clauses.length > 5) {
        shown.push(`… and ${result.clauses.length - 5} more clause(s)`);
    }
    preview.textContent = shown.join("\n");
}

const fileInput = document.getElementById("cnf-file");
const resultsEl = document.getElementById("results");

fileInput.addEventListener("change", async () => {
    resultsEl.hidden = true;

    const file = fileInput.files[0];
    if (!file) {
        document.getElementById("file-info").hidden = true;
        return;
    }

    let text;
    try {
        text = await file.text();
    } catch (err) {
        renderFileInfo({ ok: false });
        return;
    }

    renderFileInfo(parseDimacsPreview(text));
});

document.getElementById("upload_form").addEventListener("submit", async (e) => {
    e.preventDefault();

    resultsEl.className = "panel";
    resultsEl.textContent = "";
    resultsEl.hidden = true;

    const file = fileInput.files[0];
    if (!file) {
        resultsEl.className = "panel result-error";
        resultsEl.textContent = "Please choose a file to upload.";
        resultsEl.hidden = false;
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
        resultsEl.className = "panel result-error";
        resultsEl.textContent = "Could not reach the solver. Is the server running?";
        resultsEl.hidden = false;
        return;
    }

    let body;
    try {
        body = await response.json();
    } catch (err) {
        resultsEl.className = "panel result-error";
        resultsEl.textContent = "Received an unexpected response from the solver.";
        resultsEl.hidden = false;
        return;
    }

    if (!response.ok) {
        resultsEl.className = "panel result-error";
        resultsEl.textContent = `Error: ${body.detail || "unknown error"}`;
        resultsEl.hidden = false;
        return;
    }

    if (body.sat) {
        resultsEl.className = "panel result-sat";
        const assignment = body.model.map(formatLiteral).join(", ");
        resultsEl.textContent = `SAT — satisfying assignment: ${assignment}`;
    } else {
        resultsEl.className = "panel result-unsat";
        resultsEl.textContent = "UNSAT";
    }
    resultsEl.hidden = false;
});
