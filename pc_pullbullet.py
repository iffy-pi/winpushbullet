import sys
from os import startfile
from os.path import join, split, realpath, splitext, exists, expanduser
from enum import Enum

import pyperclip

script_loc_dir = split(realpath(__file__))[0]
if script_loc_dir not in sys.path:  
    sys.path.append(script_loc_dir)
from scripts.shared import checkFlags, getArgumentForFlag, setHeadless, notify, getPushBullet, isLink, getTempDirectory, config_notif, config_working_files
from scripts.PushBullet import PushObject, PushType

config_notif('WinPushBullet', join(script_loc_dir, 'pullbullet-icon.ico'))
config_working_files(script_loc_dir)

ACTION = None

IMAGE_FILE_EXTENSIONS = (
    '.png',
    '.jpg',
    '.jpeg',
    '.webp',
    '.tif',
    '.tiff',
    '.svg',
    '.bmp',
    '.gif',
    '.heic'
)

class ScriptAction(Enum):
    DEFAULT = 'default'
    COPY_CONTENT = 'copy'
    VIEW_CONTENT = 'view'
    SAVE_ALL_FILES = 'save'

class FileContainer:
    def __init__(self, name:str, url: str, fileBytes:bytes, pushType:PushType):
        self.name =  name
        self.dest = None
        self.destExt = None
        self.useExplorer = False
        self.ext = splitext(name)[1]
        self.url = url
        self.bytes = fileBytes
        self.pushType = pushType

def openInBrowser(link):
    import webbrowser
    webbrowser.open_new_tab(link)

def openTextWithOS(text:str):
    # Saves the text to a temp file and then opens that temp file
    tempFile = f"{getTempDirectory()}\\temp.txt"
    with open(tempFile, "w") as file:
        file.write(text)
    startfile(tempFile, "open")

def copyImageToClipboard(fileExt, fileContent: bytes):
    # save the image to a temp file
    tempFile = f"{getTempDirectory()}\\temp" + fileExt
    with open(tempFile, 'wb') as file:
        file.write(fileContent)

    # open the image with PIL
    import win32clipboard
    from PIL import Image
    from io import BytesIO

    image = Image.open(tempFile)

    # convert to clipboard byte stream
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    # paste into the clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def isCopyableImage(fileExt):
    return fileExt in IMAGE_FILE_EXTENSIONS

def getPushTypeStr(pt:PushType):
    match pt:
        case PushType.TEXT:
            return "Text"
        case PushType.LINK:
            return "Link"
        case PushType.FILE:
            return "File"
        case _:
            raise Exception('Unknown type')


def notifyFileSaved(fc: FileContainer, saveDest: str):
    notify(
        f'Pushed File "{fc.name}" saved' if fc.pushType == PushType.FILE else f'Pushed {getPushTypeStr(fc.pushType)} saved',
        body=f'Destination: {saveDest}'
    )


def saveWithFileExplorer(fc: FileContainer):
    from scripts.FileExplorerWindow import FileExplorerWindow
    fileExists = fc.dest is not None and exists(fc.dest)

    dlgDir = expanduser('~')
    dlgFile = fc.name
    dlgExt = fc.ext

    if fc.dest is not None:
        dlgDir = split(fc.dest)[0]
        dlgFile = split(fc.dest)[1]
        dlgExt = fc.destExt

    windowTitle = f"Save Pushed {getPushTypeStr(fc.pushType)}"
    fileTypes = [('Current File', f'*{dlgExt}'), ('All Files', '*.*')]

    if fileExists:
        windowTitle += f' - File "{join(dlgDir, dlgFile)}" already exists'
        i = 1
        base = splitext(dlgFile)[0]
        while exists(join(dlgDir, dlgFile)):
            dlgFile = f'{base} ({i}){dlgExt}'
            i += 1

    if fc.pushType != PushType.FILE:
        dlgFile = None

        content = fc.bytes.decode('utf-8').replace('\n',' ').replace('\t', ' ').replace('\r', ' ')
        maxChars = 90

        if len(content) > maxChars:
            content = content[:maxChars - (5 if fc.pushType == PushType.TEXT else 3)]
            if fc.pushType == PushType.TEXT:
                content = f'"{content}"...'
            else:
                content = f'{content}...'
        else:
            if fc.pushType == PushType.TEXT:
                content = f'"{content}"'

        windowTitle = f"Save Pushed {getPushTypeStr(fc.pushType)}: {content}"


    saved, addr = FileExplorerWindow().save(fc.bytes,
                              windowTitle=windowTitle,
                              path=(dlgDir, dlgFile),
                              fileTypes=fileTypes)

    if saved:
        notifyFileSaved(fc, addr)


def saveFile(fc: FileContainer):
    if fc.dest is not None:
        fd = split(fc.dest)[0]
        if not exists(fd):
            raise Exception(f'Save directory for push item "{fd}" does not exist')

        if exists(fc.dest):
            fc.useExplorer = True

    if fc.dest is None or fc.useExplorer or fc.pushType != PushType.FILE:
        saveWithFileExplorer(fc)
        return

    # Save the file in the destination location
    with open(fc.dest, 'wb') as file:
        file.write(fc.bytes)

    notifyFileSaved(fc, fc.dest)

def handleImageFile(fc: FileContainer):
    if ACTION == ScriptAction.VIEW_CONTENT:
        openInBrowser(fc.url)
        return

    if ACTION == ScriptAction.SAVE_ALL_FILES:
        saveFile(fc)
        return

    # Default behaviour
    # Copy content behaviour
    # Copy image to clipboard
    copyImageToClipboard(fc.ext, fc.bytes)
    notify(
        "Image has been copied to your clipboard",
        body=fc.name
    )

def handleFile(fc: FileContainer):
    if isCopyableImage(fc.ext):
        handleImageFile(fc)
        return

    # Behaviour for other files
    if ACTION == ScriptAction.VIEW_CONTENT:
        openInBrowser(fc.url)
        return

    # Default Behaviour
    # Saved using save file method
    saveFile(fc)

def handleLink(url):
    if ACTION == ScriptAction.COPY_CONTENT:
        pyperclip.copy(url)
        notify(
            'Link has been copied to your clipboard',
            url
        )
        return

    # default behaviour, open in browser
    openInBrowser(url)

def handleNote(text):

    if ACTION == ScriptAction.VIEW_CONTENT:
        openTextWithOS(text)
        return

    # Default behaviour: Copy to clipboard
    pyperclip.copy(text)
    notify(
        'Text has been copied to your clipboard',
        str(text)
    )

def getAction(args) -> ScriptAction:
    selAction = getArgumentForFlag(args, '-action')
    if selAction is None:
        return ScriptAction.DEFAULT
    selAction = selAction.lower()

    availActions = [
        ScriptAction.DEFAULT,
        ScriptAction.COPY_CONTENT,
        ScriptAction.VIEW_CONTENT,
        ScriptAction.SAVE_ALL_FILES,
    ]

    for action in availActions:
        if selAction == action.value:
            return action

    raise Exception(f'Unknown behaviour: {selAction}')

def makeFileContainerFromPush(push:PushObject, saveDir: str|None, savePath: str|None, useExplorer: bool) -> FileContainer:
    match push.type:
        case PushType.TEXT:
            fc = FileContainer('text.txt', 'N/A', push.body.encode("utf-8"), push.type)

        case PushType.LINK:
            fc = FileContainer('link.txt', push.url, push.url.encode("utf-8"), push.type)

        case PushType.FILE:
            fc = FileContainer(push.filename, push.fileURL, push.getFileBinary(), push.type)

        case _:
            raise Exception('Unidentified type {}'.format(push.type))

    fc.useExplorer = useExplorer

    if savePath is not None:
        fc.dest = savePath.replace('"', '')
        fc.destExt = splitext(savePath)[1]
        return fc

    if saveDir is not None:
        fc.dest = join(saveDir.replace('"', ''), fc.name)
        fc.destExt = fc.ext
        return fc

    return fc

def main():
    headless = True
    try:
        global ACTION

        args = sys.argv[1:]

        headless, handleAllTypesAsFile, useExplorer = checkFlags(args, flags=("--headless", "--handleAsFile", "--explorer"))
        setHeadless(headless)

        ACTION = getAction(args)
        saveIn = getArgumentForFlag(args, "-saveIn")
        saveAs = getArgumentForFlag(args, "-saveAs")

        if saveIn is not None and saveAs is not None:
            raise Exception('Conflicting flags: Cannot use "-saveIn" and "-saveAs" together')

        push = getPushBullet().pull(1)[0]

        if handleAllTypesAsFile or ACTION == ScriptAction.SAVE_ALL_FILES:
            fc = makeFileContainerFromPush(push, saveIn, saveAs, useExplorer)
            handleFile(fc)
            return 0

        match push.type:
            case PushType.TEXT:
                if isLink(push.body):
                    handleLink(push.body)
                else:
                    handleNote(push.body)

            case PushType.LINK:
                handleLink(push.url)

            case PushType.FILE:
                handleFile(makeFileContainerFromPush(push, saveIn, saveAs, useExplorer))

            case _:
                raise Exception('Unidentified type {}'.format(push['type']))
        return 0
    
    except Exception as e:
        from scripts.shared import handleError
        handleError(e, headless)


if __name__ == '__main__':
    sys.exit(main())
