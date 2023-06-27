import sys
import keyring
import pyperclip
import os

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]
if script_loc_dir not in sys.path:  
    sys.path.append(script_loc_dir)
from shared import checkFlags, notif, getPushBullet


# files that should always be opened in the browser
BROWSER_HANDLED_FILES = [
    'png',
    'jpg',
    'jpeg',
    'gif'
]

def notify(title, body=""):
    if HEADLESS:
        notif(title, body=body)
    else:
        print(title)
        if body != "":
            if len(body) > 200:
                print(f'   {body[:197]}...')
            else:
                print(f'    {body}')

def openInBrowser(link):
    import subprocess
    child = subprocess.Popen([r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", link])

def main():
    try:
        global HEADLESS
        args = sys.argv[1:]
        
        HEADLESS = checkFlags(args, flag="--headless")

        strictlyCopy, strictlyBrowser = checkFlags(args, flags=("--strictlyCopy", "--strictlyBrowser"))

        pb = getPushBullet()
        push = pb.pull(1)[0]

        if push['type'] == 'note':
            pyperclip.copy(push['body'])
            notify(
                'Text has been copied to your clipboard',
                str(push['body'])
            )

        elif push['type'] == 'link':
            pyperclip.copy(push['url'])

            if strictlyCopy:
                msg = push['url']

                if push.get('title') is not None:
                    msg = "{}\nTitle: {}".format(msg, push['title'])

                if push.get('body') is not None:
                    msg = "{}\nMessage: {}".format(msg, push['body'])

                notify(
                    'URL has been copied to your clipboard',
                    msg
                )
                return

            # default behaviour, open in browser
            openInBrowser(push['url'])


        elif push['type'] == 'file':
            # handle where it was just text over size
            if push['name'] == "Pushed Text.txt":
                text = push['content'].decode()
                pyperclip.copy(text)
                notify(
                    'Text has been copied to your clipboard',
                    str(text)
                )
                return

            fileExt = str(os.path.splitext(push['name'])[1])

            if strictlyBrowser or (fileExt.lower().replace('.', '' ) in BROWSER_HANDLED_FILES):
                # open it in browser
                openInBrowser(push['url'])
                if not strictlyBrowser:
                    title = 'File ({}) has been opened in the browser'.format(push['name'])
                    body = f'Want to always save {fileExt} files? change script settings.'
                    if HEADLESS:
                        notif(
                            title,
                            body=body,
                            filePath=__file__,
                            label="Open Script"
                        )
                    else:
                        print(title)
                        print(body)
                return
            
            # default is open file window
            from FileExplorerWindow import FileExplorerWindow
            fex = FileExplorerWindow()
            filename = fex.save(title="Save Pushed File (Or Cancel to Open In Browser)", path=(None, push['name']))
            if filename is not None:
                with open(filename, "wb") as file:
                    file.write(push['content'])
            else:
                # if user cancelled save, then open in the browser
                openInBrowser(push['url'])

    except Exception as e:
        from shared import handleError
        handleError(e, HEADLESS)


if __name__ == '__main__':
    sys.exit(main())
