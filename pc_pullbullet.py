import sys
import pyperclip
import os

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

def handleFile(pushFile):
    # handle where it was just text over size
    if pushFile['name'] == "Pushed Text.txt":
        handleNote(pushFile['content'].decode())
        return
    
    fileExt = str(os.path.splitext(pushFile['name'])[1]).lower().replace('.', '')

    if STRICTLY_BROWSWER or (fileExt in BROWSER_HANDLED_FILES):
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
        args = sys.argv[1:]
        headless, STRICTLY_COPY, STRICTLY_BROWSWER = checkFlags(args, flags=("--headless", "--strictlyCopy", "--strictlyBrowser"))
        setHeadless(headless)

        push = getPushBullet().pull(1)[0]

        match push['type']:
            case 'note':
                if isLink(push['body']):
                    handleLink(push['body'])
                else:
                    handleNote(push['body'])

            case 'link':
                handleLink(push['url'])

            case 'file':
                handleFile(push)

            case _:
                raise Exception('Unidentified type {}'.format(push['type']))
    
    except Exception as e:
        from shared import handleError
        handleError(e, headless)


if __name__ == '__main__':
    sys.exit(main())
