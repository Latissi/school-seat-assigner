import json
import os

def get_class_dir(class_name):
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    class_dir = os.path.join(base_dir, class_name)
    os.makedirs(class_dir, exist_ok=True)
    return class_dir

def _load_json(file_path, default=None):
    if not os.path.exists(file_path):
        return default or {}
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def load_layout(class_name):
    class_dir = get_class_dir(class_name)
    return _load_json(os.path.join(class_dir, 'layout.json'), default={"rows": []})

def save_layout(class_name, doc):
    class_dir = get_class_dir(class_name)
    _save_json(os.path.join(class_dir, 'layout.json'), doc)

def load_pupils(class_name):
    class_dir = get_class_dir(class_name)
    return _load_json(os.path.join(class_dir, 'pupils.json'), default={"pupils": []})

def save_pupils(class_name, doc):
    class_dir = get_class_dir(class_name)
    _save_json(os.path.join(class_dir, 'pupils.json'), doc)

def load_teacher_constraints(class_name):
    class_dir = get_class_dir(class_name)
    return _load_json(os.path.join(class_dir, 'teacher.json'), default={"keep_apart": [], "compatible_pairs": []})

def save_teacher_constraints(class_name, doc):
    class_dir = get_class_dir(class_name)
    canonical = {
        "keep_apart": doc.get("keep_apart", []) if isinstance(doc, dict) else [],
        "compatible_pairs": doc.get("compatible_pairs", []) if isinstance(doc, dict) else []
    }
    _save_json(os.path.join(class_dir, 'teacher.json'), canonical)

def load_assignment(class_name):
    class_dir = get_class_dir(class_name)
    return _load_json(os.path.join(class_dir, 'assignment.json'), default={"mapping": {}, "score": 0})

def save_assignment(class_name, doc):
    class_dir = get_class_dir(class_name)
    _save_json(os.path.join(class_dir, 'assignment.json'), doc)
