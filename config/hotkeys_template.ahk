#NoEnv
#SingleInstance, Force
SendMode, Input
SetBatchLines, -1
SetWorkingDir, %A_ScriptDir%

; Ctrl + Alt + [ : Pull Content (Default)
^![:: ;Ctrl+Alt+[
    Run, <PYTHON EXECUTABLE> "<PROJECT_ROOT>\pc_pullbullet.py" "--headless" "-behaviour" "default"
    return

; Ctrl + Alt + ; : Pull Content (Copy)
^!;:: ;Ctrl+Alt+;
    Run, <PYTHON EXECUTABLE> "<PROJECT_ROOT>\pc_pullbullet.py" "--headless" "-behaviour" "copy"
    return

; Ctrl + Alt + . : Pull Content (View)
^!.:: ;Ctrl+Alt+.
    Run, <PYTHON EXECUTABLE> "<PROJECT_ROOT>\pc_pullbullet.py" "--headless" "-behaviour" "view"
    return

; Ctrl + Alt + , : Pull Content (Save To File)
^!,:: ;Ctrl+Alt+,
    Run, <PYTHON EXECUTABLE> "<PROJECT_ROOT>\pc_pullbullet.py" "--headless" "-behaviour" "save" "--handleAsFile"
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