# Copilot Instructions for school-seat-assigner

## Big picture architecture
- This is a single-process Flask app (`app.py`) with no database; all persistent state is JSON files under `data/<class_name>/`.
- Route handlers are thin: they load/save JSON via `engine/io.py`, render Jinja templates, and only call solver logic from `engine/solver.py` in `/class/<class_name>/assign`.
- UI is mostly server-rendered templates in `templates/` with page-local vanilla JS `fetch` calls back to same Flask endpoints (no frontend build step).
- Assignment flow is: edit layout (`layout.json`) → edit pupils (`pupils.json`) → edit teacher rules (`teacher.json`) → generate assignment (`assignment.json`).

## Core modules and boundaries
- `app.py`: HTTP/API surface and page orchestration. Keep business logic out of routes where possible.
- `engine/io.py`: canonical read/write layer for class JSON documents; always use these helpers instead of direct file I/O from routes/templates.
- `engine/solver.py`: seat assignment heuristic. It expects the JSON structures produced by template pages and returns `{mapping, score}` or `{error}`.
- `engine/models.py`: dataclass definitions for domain concepts; currently informational (solver mostly uses dicts).

## Data contracts used across pages
- `layout.json` default is `{"rows": []}` in IO, but current editor writes `{"width", "height", "seats": [...]}` where each seat has `id,row_idx,col_idx,tag`.
- Solver and result page include compatibility logic for old row/group format (`layout.rows[*].groups[*].seats[*]`); preserve this fallback when changing layout handling.
- `pupils.json` shape: `{"pupils": [{"id","name","sit_next_to":[],"avoid":[]}...]}`.
- `teacher.json` shape: `{"front_row": [], "back_row": [], "keep_apart": [[p1,p2], ...]}`.
- `assignment.json` shape: `{"mapping": {seat_id: pupil_id}, "score": number}`.

## Solver behavior to preserve
- Hard-ish placement phase: tries to place `front_row` and `back_row` pupils first into tagged seats; falls back to any free seat if tagged seats are exhausted.
- Soft optimization phase: hill-climbing swaps non-fixed pupils for 1000 iterations, maximizing score.
- Scoring in `calc_score`: `keep_apart` neighbor violations are `-1000`; pupil `sit_next_to` is `+10`; pupil `avoid` is `-10`.
- Adjacency is Manhattan distance 1 using `row_idx/col_idx`; changing grid semantics impacts all preference scoring.

## Development workflows
- Local run: `python app.py` (Flask debug on `0.0.0.0:5000` in `if __name__ == '__main__'`).
- Container run: `docker compose up` (service `seat-assigner`, port `5000:5000`, repo mounted at `/workspace`).
- Alternative container run mirrors Dockerfile entrypoint: `docker run -p 5000:5000 school-seat-assigner`.
- Dependencies are minimal and pinned in `requirements.txt` (`Flask`, `Werkzeug`, `Jinja2`); no JS package manager/build tooling is used.
- There is currently no test suite in the repo; validate changes by running the app and exercising the class dashboard workflow end-to-end.

## Project-specific coding patterns
- Keep template scripts self-contained per page (see `templates/layout.html`, `templates/pupils.html`, `templates/teacher.html`, `templates/result.html`).
- Keep API responses simple JSON (`{"status":"success"}` or solver payload) because frontend JS assumes these exact shapes.
- For backward compatibility, prefer additive changes over replacing existing keys in persisted JSON.
- Use IDs (not names) as cross-file references for pupils and seats (`assignment.mapping` maps `seat_id -> pupil_id`).
