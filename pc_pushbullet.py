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

def notify(title, body=""):
    toast = Notification('PushBullet', title, msg=body, icon=r"C:\Users\omnic\local\GitRepos\pushbullet-pc-integration\pushbullet-icon.png")
    toast.show()

def main():
    try:
        content = CONTENT

        TEXT = 0
        LINK = 1
        FILE = 2

        pushType = -1

        if content == '':
            notify("No content to push!")
            return

        args = sys.argv[1:]
        if len(args) > 0:
            arg = args[0]
            if arg == '--forceText':
                pushType = TEXT
            elif arg == '--filePathCopied':
                pushType = FILE


        if pushType == -1:
            # infer if it is a file path and then make file
            path = content
            for q in [ '"', "'" ]:
                if path[0] == q:
                    path = path[1:-1]
            
            if os.path.exists(path):
                pushType = FILE
                content = path
    

        if pushType == -1:
            # infer if it is a link
            for p in ['http://', 'https://', 'www.']:
                if content.startswith(p):
                    pushType = LINK
                
            if pushType != LINK:
                for p in ['.com', '.ca', '.org']:
                    if content.endswith(p):
                        pushType = LINK

        if pushType == -1:
            pushType = TEXT

        accessToken = keyring.get_password('api.pushbullet.com', 'omnictionarian.xp@gmail.com')
        pb = PushBullet(accessToken)

        pushFunction = {
            str(TEXT) : pb.pushNote,
            str(LINK) : pb.pushLink,
            str(FILE) : pb.pushFile
        }

        if pushType == FILE:
            for q in [ '"', "'" ]:
                if content[0] == 'q':
                    content = content[1:-1]
        
        notifs = {
            str(TEXT) : "Text pushed successfully",
            str(LINK) : "Link pushed successfully",
            str(FILE) :  "" if pushType != FILE  else "{} pushed successfully".format(os.path.split(content)[1])
        }
        

        # call the relevant push function
        pushFunction[str(pushType)](content)

        # notify user
        notify(notifs[str(pushType)], body=content)

    except Exception as e:
        # something went wrong
        notify("An error occured", body=str(e))


    

if __name__ == "__main__":
    sys.exit(main())