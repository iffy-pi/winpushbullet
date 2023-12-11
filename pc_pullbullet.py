import sys
import pyperclip
import os
from scripts.PushBullet import PushBullet

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]
if script_loc_dir not in sys.path:  
    sys.path.append(script_loc_dir)
from scripts.shared import checkFlags, setHeadless, notify, getPushBullet, isLink
from config.userconfig import TEMP_DIRECTORY, BROWSER_EXECUTABLE_PATH


IMAGE_FILE_EXTENSIONS = (
    'png',
    'jpg',
    'jpeg',
)

def openInBrowser(link):
    import subprocess
    child = subprocess.Popen([BROWSER_EXECUTABLE_PATH, link])

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
    

def saveFileToFolder(pushFile, folder):
    # saves the file to the given directory path
    with open(os.path.join(folder, pushFile['name']), 'wb') as file:
        file.write(pushFile['content'])
    
    notify(
        'File {} saved to directory'.format(pushFile['name']),
        body='Directory: {}'.format(folder),
    )

def isCopyableImage(fileExt):
    return fileExt in IMAGE_FILE_EXTENSIONS

def copyImageAndNotify(pushFile, fileExt):
    copyImageToClipboard(fileExt, pushFile['content'])
    notify(
        "Image has been copied to your clipboard",
        body=pushFile['name']
    )

def saveFileWithDialog(pushFile, folder=None) -> bool:
    # Returns true if the file was saved, and false otherwise
    from scripts.FileExplorerWindow import FileExplorerWindow
    fex = FileExplorerWindow()

    filename = fex.save(title="Save Pushed File (Or Cancel to Open In Browser)", path=(folder, pushFile['name']))
    
    if filename is not None:
        with open(filename, "wb") as file:
            file.write(pushFile['content'])
        return True
    else:
        return False

def handleFile(pushFile):
    fileExt = str(os.path.splitext(pushFile['name'])[1]).lower().replace('.', '')

    if SAVE_TO_PATH_ARG_AVAIL:
        # Save to the given path
        saveFileToFolder(pushFile, ARGS[0].replace('"', ''))
        return

    # Only image files can be copied
    if not(STRICTLY_FILE or STRICTLY_BROWSWER) and isCopyableImage(fileExt):
        copyImageAndNotify(pushFile, fileExt)
        return
    
    if STRICTLY_BROWSWER:
        # open the file in browser
        openInBrowser(pushFile['url'])
        return
    
    # default is open file window
    windowDirectory = ARGS[0].replace('"', '') if SAVE_TO_PATH_AND_RENAME else None
    fileSaved = saveFileWithDialog(pushFile, folder=windowDirectory)

    if not fileSaved and not SAVE_TO_PATH_AND_RENAME:
        # If file was not saved and user did not want to rename the file, open in the browser
        openInBrowser(pushFile['url'])

def handleLink(url):
    # copy to clipboard if stricly copy is on, otherwise open in browser
    if STRICTLY_COPY:
        pyperclip.copy(url)
        notify(
            'Link has been copied to your clipboard',
            url
        )
        return

    # default behaviour, open in browser
    openInBrowser(url)

def handleNote(text):
    # copies text to clipboard
    pyperclip.copy(text)
    notify(
        'Text has been copied to your clipboard',
        str(text)
    )


def main():
    try:
        global STRICTLY_COPY
        global STRICTLY_BROWSWER
        global STRICTLY_FILE
        global SAVE_TO_PATH_ARG_AVAIL
        global SAVE_TO_PATH_AND_RENAME
        global ARGS
        ARGS = sys.argv[1:]


        headless, STRICTLY_COPY, STRICTLY_BROWSWER, STRICTLY_FILE, SAVE_TO_PATH_ARG_AVAIL, SAVE_TO_PATH_AND_RENAME = checkFlags(ARGS, 
            flags=("--headless", "--strictlyCopy", "--strictlyBrowser", "--strictlyFile", "--saveToDir", "--saveToDirAndRename"))
        setHeadless(headless)

        push = getPushBullet().pull(1)[0]

        match push['type']:
            case PushBullet.PushType.TEXT:
                if isLink(push['body']):
                    handleLink(push['body'])
                else:
                    handleNote(push['body'])

            case PushBullet.PushType.LINK:
                handleLink(push['url'])

            case PushBullet.PushType.FILE:
                handleFile(push)

            case _:
                raise Exception('Unidentified type {}'.format(push['type']))
    
    except Exception as e:
        from scripts.shared import handleError
        handleError(e, headless)


if __name__ == '__main__':
    sys.exit(main())
