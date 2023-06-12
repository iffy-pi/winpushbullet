import pyperclip
CONTENT = pyperclip.paste()

from winotify import Notification
import sys
import os
import keyring

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]
if script_loc_dir not in sys.path:  
    sys.path.append(script_loc_dir)
from PushBullet import PushBullet

TEXT = 0
LINK = 1
FILE = 2

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
        toast.show()
    else:
        print(title)
        if body != "":
            print(f'   {body}')

def determineType(content, inferFileAllowed=False):
    if inferFileAllowed:
        # infer if it is a file path and then make file
        path = content
        for q in [ '"', "'" ]:
            if path[0] == q:
                path = path[1:-1]
        
        if os.path.exists(path):
            return FILE, path

    # infer if it is a link
    for p in ['http://', 'https://', 'www.']:
        if content.startswith(p):
            return LINK, content
        
    for p in ['.com', '.ca', '.org']:
        if content.endswith(p):
            return LINK, content

    return TEXT, content

def main():
    try:
        content = CONTENT
        pushType = -1
        inferFileAllowed = False
        global HEADLESS
        HEADLESS = False

        args = sys.argv[1:]
        
        HEADLESS = checkFlags(args, flag="--headless")

        if content == '':
            notify("No content to push!")
            return
        
        forceText, filePathCopied, inferFileAllowed = checkFlags(args, flags=("--forceText", "--filePathCopied", "--inferFileAllowed"))
        if forceText:
            pushType = TEXT
        
        elif filePathCopied:
            pushType = FILE

        if pushType == -1:
            pushType, content = determineType(content, inferFileAllowed=inferFileAllowed)

        accessToken = keyring.get_password('api.pushbullet.com', 'omnictionarian.xp@gmail.com')
        pb = PushBullet(accessToken)

        pushFunction = {
            str(TEXT) : pb.pushNote,
            str(LINK) : pb.pushLink,
            str(FILE) : pb.pushFile
        }

        if pushType == FILE:
            content = content.replace('"', '').replace("'", "")

        notifs = {
            str(TEXT) : ("Text pushed successfully", content),
            str(LINK) : ("Link pushed successfully", content),
            str(FILE) :  ("" if pushType != FILE  else "File ({}) pushed successfully".format(os.path.split(content)[1]), "Filepath: {}".format(content) )
        }
        

        # call the relevant push function
        pushFunction[str(pushType)](content)

        # notify user
        notifInfo = notifs[str(pushType)]
        notify(notifInfo[0], body=notifInfo[1])

    except Exception as e:
        # something went wrong
        if HEADLESS:
            notify("An error occured", str(e))
        else:
            import traceback
            traceback.print_exc()

    

if __name__ == "__main__":
    sys.exit(main())