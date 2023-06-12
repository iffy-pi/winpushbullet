import sys
import keyring
from winotify import Notification
import pyperclip
import os

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]
if script_loc_dir not in sys.path:  
    sys.path.append(script_loc_dir)
from PushBullet import PushBullet

# files that should always be opened in the browser
BROWSER_HANDLED_FILES = [
    'png',
    'jpg',
    'jpeg',
    'gif'
]

def checkFlags(args:list, flag:str = "", flags:tuple=()):  
    usedList = False
    if len(flags) == 0:
        flags = flag,
    else:
        usedList = True

    results = []

    for fl in flags:
        res = False
        try:
            flInd = args.index(fl)
            # flag is in args lsit
            res = True

            # remove flag from list
            args.pop(flInd)    
        except ValueError:
            pass

        results.append(res)

    if not usedList and len(results) == 1:
        return results[0]
    
    return tuple(results)

def notify(title, body=""):
    if HEADLESS:
        toast = Notification('PushBullet', title, msg=body, icon=r"C:\Users\omnic\local\GitRepos\pushbullet-pc-integration\pushbullet-icon.png")
    else:
        print(title)
        if body != "":
            print(f'   {body}')

def brave(link):
    import subprocess
    child = subprocess.Popen([r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", link])

def main():
    try:
        global HEADLESS
        args = sys.argv[1:]
        
        HEADLESS = checkFlags(args, flag="--headless")

        openSaveDialog, openInBrowser= checkFlags(args, flags=("--openSaveDialog", "--openInBrowser"))

        accessToken = keyring.get_password('api.pushbullet.com', 'omnictionarian.xp@gmail.com')
        pb = PushBullet(accessToken)

        push = pb.pull(1)[0]

        if push['type'] == 'note':
            pyperclip.copy(push['body'])
            notify(
                'Text has been copied to your clipboard',
                str(push['body'])
            )

        elif push['type'] == 'link':
            pyperclip.copy(push['url'])

            msg = push['url']

            if push.get('title') is not None:
                msg = "{}\nTitle: {}".format(msg, push['title'])

            if push.get('body') is not None:
                msg = "{}\nMessage: {}".format(msg, push['body'])

            notify(
                'URL has been copied to your clipboard',
                msg
            )

        elif push['type'] == 'file':
            fileExt = str(os.path.splitext(push['name'])[1])

            if openInBrowser or (not openSaveDialog and fileExt.lower().replace('.', '' ) in BROWSER_HANDLED_FILES):
                # open it in browser
                brave(push['url'])
                notify(
                    'File ({}) has been opened in the browser'.format(push['name']),
                    f'Want to always save {fileExt} files, change script settings'
                )
                return
            
            # save to file
            from FileExplorerWindow import FileExplorerWindow
            fex = FileExplorerWindow()
            filename = fex.save(title="Save Pushed File", path=(None, push['name']))
            if filename is not None:
                with open(filename, "wb") as file:
                    file.write(push['content'])


    except Exception as e:
        # something went wrong
        if HEADLESS:
            notify("An error occured", str(e))
        else:
            import traceback
            traceback.print_exc()



if __name__ == '__main__':
    sys.exit(main())
