import sys
import os
from enum import Enum

import pyperclip

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]
if script_loc_dir not in sys.path:  
    sys.path.append(script_loc_dir)
from scripts.shared import checkFlags, getArgumentForFlag, setHeadless, notify, getPushBullet, isLink
from scripts.PushBullet import PushBullet, PushObject, PushType
from config.userconfig import TEMP_DIRECTORY


IMAGE_FILE_EXTENSIONS = (
    'png',
    'jpg',
    'jpeg',
)

class ScriptBehaviour(Enum):
    DEFAULT = 'default'
    COPY_CONTENT = 'copy'
    VIEW_CONTENT = 'view'
    SAVE_ALL_FILES = 'save'

class FileContainer:
    def __init__(self, name:str, url: str, fileBytes:bytes, pushType:PushType):
        self.name =  name
        self.ext = os.path.splitext(name)[1].replace('.', '')
        self.url = url
        self.bytes = fileBytes
        self.pushType = pushType

def openInBrowser(link):
    import webbrowser
    webbrowser.open_new_tab(link)

def openTextWithOS(text:str):
    # Saves the text to a temp file and then opens that temp file
    tempFile = f"{TEMP_DIRECTORY}\\temp.txt"
    with open(tempFile, "w") as file:
        file.write(text)
    os.startfile(tempFile, "open")

def copyImageToClipboard(fileExt, fileContent):
    # save the image to a temp file
    tempFile = f"{TEMP_DIRECTORY}\\temp." + fileExt
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

def getCommonName(pt:PushType):
    return "Link" if PushType == PushType.LINK else "Note"

def saveFile(fc: FileContainer):
    # Save file method for -saveToDir
    # If there is a file that exists at that location, default to file explorer dialog
    if SAVE_DIRECTORY_PATH is not None and not SAVE_TO_DIR_USING_DLG and not os.path.exists(os.path.join(SAVE_DIRECTORY_PATH, fc.name)):
        with open(os.path.join(SAVE_DIRECTORY_PATH, fc.name), 'wb') as file:
            file.write(fc.bytes)

        title = 'File {} saved to directory'.format(fc.name)

        if FORCING_TYPE_TO_FILE:
            title = 'Pushed {} was saved to the directory as {}'.format(getCommonName(fc.pushType), fc.name)

        notify(
            title,
            body='Directory: {}'.format(SAVE_DIRECTORY_PATH),
        )
        return

    # Default Save File Method: Use explorer dialog
    # -saveWithDlg will override SAVE_DIRECTORY_PATH
    from scripts.FileExplorerWindow import FileExplorerWindow

    windowTitle = "Save Pushed File"
    fileTypes = [('Current File', f'*.{fc.ext}'), ('All Files', '*.*')]

    # If the type is not a file type then we should
    if TREATING_TYPE_AS_FILE in [ PushType.LINK, PushType.TEXT ]:
        windowTitle = "Save {}".format("Link" if TREATING_TYPE_AS_FILE == PushType.LINK else "Note")
        fileTypes = [('Plain Text', '*.txt'), ('All Files', '*.*')]

    FileExplorerWindow().save(fc.bytes,
                                     windowTitle=windowTitle,
                                     path=(SAVE_DIRECTORY_PATH, fc.name),
                                     fileTypes=fileTypes)

def handleImageFile(fc: FileContainer):
    if BEHAVIOUR == ScriptBehaviour.VIEW_CONTENT:
        openInBrowser(fc.url)
        return

    if BEHAVIOUR == ScriptBehaviour.SAVE_ALL_FILES:
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
    if BEHAVIOUR == ScriptBehaviour.VIEW_CONTENT:
        openInBrowser(fc.url)
        return

    # Default Behaviour
    # Saved using save file method
    saveFile(fc)

def handleLink(url):
    if BEHAVIOUR == ScriptBehaviour.COPY_CONTENT:
        pyperclip.copy(url)
        notify(
            'Link has been copied to your clipboard',
            url
        )
        return

    # default behaviour, open in browser
    openInBrowser(url)

def handleNote(text):

    if BEHAVIOUR == ScriptBehaviour.VIEW_CONTENT:
        openTextWithOS(text)
        return

    # Default behaviour: Copy to clipboard
    pyperclip.copy(text)
    notify(
        'Text has been copied to your clipboard',
        str(text)
    )

def getBehaviour(args) -> ScriptBehaviour:
    # read the behaviour argument
    selBhvr = getArgumentForFlag(args, '-behaviour')
    if selBhvr is None:
        return ScriptBehaviour.DEFAULT
    selBhvr = selBhvr.lower()

    availBhvrs = [
        ScriptBehaviour.DEFAULT,
        ScriptBehaviour.COPY_CONTENT,
        ScriptBehaviour.VIEW_CONTENT,
        ScriptBehaviour.SAVE_ALL_FILES,
    ]

    for bhvr in availBhvrs:
        if selBhvr == bhvr.value:
            return bhvr

    raise Exception(f'Unknown behaviour: {selBhvr}')

def makeFileContainerFromPush(push:PushObject) -> FileContainer:
    match push.type:
        case PushType.TEXT:
            return FileContainer('text.txt', 'N/A', push.body.encode("utf-8"), push.type)

        case PushType.LINK:
            return FileContainer('link.txt', push.url, push.url.encode("utf-8"), push.type)

        case PushType.FILE:
            return FileContainer(push.filename, push.fileURL, push.getFileBinary(), push.type)

        case _:
            raise Exception('Unidentified type {}'.format(push.type))


def main():
    headless = True
    try:
        global SAVE_DIRECTORY_PATH
        global SAVE_TO_DIR_USING_DLG
        global BEHAVIOUR
        global TREATING_TYPE_AS_FILE
        global FORCING_TYPE_TO_FILE

        SAVE_TO_DIR_USING_DLG = False
        SAVE_DIRECTORY_PATH = None
        TREATING_TYPE_AS_FILE = None
        FORCING_TYPE_TO_FILE = False

        args = sys.argv[1:]

        headless, handleAsFile = checkFlags(args, flags=("--headless", "--handleAsFile"))
        setHeadless(headless)

        BEHAVIOUR = getBehaviour(args)
        saveToDirArg = getArgumentForFlag(args, "-saveToDir")
        saveToDirWithDlgArg = getArgumentForFlag(args, "-saveToDirWithDlg")

        if saveToDirArg is not None and saveToDirWithDlgArg is not None:
            raise Exception('Conflicting flags: Cannot use "-saveToDir" and "-saveToDirWithDlg" together')

        if saveToDirWithDlgArg is not None:
            SAVE_DIRECTORY_PATH = saveToDirWithDlgArg
            SAVE_TO_DIR_USING_DLG = True
        elif saveToDirArg is not None:
            SAVE_DIRECTORY_PATH = saveToDirArg

        if SAVE_DIRECTORY_PATH is not None:
            SAVE_DIRECTORY_PATH = SAVE_DIRECTORY_PATH.replace('"', '')
            if not os.path.exists(SAVE_DIRECTORY_PATH):
                raise Exception('Save Directory does not exist!')

        push = getPushBullet().pull(1)[0]

        if handleAsFile or BEHAVIOUR == ScriptBehaviour.SAVE_ALL_FILES:
            fc = makeFileContainerFromPush(push)
            TREATING_TYPE_AS_FILE = push.type
            FORCING_TYPE_TO_FILE = push.type != PushType.FILE
            handleFile(fc)
        else:
            match push.type:
                case PushType.TEXT:
                    if isLink(push.body):
                        handleLink(push.body)
                    else:
                        handleNote(push.body)

                case PushType.LINK:
                    handleLink(push.url)

                case PushType.FILE:
                    handleFile(makeFileContainerFromPush(push))

                case _:
                    raise Exception('Unidentified type {}'.format(push['type']))
    
    except Exception as e:
        from scripts.shared import handleError
        handleError(e, headless)


if __name__ == '__main__':
    sys.exit(main())
