import re

# 1. Update layout.html
with open('templates/layout.html', 'r', encoding='utf-8') as f:
    layout_content = f.read()

css_addition = """
.classroom-wrapper {
    display: inline-flex;
    flex-direction: column;
    align-items: stretch;
}
.tool-option {
    display: block;
    margin-bottom: 0.5em;
}
.tool-option input[type="radio"] {
    display: none;
}
.tool-option .btn-surface {
    padding: 0.5em 1em;
    border: 2px solid #ccc;
    border-radius: 4px;
    background: #fff;
    cursor: pointer;
    transition: all 0.2s;
    color: #333;
    display: block;
}
.tool-option input[type="radio"]:checked + .btn-surface {
    border-color: #00acc1;
    background: #e0f7fa;
    color: #007c8a;
    font-weight: bold;
    box-shadow: 0 0 5px rgba(0, 172, 193, 0.4);
}
.tool-group-title {
    font-size: 0.85em;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 0.5em;
    margin-top: 1em;
    letter-spacing: 0.5px;
}
</style>
"""
layout_content = layout_content.replace('</style>', css_addition)

main_area_old = """    <h2><i class="fa-solid fa-border-all"></i> Layout Editor: {{ class_name }}</h2>
    <div class="teacher-desk"><i class="fa-solid fa-person-chalkboard"></i> FRONT OF CLASSROOM / TEACHER DESK</div>
    <div id="grid-container"></div>"""

main_area_new = """    <h2><i class="fa-solid fa-border-all"></i> Layout Editor: {{ class_name }}</h2>
    <div class="classroom-wrapper">
      <div class="teacher-desk"><i class="fa-solid fa-person-chalkboard"></i> FRONT OF CLASSROOM / TEACHER DESK</div>
      <div id="grid-container"></div>
    </div>"""
layout_content = layout_content.replace(main_area_old, main_area_new)

tools_old = """      <h3><i class="fa-solid fa-paint-roller"></i> Paint Tool</h3>
      <label><input type="radio" name="tool" value="toggle_seat" checked> <i class="fa-solid fa-chair"></i> Toggle Seat</label><br>
      <label><input type="radio" name="tool" value="tag_front"> <i class="fa-solid fa-arrow-up"></i> Mark Front Row</label><br>
      <label><input type="radio" name="tool" value="tag_back"> <i class="fa-solid fa-arrow-down"></i> Mark Back Row</label><br>
      <label><input type="radio" name="tool" value="tag_middle"> <i class="fa-solid fa-left-right"></i> Mark Middle (Default)</label><br>"""

tools_new = """      <h3><i class="fa-solid fa-pen-ruler"></i> Edit Mode</h3>
      <div class="tool-group-title" style="margin-top: 0;">Placement</div>
      <label class="tool-option"><input type="radio" name="tool" value="toggle_seat" checked> <span class="btn-surface"><i class="fa-solid fa-plus-minus"></i> Add / Remove Seat</span></label>
      
      <div class="tool-group-title">Seat Tags</div>
      <label class="tool-option"><input type="radio" name="tool" value="tag_front"> <span class="btn-surface"><i class="fa-solid fa-arrow-up"></i> Mark Front Row</span></label>
      <label class="tool-option"><input type="radio" name="tool" value="tag_back"> <span class="btn-surface"><i class="fa-solid fa-arrow-down"></i> Mark Back Row</span></label>
      <label class="tool-option"><input type="radio" name="tool" value="tag_middle"> <span class="btn-surface"><i class="fa-solid fa-left-right"></i> Mark Middle (Standard)</span></label>"""
layout_content = layout_content.replace(tools_old, tools_new)

with open('templates/layout.html', 'w', encoding='utf-8') as f:
    f.write(layout_content)

# 2. Update result.html
with open('templates/result.html', 'r', encoding='utf-8') as f:
    result_content = f.read()

result_css_addition = """
.classroom-wrapper {
    display: inline-flex;
    flex-direction: column;
    align-items: stretch;
}
.layout-editor {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    flex-wrap: nowrap;
    overflow-x: auto;
}
.layout-main {
    flex: 1 1 auto;
    min-width: 0;
}
.layout-tools {
    flex: 0 0 320px;
}
</style>
"""
result_content = result_content.replace('</style>', result_css_addition)

flex_two_old = """<div class="flex two">
    <div class="three-fourth">
        <div class="teacher-desk"><i class="fa-solid fa-person-chalkboard"></i> FRONT OF CLASSROOM / TEACHER DESK</div>
        <div id="result-container"></div>
    </div>
    <div class="one-fourth">"""

flex_two_new = """<div class="layout-editor">
    <div class="layout-main">
        <div class="classroom-wrapper">
          <div class="teacher-desk"><i class="fa-solid fa-person-chalkboard"></i> FRONT OF CLASSROOM / TEACHER DESK</div>
          <div id="result-container"></div>
        </div>
    </div>
    <div class="layout-tools">"""
result_content = result_content.replace(flex_two_old, flex_two_new)

with open('templates/result.html', 'w', encoding='utf-8') as f:
    f.write(result_content)

print("HTML template patches applied.")
