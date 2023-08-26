import sys
import pyperclip
import os
from PushBullet import PushBullet

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]
if script_loc_dir not in sys.path:  
    sys.path.append(script_loc_dir)
from shared import checkFlags, setHeadless, notify, getPushBullet, isLink


# files that should always be opened in the browser
BROWSER_HANDLED_FILES = [
    'png',
    'jpg',
    'jpeg',
    'gif'
]

def openInBrowser(link):
    import subprocess
    child = subprocess.Popen([r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", link])

def handleNote(text):
    # copies text to clipboard
    pyperclip.copy(text)
    notify(
        'Text has been copied to your clipboard',
        str(text)
    )

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

def copyImageToClipboard(fileExt, fileContent):
    # save the image to a temp file
    tempFile = r"C:\Users\omnic\local\temp\temp." + fileExt
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
    

def handleFile(pushFile):
    fileExt = str(os.path.splitext(pushFile['name'])[1]).lower().replace('.', '')

    if STRICTLY_COPY or (not STRICTLY_FILE and fileExt in ['png', 'jpeg', 'jpg']):
        # if it is an image file, then we copy it to the clipboard 
        # if strictly copy or default behaviour
        copyImageToClipboard(fileExt, pushFile['content'])
        notify(
            "Image has been copied to your clipboard",
            body=pushFile['name']
        )
        return
    
    if STRICTLY_BROWSWER:
        # open it in browser
        openInBrowser(pushFile['url'])
        if not STRICTLY_BROWSWER:
            # it means it was inferred to be opened in the browser
            # notify user how to change the settings
            title = 'File ({}) has been opened in the browser'.format(pushFile['name'])
            body = f'Want to always save .{fileExt} files? change script settings.'

            notify(
                    title,
                    body=body,
                    attachmentPath=__file__,
                    attachmentLabel="Open Script"
                )
        return
    
    # default is open file window
    from FileExplorerWindow import FileExplorerWindow
    fex = FileExplorerWindow()
    filename = fex.save(title="Save Pushed File (Or Cancel to Open In Browser)", path=(None, pushFile['name']))
    if filename is not None:
        with open(filename, "wb") as file:
            file.write(pushFile['content'])
    else:
        # if user cancelled save, then open in the browser
        openInBrowser(pushFile['url'])

def main():
    try:
        global STRICTLY_COPY
        global STRICTLY_BROWSWER
        global STRICTLY_FILE
        args = sys.argv[1:]
        headless, STRICTLY_COPY, STRICTLY_BROWSWER, STRICTLY_FILE = checkFlags(args, flags=("--headless", "--strictlyCopy", "--strictlyBrowser", "--strictlyFile"))
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
        from shared import handleError
        handleError(e, headless)


if __name__ == '__main__':
    sys.exit(main())
