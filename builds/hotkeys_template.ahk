#NoEnv
#SingleInstance, Force
SendMode, Input
SetBatchLines, -1
SetWorkingDir, %A_ScriptDir%

; Ctrl + Alt + [ : Hotkey #1
^![:: ;Ctrl+Alt+[
    ; Pull content to clipboard
    Run, <INSTDIR>\PC_PullBullet\PC_PullBullet.exe "--headless" "-behaviour" "copy"
    return

; Ctrl + Alt + ] : Hotkey #2
^!]:: ;Ctrl+Alt+]
    ; push clipboard content
    Run, <INSTDIR>\PC_PushBullet\PC_PushBullet.exe "--headless" "--clip"
    return

; Ctrl + Alt + ; : Hotkey #3
^!;:: ;Ctrl+Alt+;
    ; pull and paste, pull content to clipboard and paste
    Run, <INSTDIR>\PC_PullBullet\PC_PullBullet.exe "--headless" "-behaviour" "copy"
    sleep 100
    Send, ^v
    return

; Ctrl + Alt + ' : Hotkey #4
^!':: ;Ctrl+Alt+'
    ; do ctrl c and then push
    Send, ^c
    sleep 100
    Run, <INSTDIR>\PC_PushBullet\PC_PushBullet.exe "--headless" "--clip"
    return

; Ctrl + Alt + , : Hotkey #5
^!,:: ;Ctrl+Alt+,
    ; pull and save to file
    Run, <INSTDIR>\PC_PullBullet\PC_PullBullet.exe "--headless" "-behaviour" "save" "--handleAsFile"
    return

; Ctrl + Alt + . : Hotkey #6
^!.:: ;Ctrl+Alt+.
    ; view content
    Run, <INSTDIR>\PC_PullBullet\PC_PullBullet.exe "--headless" "-behaviour" "view"
    return

; Ctrl + Alt + / : Hotkey #7
^!/:: ;Ctrl+Alt+/
    ; Select address bar with Alt+D, copy with Ctrl+C and push
    Send, !d
    sleep 100
    Send, ^c
    sleep 100
    Run, <INSTDIR>\PC_PushBullet\PC_PushBullet.exe "--headless" "--link" "--convertFileURI"
    return