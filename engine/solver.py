import math
from typing import Dict, Any
from . import io

def assign_seats(class_name: str) -> Dict[str, Any]:
    # Load all class data
    layout_data = io.load_layout(class_name)
    pupils_data = io.load_pupils(class_name)
    teacher_data = io.load_teacher_constraints(class_name)
    
    return _assign_seats_ortools(layout_data, pupils_data, teacher_data)

def _prepare_data(layout_data, pupils_data, teacher_data):
    pupils = {p['id']: p for p in pupils_data.get('pupils', [])}
    pupil_ids = list(pupils.keys())
    
    seats = []
    
    # Parse layout
    layout_seats = layout_data.get('seats', [])
    layout_width = layout_data.get('width', 10)
    teacher_desk = layout_data.get('teacher_desk', None)
    
    # Fallback to old format
    if not layout_seats and layout_data.get('rows'):
        for row in layout_data.get('rows', []):
            col = 0
            layout_width = max(layout_width, len(row.get('groups', [])) * 2) # Rough approximation
            for group in row.get('groups', []):
                for seat in group.get('seats', []):
                    s_id = seat['id']
                    layout_seats.append({
                        'id': s_id, 'row_idx': seat.get('row_idx', 0), 'col_idx': col
                    })
                    col += 1
                col += 1

    for seat in layout_seats:
        seats.append(seat['id'])
        
    # Standardize teacher coordinates (fallback to center top if unknown)
    teacher_row = -1
    teacher_col = layout_width / 2.0
    if teacher_desk:
        teacher_row = teacher_desk.get('row_idx', -1)
        teacher_col = teacher_desk.get('col_idx', layout_width / 2.0)
        
    # Calculate Distances
    seat_distances = {}
    for seat in layout_seats:
        r = seat.get('row_idx', 0)
        c = seat.get('col_idx', 0)
        dist = math.sqrt((r - teacher_row)**2 + (c - teacher_col)**2)
        seat_distances[seat['id']] = dist
            
    return pupils, pupil_ids, seats, seat_distances, layout_seats


def _assign_seats_ortools(layout_data, pupils_data, teacher_data) -> Dict[str, Any]:
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        return {"error": "OR-Tools is not installed on the server."}
        
    pupils_map, pupil_ids, seats, seat_distances, layout_seats = _prepare_data(layout_data, pupils_data, teacher_data)
    
    if len(pupil_ids) > len(seats):
        return {"error": "More pupils than available seats!"}
        
    if len(pupil_ids) == 0:
        return {"mapping": {}, "score": 0}

    # Precompute seat neighbor pairs
    seat_coords = {s['id']: (s['row_idx'], s['col_idx']) for s in layout_seats}
    neighbor_pairs = []
    
    max_row = max((s['row_idx'] for s in layout_seats), default=0)
    max_col = max((s['col_idx'] for s in layout_seats), default=0)
    
    seat_list = list(seats) # Ensure stable index mapping
    for i in range(len(seat_list)):
        for j in range(i + 1, len(seat_list)):
            s1 = seat_list[i]
            s2 = seat_list[j]
            r1, c1 = seat_coords[s1]
            r2, c2 = seat_coords[s2]
            if abs(r1 - r2) + abs(c1 - c2) == 1:
                neighbor_pairs.append((s1, s2))

    model = cp_model.CpModel()
    
    # 1. Variables X[p][s] boolean
    X = {}
    for p in pupil_ids:
        for s in seats:
            X[(p, s)] = model.NewBoolVar(f'X_{p}_{s}')
            
    # 2. Hard constraints
    # Every pupil gets exactly one seat
    for p in pupil_ids:
        model.AddExactlyOne([X[(p, s)] for s in seats])
        
    # Every seat has AT MOST one pupil
    for s in seats:
        model.AddAtMostOne([X[(p, s)] for p in pupil_ids])
        
    # 3. Objective function variables mapped to flexible penalties
    objective_terms = []
    
    # helper for adjacency variable creation
    def add_adjacency_reward(p1, p2, weight_val, prefix):
        if p1 not in pupil_ids or p2 not in pupil_ids: return
        
        # is_adj is highly true if p1 and p2 are neighbors
        is_adj = model.NewBoolVar(f'{prefix}_{p1}_{p2}')
        
        # For every neighboring seat pair (s1, s2)
        pair_bools = []
        for s1, s2 in neighbor_pairs:
            bp1 = model.NewBoolVar('')
            model.AddBoolAnd([X[(p1, s1)], X[(p2, s2)]]).OnlyEnforceIf(bp1)
            model.AddBoolOr([X[(p1, s1)].Not(), X[(p2, s2)].Not()]).OnlyEnforceIf(bp1.Not())
            pair_bools.append(bp1)
            
            bp2 = model.NewBoolVar('')
            model.AddBoolAnd([X[(p1, s2)], X[(p2, s1)]]).OnlyEnforceIf(bp2)
            model.AddBoolOr([X[(p1, s2)].Not(), X[(p2, s1)].Not()]).OnlyEnforceIf(bp2.Not())
            pair_bools.append(bp2)
            
        if pair_bools:
            model.AddBoolOr(pair_bools).OnlyEnforceIf(is_adj)
            model.AddBoolAnd([b.Not() for b in pair_bools]).OnlyEnforceIf(is_adj.Not())
        else:
            model.Add(is_adj == 0)
        
        objective_terms.append(is_adj * weight_val)
        
    # Keep apart (distance optimization)
    # The larger the mathematical distance, the better.
    ka_idx = 0
    for p1, p2 in teacher_data.get('keep_apart', []):
        if p1 not in pupil_ids or p2 not in pupil_ids: continue
        
        R_1 = model.NewIntVar(0, max_row, f'R1_{ka_idx}')
        C_1 = model.NewIntVar(0, max_col, f'C1_{ka_idx}')
        R_2 = model.NewIntVar(0, max_row, f'R2_{ka_idx}')
        C_2 = model.NewIntVar(0, max_col, f'C2_{ka_idx}')
        
        for s in seats:
            r, c = seat_coords[s]
            model.Add(R_1 == r).OnlyEnforceIf(X[(p1, s)])
            model.Add(C_1 == c).OnlyEnforceIf(X[(p1, s)])
            model.Add(R_2 == r).OnlyEnforceIf(X[(p2, s)])
            model.Add(C_2 == c).OnlyEnforceIf(X[(p2, s)])
            
        R_diff = model.NewIntVar(-max_row, max_row, f'Rdiff_{ka_idx}')
        model.Add(R_diff == R_1 - R_2)
        R_abs = model.NewIntVar(0, max_row, f'Rabs_{ka_idx}')
        model.AddAbsEquality(R_abs, R_diff)
        
        C_diff = model.NewIntVar(-max_col, max_col, f'Cdiff_{ka_idx}')
        model.Add(C_diff == C_1 - C_2)
        C_abs = model.NewIntVar(0, max_col, f'Cabs_{ka_idx}')
        model.AddAbsEquality(C_abs, C_diff)
        
        dist_var = model.NewIntVar(0, max_row + max_col, f'dist_var_{ka_idx}')
        model.Add(dist_var == R_abs + C_abs)
        
        # Maximize the exact distance directly
        objective_terms.append(dist_var * 100)
        ka_idx += 1
        
    # Compatible Pairs
    for p1, p2 in teacher_data.get('compatible_pairs', []):
        add_adjacency_reward(p1, p2, 200, 'comp')
        
    # Pupil Preferences
    for p in pupil_ids:
        for nxt in pupils_map[p].get('sit_next_to', []):
            add_adjacency_reward(p, nxt, 30, 'like')
        for avd in pupils_map[p].get('avoid', []):
            add_adjacency_reward(p, avd, -30, 'dislike')
            
    # Performance-based Distance Calculation
    # Centered scale: performance 3 is neutral, 1-2 prefer close, 4-5 prefer far.
    max_dist = max(seat_distances.values()) if seat_distances else 1.0
    perf_scale = 30

    for p in pupil_ids:
        perf = pupils_map[p].get('performance', 3)
        perf_factor = 3 - perf

        if perf_factor == 0:
            continue
        
        for s in seats:
            dist = seat_distances[s]
            closeness = max_dist - dist
            score = int(perf_factor * closeness * perf_scale)
            if score != 0:
                objective_terms.append(X[(p, s)] * score)
                
    # 4. Solve
    model.Maximize(sum(objective_terms))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 8.0 # Generous timeout for CP-SAT
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        mapping = {}
        for p in pupil_ids:
            for s in seats:
                if solver.Value(X[(p, s)]):
                    mapping[s] = p
                    
        return {"mapping": mapping, "score": int(solver.ObjectiveValue())}
    else:
        return {"error": "Could not find a feasible solution in the time limit."}
