import os
import sys
import winreg as reg

PYTHONEXEC = r'C:\Python310\pythonw.exe'
BACKGROUND_DIRECTORY_CONTEXT_MENU_PATH = r"Directory\\Background\\shell"
SELECTED_DIRECTORY_CONTEXT_MENU_PATH = r"Directory\\shell"
SELECTED_FILE_CONTEXT_MENU_PATH = r"*\\shell"
headlessFlag = '--headless'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))

def addContextMenuRegistry(folderPath, optionName, commandStr, icon=None):
    folderKey = reg.CreateKeyEx(reg.HKEY_CLASSES_ROOT, folderPath)
    reg.SetValue(folderKey, '', reg.REG_SZ, f'&{optionName}')

    if icon is not None:
        reg.SetValueEx(folderKey, 'Icon', 0, reg.REG_SZ, icon)

    commandKey = reg.CreateKeyEx(folderKey, r'command')
    reg.SetValue(commandKey, '', reg.REG_SZ, commandStr)


def addPushFileToContextMenu(scriptPath, icon):
    folderPath = SELECTED_FILE_CONTEXT_MENU_PATH + r"\\" + "Python PushBullet Push File"
    optionName = 'Push File'
    commandStr = f'{PYTHONEXEC} "{scriptPath}" "{headlessFlag}" "--filePathArgument" "%1"'
    addContextMenuRegistry(folderPath, optionName, commandStr, icon=icon)


def addPushDirPathToContextMenu(scriptPath, icon):
    addContextMenuRegistry(
        BACKGROUND_DIRECTORY_CONTEXT_MENU_PATH + r"\\" + "Python PushBullet Push Current Directory Path",
        'Push Path of Current Directory',
        f'{PYTHONEXEC} "{scriptPath}" "{headlessFlag}" "--textArgument" "%V"',
        icon=icon
    )
    # also add one when the directory is selected
    addContextMenuRegistry(
        SELECTED_DIRECTORY_CONTEXT_MENU_PATH + r"\\" + "Python PushBullet Push Directory Path",
        'Push Directory Path',
        f'{PYTHONEXEC} "{scriptPath}" "{headlessFlag}" "--textArgument" "%V"',
        icon=icon
    )


def addPullFileToContextMenu(scriptPath, icon):
    addContextMenuRegistry(
        BACKGROUND_DIRECTORY_CONTEXT_MENU_PATH + r"\\" + "Python PullBullet Pull File",
        'Pull File To Here',
        f'{PYTHONEXEC} "{scriptPath}" "{headlessFlag}" "--strictlyFile" "--saveToDir" "%V"',
        icon=icon
    )


def addPullFileRenameToContextMenu(scriptPath, icon):
    addContextMenuRegistry(
        BACKGROUND_DIRECTORY_CONTEXT_MENU_PATH + r"\\" + "Python PullBullet Pull File And Rename",
        'Pull File To Here and Rename...',
        f'{PYTHONEXEC} "{scriptPath}" "{headlessFlag}" "--strictlyFile" "--saveToDirAndRename" "%V"',
        icon=icon
    )


# Add pull to directory

def main():
    global PYTHONEXEC

    PYTHONEXEC = os.path.join(os.path.split(sys.executable)[0], 'pythonw.exe')
    pushBulletScript = os.path.join(PROJECT_ROOT, 'pc_pushbullet.py')
    pullBulletScript = os.path.join(PROJECT_ROOT, 'pc_pullbullet.py')
    pushBulletIcon =  os.path.join(PROJECT_ROOT, 'config', "pushbullet-icon.ico")
    pullBulletIcon = os.path.join(PROJECT_ROOT, 'config', "pullbullet-icon.ico")

    print('Adding Push File To Context Menu')
    addPushFileToContextMenu(pushBulletScript, pushBulletIcon)

    print('Adding Push Directory Path To Context Menu')
    addPushDirPathToContextMenu(pushBulletScript, pushBulletIcon)

    print('Adding Pull File To Here To Context Menu')
    addPullFileToContextMenu(pullBulletScript, pullBulletIcon)

    print('Adding Pull File And Rename To Context Menu')
    addPullFileRenameToContextMenu(pullBulletScript, pullBulletIcon)

    print('Process Complete')
    input('Press Enter to Exit')

if __name__ == "__main__":
    sys.exit(main())
