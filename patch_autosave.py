import re

# 1. Patch pupils.html
with open('templates/pupils.html', 'r', encoding='utf-8') as f:
    pupils_content = f.read()

# Remove the Save All button
pupils_content = re.sub(r'<hr>\s*<button class="success" onclick="savePupils\(\)"><i class="fa-solid fa-floppy-disk"></i> Save All</button>', '', pupils_content)

# Add savePupils() call in addPupil
pupils_content = pupils_content.replace("renderPupils();\n        }", "renderPupils();\n            savePupils();\n        }")

# Add savePupils() call in deletePupil
pupils_content = pupils_content.replace("renderPupils();\n    }", "renderPupils();\n        savePupils();\n    }")

# Remove the alert from savePupils
pupils_content = pupils_content.replace('if(res.status === "success") alert("Saved Pupils Successfully!");', '// Silently saved')

with open('templates/pupils.html', 'w', encoding='utf-8') as f:
    f.write(pupils_content)


# 2. Patch preferences.html
with open('templates/preferences.html', 'r', encoding='utf-8') as f:
    prefs_content = f.read()

# Remove the Save Rules button
prefs_content = re.sub(r'<hr>\s*<button class="success" onclick="savePrefs\(\)"><i class="fa-solid fa-floppy-disk"></i> Save Rules</button>', '', prefs_content)

# Add savePrefs() right after renderPrefs() in mutations
prefs_content = prefs_content.replace("renderPrefs();\n    }", "renderPrefs();\n        savePrefs();\n    }")

# Remove the alert from savePrefs
prefs_content = prefs_content.replace('if(res.status === "success") alert("Preferences Saved Successfully!");', '// Silently saved')

with open('templates/preferences.html', 'w', encoding='utf-8') as f:
    f.write(prefs_content)


# 3. Patch teacher.html
with open('templates/teacher.html', 'r', encoding='utf-8') as f:
    teacher_content = f.read()

# Remove the Save All Rules button card
teacher_content = re.sub(r'<div class="card" style="padding: 1em; margin-top: 1em; text-align: center;">\s*<button class="success" onclick="saveRules\(\)".*?>.*?</div>', '', teacher_content, flags=re.DOTALL)

# Add saveRules() inside mutations
teacher_content = teacher_content.replace("renderAll(); }", "renderAll(); saveRules(); }")
teacher_content = teacher_content.replace("renderAll(); \n        }", "renderAll(); \n            saveRules();\n        }")

# Remove the alert from saveRules
teacher_content = teacher_content.replace('if(res.status==="success") alert("Saved Rules Successfully!");', '// Silently saved')

with open('templates/teacher.html', 'w', encoding='utf-8') as f:
    f.write(teacher_content)

print("HTML auto-save patches applied.")
