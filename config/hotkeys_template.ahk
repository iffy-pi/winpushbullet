#NoEnv
#SingleInstance, Force
SendMode, Input
SetBatchLines, -1
SetWorkingDir, %A_ScriptDir%

; Ctrl + Alt + [ : Pull Content (Default)
^![:: ;Ctrl+Alt+[
    Run, <PYTHON EXECUTABLE> "<PROJECT_ROOT>\pc_pullbullet.py" "--headless"
    return

; Ctrl + Alt + ; : Pull Content (Copy)
^!;:: ;Ctrl+Alt+;
    Run, <PYTHON EXECUTABLE> "<PROJECT_ROOT>\pc_pullbullet.py" "--headless" "--strictlyCopy"
    return

; Ctrl + Alt + . : Pull Content (Browser)
^!.:: ;Ctrl+Alt+.
    Run, <PYTHON EXECUTABLE> "<PROJECT_ROOT>\pc_pullbullet.py" "--headless" "--strictlyBrowser"
    return

; Ctrl + Alt + , : Pull Content (Save To File)
^!,:: ;Ctrl+Alt+,
    Run, <PYTHON EXECUTABLE> "<PROJECT_ROOT>\pc_pullbullet.py" "--headless" "--strictlyFile"
    return

; Ctrl + Alt + ] : Push Content (Default)
^!]:: ;Ctrl+Alt+]
    Run, <PYTHON EXECUTABLE> "<PROJECT_ROOT>\pc_pushbullet.py" "--headless"
    return

; Ctrl + Alt + ' : Push Content (Text)
^!':: ;Ctrl+Alt+'
    Run, <PYTHON EXECUTABLE> "<PROJECT_ROOT>\pc_pushbullet.py" "--headless" "--forceText"
    return

; Ctrl + Alt + / : Push Content (Temp)
^!/:: ;Ctrl+Alt+/
    Run, <PYTHON EXECUTABLE> "<PROJECT_ROOT>\pc_pushbullet.py" "--headless" "--latestTempFile"
    return