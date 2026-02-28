import random
from typing import Dict, Any
from . import io

def assign_seats(class_name: str) -> Dict[str, Any]:
    # Phase 1: load data
    layout_data = io.load_layout(class_name)
    pupils_data = io.load_pupils(class_name)
    teacher_data = io.load_teacher_constraints(class_name)
    
    pupils = {p['id']: p for p in pupils_data.get('pupils', [])}
    pupil_ids = list(pupils.keys())
    
    seats = []
    front_seats = []
    back_seats = []
    
    # Parse layout
    layout_seats = layout_data.get('seats', [])
    
    # Fallback to old format
    if not layout_seats and layout_data.get('rows'):
        for row in layout_data.get('rows', []):
            col = 0
            for group in row.get('groups', []):
                for seat in group.get('seats', []):
                    s_id = seat['id']
                    tag = seat.get('tag', 'middle')
                    layout_seats.append({
                        'id': s_id, 'row_idx': seat.get('row_idx', 0), 'col_idx': col, 'tag': tag
                    })
                    col += 1
                col += 1

    for seat in layout_seats:
        s_id = seat['id']
        seats.append(s_id)
        tag = seat.get('tag', 'middle')
        if tag == 'front':
            front_seats.append(s_id)
        elif tag == 'back':
            back_seats.append(s_id)
                    
    if len(pupil_ids) > len(seats):
        return {"error": "More pupils than available seats!"}

    mapping = {}
    unassigned_pupils = set(pupil_ids)
    available_seats = set(seats)
    available_front_seats = set(front_seats)
    available_back_seats = set(back_seats)

    # 1. Place 'front_row' pupils
    front_req = teacher_data.get('front_row', [])
    for p_id in front_req:
        if p_id in unassigned_pupils:
            if not available_front_seats:
                # Fallback if front seats are full: place anywhere
                seat = random.choice(list(available_seats))
            else:
                seat = random.choice(list(available_front_seats))
                available_front_seats.remove(seat)
                
            mapping[seat] = p_id
            available_seats.remove(seat)
            unassigned_pupils.remove(p_id)

    # 2. Place 'back_row' pupils
    back_req = teacher_data.get('back_row', [])
    for p_id in back_req:
        if p_id in unassigned_pupils:
            if not available_back_seats:
                seat = random.choice(list(available_seats))
            else:
                seat = random.choice(list(available_back_seats))
                available_back_seats.remove(seat)
                
            mapping[seat] = p_id
            available_seats.remove(seat)
            unassigned_pupils.remove(p_id)

    # 3. For 'keep_apart', we ideally parse empty/adjacent logic.
    unassigned_list = list(unassigned_pupils)
    available_seats_list = list(available_seats)
    random.shuffle(unassigned_list)
    for p_id, s_id in zip(unassigned_list, available_seats_list):
        mapping[s_id] = p_id

    # Precompute seat coords
    seat_coords = {s['id']: (s['row_idx'], s['col_idx']) for s in layout_seats}

    def are_neighbors(s1, s2):
        if s1 not in seat_coords or s2 not in seat_coords: return False
        r1, c1 = seat_coords[s1]
        r2, c2 = seat_coords[s2]
        
        # Grid neighbor calculation (left/right or up/down)
        dist = abs(r1 - r2) + abs(c1 - c2)
        return dist == 1

    def calc_score(curr_map):
        score = 0
        reverse_map = {v: k for k, v in curr_map.items()}
        
        # apply teacher keep_apart
        for p1, p2 in teacher_data.get('keep_apart', []):
            if p1 in reverse_map and p2 in reverse_map:
                if are_neighbors(reverse_map[p1], reverse_map[p2]):
                    score -= 1000

        # apply pupil preferences
        for p_id, p in pupils.items():
            if p_id not in reverse_map: continue
            my_seat = reverse_map[p_id]
            for nxt in p.get('sit_next_to', []):
                if nxt in reverse_map and are_neighbors(my_seat, reverse_map[nxt]):
                    score += 10
            for avd in p.get('avoid', []):
                if avd in reverse_map and are_neighbors(my_seat, reverse_map[avd]):
                    score -= 10
        return score

    # Hill climbing to optimize soft constraints
    current_score = calc_score(mapping)
    
    fixed_pupils = set(front_req + back_req)
    swap_candidates = [s for s, p in mapping.items() if p not in fixed_pupils]
    
    # Run simple hill climbing
    for _ in range(1000):
        if len(swap_candidates) < 2:
            break
        s1, s2 = random.sample(swap_candidates, 2)
        
        # swap
        mapping[s1], mapping[s2] = mapping[s2], mapping[s1]
        new_score = calc_score(mapping)
        if new_score >= current_score:
            current_score = new_score
        else:
            # revert
            mapping[s1], mapping[s2] = mapping[s2], mapping[s1]

    return {"mapping": mapping, "score": current_score}
