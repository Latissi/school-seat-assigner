# School Seat Assigner

School Seat Assigner is a Flask web app that helps teachers create seat plans for a class.
It combines classroom layout, teacher rules, and pupil preferences, then computes a seating assignment using OR-Tools (CP-SAT).

## Purpose

The app is built to make seat planning faster and more transparent by:

- modeling a real classroom grid (including teacher desk position),
- capturing teacher constraints (e.g. keep-apart and compatible pairs),
- capturing pupil preferences (sit next to / avoid),
- generating and scoring an assignment automatically.

## Features

- **Class-based workflow**: Create and manage multiple classes under `data/<class_name>/`.
- **Interactive layout editor**: Define rows, columns, available seats, and teacher desk.
- **Pupil management**: Add/remove pupils with first name, last name, and performance level.
- **Preference rules**:
	- Pupil → pupil: `sit_next_to`, `avoid`
	- Teacher: `keep_apart`, `compatible_pairs`
- **Automatic seat assignment**: OR-Tools CP-SAT optimization with an 8-second solve limit.
- **Live updates**: Changes are auto-saved through JSON API endpoints.
- **Result tools**: View score, drag-and-drop swap pupils, and export the seat map as PNG.

## Installation

### Option 1: Local Python setup

Requirements:

- Python 3.12+ (recommended)
- `pip`

Steps:

```bash
git clone https://github.com/Latissi/school-seat-assigner.git
cd school-seat-assigner

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python app.py
```

Open: `http://localhost:5000`

### Option 2: Docker Compose

```bash
git clone https://github.com/Latissi/school-seat-assigner.git
cd school-seat-assigner
docker compose up --build
```

Open: `http://localhost:5000`

Data persists via the mounted `./data` volume.

## How to use

1. Create or open a class from the home page.
2. Define the classroom layout.
3. Add pupils.
4. Add pupil preferences.
5. Add teacher rules.
6. Generate the assignment and adjust manually if needed.

## Screenshots

### Dashboard / Setup

![Dashboard](docs/Screenshot%20from%202026-02-28%2015-05-34.png)

### Rule Editing

![Rule editing](docs/Screenshot%20from%202026-02-28%2015-06-36.png)

### Assignment Result

![Assignment result](docs/Screenshot%20from%202026-02-28%2015-08-12.png)
