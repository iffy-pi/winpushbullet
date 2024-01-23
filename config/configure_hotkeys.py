import os
import sys

project_root = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
python_exec = os.path.join(os.path.split(sys.executable)[0], 'pythonw.exe')

with open(os.path.join(project_root, 'config', 'hotkeys_template.ahk'), 'r') as file:
    content = file.read()

content = content.replace("<PROJECT_ROOT>", project_root)
content = content.replace("<PYTHON EXECUTABLE>", python_exec)


hotKeyFile = os.path.join(project_root, 'config', 'hotkeys.ahk')
with open(hotKeyFile, 'w') as file:
    file.write(content)

print(f'Hotkeys Configured, outputted to {hotKeyFile}')