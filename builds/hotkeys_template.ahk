#Requires AutoHotkey v2.0
#SingleInstance Force

; Ctrl + Alt + [ : Hotkey #1
^![:: {
    ; Pull content to clipboard
    Run "`"<INSTDIR>\PC_PullBullet.exe`" `"--headless`" `"-action`" `"copy`""

}

; Ctrl + Alt + ] : Hotkey #2
^!]:: {
    ; push clipboard content
    Run "`"<INSTDIR>\PC_PushBullet.exe`" `"--headless`" `"--clip`""
}

; Ctrl + Alt + ; : Hotkey #3
^!;:: {
    ; pull and paste, pull content to clipboard and paste
    Run "`"<INSTDIR>\PC_PullBullet.exe`" `"--headless`" `"-action`" `"copy`""
    sleep 100
    Send "^v"
}

; Ctrl + Alt + ' : Hotkey #4
^!':: {
    ; do ctrl c and then push
    Send "^c"
    Sleep 100
    Run "`"<INSTDIR>\PC_PushBullet.exe`" `"--headless`" `"--clip`""
}

; Ctrl + Alt + , : Hotkey #5
^!,:: {
    ; pull and save to file
    Run "`"<INSTDIR>\PC_PullBullet.exe`" `"--headless`" `"-action`" `"save`" `"--handleAsFile`""
}

; Ctrl + Alt + . : Hotkey #6
^!.:: {
    ; view content
    Run "`"<INSTDIR>\PC_PullBullet.exe`" `"--headless`" `"-action`" `"view`""
}

; Ctrl + Alt + / : Hotkey #7
^!/:: {
    ; Select address bar with Alt+D, copy with Ctrl+C and push
    Send "!d"
    Sleep 100
    Send "^c"
    Sleep 100
    Run "`"<INSTDIR>\PC_PushBullet.exe`" `"--headless`" `"--link`" `"--convertFileURI`""
}
