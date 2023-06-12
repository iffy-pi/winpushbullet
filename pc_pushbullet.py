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
from shared import notif, checkFlags

TEXT = 0
LINK = 1
FILE = 2

def notify(title, body=""):
    if HEADLESS:
        notif(title, body=body)
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

def latestFileInTemp():
    import glob
    # get the list of files in the log directory
    dd = "C:\\Users\\omnic\\local\\temp"
    list_of_files = glob.glob(f'{dd}\\*')
    # get the c time of each file and use that as the key to order the list
    # and identify the maximum
    latest_file = max(list_of_files, key=os.path.getmtime)
    return os.path.join(dd, latest_file)

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
        
        forceText, filePathCopied, inferFileAllowed, useLatestTempFile = checkFlags(args, flags=("--forceText", "--filePathCopied", "--inferFileAllowed", "--latestTempFile"))

        if useLatestTempFile:
            # pushing latest file in temp
            content = latestFileInTemp()
            pushType = FILE

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
        from shared import handleError
        handleError(e, HEADLESS)

    

if __name__ == "__main__":
    sys.exit(main())