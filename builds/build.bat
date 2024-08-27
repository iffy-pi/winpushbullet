@echo off
set buildPsh=%1
set buildPll=%2
set buildPb=%3
set buildsFolder=%~dp0
set pyinstaller=C:\Python\3.12.5\Scripts\pyinstaller.exe --clean

echo hello

if "%buildPsh%" EQU "true" call :build_pushbullet
if "%buildPll%" EQU "true" call :build_pullbullet
if "%buildPb%" EQU "true" call :build_pb
goto :eof

:build_pushbullet
    cd %buildsFolder%pc_pushbullet
    echo "Building PC_PushBullet"
    if exist build\ rd /q /s build
    if exist dist\ rd /q /s dist
    %pyinstaller% pc_pushbullet.spec
    cd dist
    if exist PC_PushBullet 7zip a PC_PushBullet.zip PC_PushBullet
goto:eof

:build_pullbullet
    cd %buildsFolder%pc_pullbullet
    if exist build\ rd /q /s build
    if exist dist\ rd /q /s dist
    echo "Building PC_PullBullet"
    %pyinstaller% pc_pullbullet.spec
    cd dist
    if exist PC_PullBullet 7zip a PC_PullBullet.zip PC_PullBullet
goto:eof

:build_pb
    cd %buildsFolder%pb
    if exist build\ rd /q /s build
    if exist dist\ rd /q /s dist
    echo "Building PB"
    %pyinstaller% pb.spec
    cd dist
    if exist pb 7zip a pb.zip pb
goto:eof