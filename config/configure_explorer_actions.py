from os.path import join, split, abspath
import sys
import winreg as reg

BACKGROUND_DIRECTORY_CONTEXT_MENU_PATH = r"Directory\\Background\\shell"
SELECTED_DIRECTORY_CONTEXT_MENU_PATH = r"Directory\\shell"
SELECTED_FILE_CONTEXT_MENU_PATH = r"*\\shell"
headlessFlag = '--headless'
PROJECT_ROOT = abspath(join(split(__file__)[0], '..'))

def addContextMenuRegistry(folderPath, optionName, commandStr, icon=None):
    folderKey = reg.CreateKeyEx(reg.HKEY_CLASSES_ROOT, folderPath)
    reg.SetValue(folderKey, '', reg.REG_SZ, f'&{optionName}')

    if icon is not None:
        reg.SetValueEx(folderKey, 'Icon', 0, reg.REG_SZ, icon)

    commandKey = reg.CreateKeyEx(folderKey, r'command')
    reg.SetValue(commandKey, '', reg.REG_SZ, commandStr)


def addPushFileToContextMenu(scriptPath, icon):
    folderPath = SELECTED_FILE_CONTEXT_MENU_PATH + r"\\" + "PC_PushBullet Push File"
    optionName = 'Push File'
    commandStr = f'"{scriptPath}" "{headlessFlag}" "-arg" "%1" "--file"'
    addContextMenuRegistry(folderPath, optionName, commandStr, icon=icon)


def addPushDirPathToContextMenu(scriptPath, icon):
    addContextMenuRegistry(
        BACKGROUND_DIRECTORY_CONTEXT_MENU_PATH + r"\\" + "PC_PushBullet Push Current Directory Path",
        'Push Path of Current Directory',
        f'"{scriptPath}" "{headlessFlag}" "-arg" "%V" "--text"',
        icon=icon
    )
    # also add one when the directory is selected
    addContextMenuRegistry(
        SELECTED_DIRECTORY_CONTEXT_MENU_PATH + r"\\" + "PC_PushBullet Push Directory Path",
        'Push Directory Path',
        f'"{scriptPath}" "{headlessFlag}" "-arg" "%V" "--text"',
        icon=icon
    )


def addPullFileToContextMenu(scriptPath, icon):
    addContextMenuRegistry(
        BACKGROUND_DIRECTORY_CONTEXT_MENU_PATH + r"\\" + "PC_PullBullet Pull File",
        'Pull File To Here',
        f'"{scriptPath}" "{headlessFlag}" "--handleAsFile" "-behaviour" "save" "-saveToDir" "%V"',
        icon=icon
    )


def addPullFileRenameToContextMenu(scriptPath, icon):
    addContextMenuRegistry(
        BACKGROUND_DIRECTORY_CONTEXT_MENU_PATH + r"\\" + "PC_PullBullet Pull File And Rename",
        'Pull File To Here and Rename...',
        f'"{scriptPath}" "{headlessFlag}" "--handleAsFile" "-behaviour" "save" "-saveToDirWithDlg" "%V"',
        icon=icon
    )

def main():
    pshDir = 'C:\\PC_PushBullet_Integrations\\PC_PushBullet'
    pllDir = 'C:\\PC_PushBullet_Integrations\\PC_PullBullet'
    pshExec = join(pshDir, 'PC_PushBullet.exe')
    pllExec = join(pllDir, 'PC_PullBullet.exe')

    print('Adding Push File To Context Menu')
    addPushFileToContextMenu(pshExec, pshExec)

    print('Adding Push Directory Path To Context Menu')
    addPushDirPathToContextMenu(pshExec, pshExec)

    print('Adding Pull File To Here To Context Menu')
    addPullFileToContextMenu(pllExec, pllExec)

    print('Adding Pull File And Rename To Context Menu')
    addPullFileRenameToContextMenu(pllExec, pllExec)

    print('Process Complete')
    input('Press Enter to Exit')

if __name__ == "__main__":
    sys.exit(main())
