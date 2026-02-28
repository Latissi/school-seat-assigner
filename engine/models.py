from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

@dataclass
class Seat:
    id: str
    row_idx: int
    col_idx: int
    group_id: str
    tag: str = "middle" # front, middle, back

@dataclass
class DeskGroup:
    id: str
    seats: List[Seat]

@dataclass
class Row:
    id: str
    groups: List[DeskGroup]

@dataclass
class Layout:
    rows: List[Row]

@dataclass
class Pupil:
    id: str
    name: str

@dataclass
class PupilPreferences:
    sit_next_to: List[str] = field(default_factory=list)
    avoid: List[str] = field(default_factory=list)

@dataclass
class TeacherConstraints:
    front_row: List[str] = field(default_factory=list)
    back_row: List[str] = field(default_factory=list)
    keep_apart: List[List[str]] = field(default_factory=list)
