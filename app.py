import os
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

from engine import io

@app.route('/')
def index():
    classes = []
    if os.path.exists(DATA_DIR):
        classes = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    return render_template('index.html', classes=classes)

@app.route('/class/create', methods=['POST'])
def create_class():
    class_name = request.form.get('class_name')
    if class_name:
        class_dir = os.path.join(DATA_DIR, class_name)
        os.makedirs(class_dir, exist_ok=True)
    return redirect(url_for('index'))

@app.route('/class/<class_name>')
def class_dashboard(class_name):
    return render_template('dashboard.html', class_name=class_name)

@app.route('/class/<class_name>/layout', methods=['GET', 'POST'])
def class_layout(class_name):
    if request.method == 'POST':
        data = request.json
        io.save_layout(class_name, data)
        return jsonify({"status": "success"})
    layout = io.load_layout(class_name)
    return render_template('layout.html', class_name=class_name, layout=layout)

@app.route('/class/<class_name>/pupils', methods=['GET', 'POST'])
def class_pupils(class_name):
    if request.method == 'POST':
        data = request.json
        io.save_pupils(class_name, data)
        return jsonify({"status": "success"})
    pupils = io.load_pupils(class_name)
    return render_template('pupils.html', class_name=class_name, pupils=pupils)

@app.route('/class/<class_name>/teacher', methods=['GET', 'POST'])
def class_teacher(class_name):
    if request.method == 'POST':
        data = request.json
        io.save_teacher_constraints(class_name, data)
        return jsonify({"status": "success"})
    constraints = io.load_teacher_constraints(class_name)
    pupils = io.load_pupils(class_name)
    return render_template('teacher.html', class_name=class_name, constraints=constraints, pupils=pupils)

@app.route('/class/<class_name>/assign', methods=['GET', 'POST'])
def class_assign(class_name):
    from engine import solver
    if request.method == 'POST':
        # Trigger assignment
        result = solver.assign_seats(class_name)
        io.save_assignment(class_name, result)
        return jsonify(result)
        
    assignment = io.load_assignment(class_name)
    layout = io.load_layout(class_name)
    pupils = io.load_pupils(class_name)
    return render_template('result.html', class_name=class_name, assignment=assignment, layout=layout, pupils=pupils)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
