# Copilot Instructions for school-seat-assigner

## Architecture & Boundaries
- **Flask Monolith**: A single-process app running via [app.py](app.py), persisting all state to JSON documents via [engine/io.py](engine/io.py) instead of a database.
- **Domain Logic**: Web routes handle only HTTP routing and Jinja context. All seat assignment constraint logic natively lives inside the OR-Tools SAT solver within [engine/solver.py](engine/solver.py).
- **Data Access**: Always use the canonical read/write wrappers (e.g., `load_layout`, `save_pupils`) in [engine/io.py](engine/io.py) instead of direct file I/O operations.

## Data Models & Assignment Flow
- **Data Flow**: Base configuration sequentially moves from layout grids to pupil parameters to teacher assignment rules, culminating in final seat assignments.
- **References**: Always use system-generated IDs for mapping `seat_id` to `pupil_id`, never raw text names.
- **Legacy Fallbacks**: Native grid setups output `{"width", "height", "seats": [...]}` shapes. Ensure backwards compatibility by continuing to natively parse the older nested `rows` formats inside configurations.
- **Constraints Shapes**:
  - Pupils: Expect dynamic payload properties with nested arrays for preferences (`sit_next_to` or `avoid`) and performance scoring variables (e.g., scale 1-5).
  - Teacher: Captures constraint lists for elements like `keep_apart` and `compatible_pairs`.

## Solver Behavior
- **OR-Tools Constraint Programming**: The previous soft heuristic has been entirely replaced by formal declarative paths in [engine/solver.py](engine/solver.py#L59) utilizing an OR-Tools CP model capped at an 8-second time horizon.
- **Preferences Engine**: `keep_apart` constraints strictly maximize coordinate distance variables. Soft preferences directly adjust objective variables (e.g., `compatible_pairs` functionally reward grouped assignments with `+200`; pupil neighbor preferences provide scalable integer scores).

## UI Conventions
- **Auto-Saving Patterns**: No manual save interface buttons or blocking popups exist contextually. All UI modifications must immediately trigger silent asynchronous updates backward to the server, matching the implementations natively found in [templates/pupils.html](templates/pupils.html) and [templates/teacher.html](templates/teacher.html).
- **No Build Tools**: Standalone HTML templates dynamically utilize embedded vanilla JS and CSS styles. Do not structurally introduce external library bundlers, Webpack, or isolated Node frameworks.
- **API Responses**: Always formally echo standard JSON responses (like `{"status": "success"}`) fulfilling legacy asynchronous client expectations.

## Developer & Execution Workflows
- **Local run**: Start web services natively on [app.py](app.py) to enable immediate debug routing over port 5000.
- **Containerization**: Standard docker-compose setups functionally expose necessary environments natively without environment adjustments.
- **Dependencies**: Keep constraints engines and routing libraries synchronously updated in [requirements.txt](requirements.txt). Confirm functionality iteratively via end-to-end dashboard walkthroughs as no programmatic tests currently validate the constraints structure.