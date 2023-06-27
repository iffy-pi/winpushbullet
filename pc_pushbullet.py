# pull from clip board first
import win32clipboard as cb
CLIPBOARD_CONTENT = None
couldBeScreenshot = False

cb.OpenClipboard()
CLIPBOARD_HAS_FILE_HANDLER = cb.IsClipboardFormatAvailable(cb.CF_HDROP)
if cb.IsClipboardFormatAvailable(cb.CF_HDROP):
    CLIPBOARD_CONTENT = cb.GetClipboardData(cb.CF_HDROP)
    CLIPBOARD_HAS_FILE_HANDLER = True
else:
    # tuple to allow for multiple items
    try:
        CLIPBOARD_CONTENT = (cb.GetClipboardData(), )
    except TypeError:
        CLIPBOARD_CONTENT = None
        couldBeScreenshot = True
cb.CloseClipboard()

if couldBeScreenshot:
    # screenshots copied to clipboard cause this exception
    # grab the screenshow with Pillow, save to file and return the file handler
    from PIL import ImageGrab
    tempSc = r"C:\Users\omnic\local\temp\screenshot.png"
    img = ImageGrab.grabclipboard()
    img.save(tempSc)
    CLIPBOARD_CONTENT = (tempSc, )
    CLIPBOARD_HAS_FILE_HANDLER = True

import sys
import os
import keyring

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]
if script_loc_dir not in sys.path:  
    sys.path.append(script_loc_dir)
from shared import notif, checkFlags, getPushBullet

TEXT = 0
LINK = 1
FILE = 2

def notify(title, body="", filePath=None):
    if HEADLESS:
        notif(title, body=body, filePath=filePath)
    else:
        print(title)
        if body != "":
            if len(body) > 200:
                print(f'   {body[:197]}...')
            else:
                print(f'    {body}')
        
def determineType(content, inferFileAllowed=False):
    if CLIPBOARD_HAS_FILE_HANDLER:
        # that means there is a file copied to the clipboard, return that and the path
        return FILE
    
    if inferFileAllowed:
        # infer if it is a file path and then make file
        path = content
        for q in [ '"', "'" ]:
            if path[0] == q:
                path = path[1:-1]
        
        if os.path.exists(path):
            return FILE

    # infer if it is a link
    for p in ['http://', 'https://', 'www.']:
        if content.startswith(p):
            return LINK
        
    for p in ['.com', '.ca', '.org']:
        if content.endswith(p):
            return LINK

    return TEXT

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
        global HEADLESS
        HEADLESS = False
        args = sys.argv[1:]

        HEADLESS = checkFlags(args, flag="--headless")
        forceText, filePathCopied, useLatestTempFile = checkFlags(args, flags=("--forceText", "--filePathCopied", "--latestTempFile"))

        pb = getPushBullet()
        
        pushFunction = {
            str(TEXT) : pb.pushNote,
            str(LINK) : pb.pushLink,
            str(FILE) : pb.pushFile
        }

        somethingPushed = False

        if CLIPBOARD_CONTENT is None:
            notify("No content to push")
            return 0

        for content in CLIPBOARD_CONTENT:
            pushType = -1
            if content == '':
                continue

            if useLatestTempFile:
                # pushing latest file in temp
                content = latestFileInTemp()
                pushType = FILE

            elif forceText:
                # treat anything copied as text
                pushType = TEXT
            
            elif filePathCopied:
                pushType = FILE

            if pushType == -1:
                pushType = determineType(content, inferFileAllowed=False)

            # if its a file, then remove any quotes in the file path name
            if pushType == FILE:
                content = content.replace('"', '').replace("'", "")

            notifAttachment = None
            notifs = {
                str(TEXT) : ("Text pushed successfully", content),
                str(LINK) : ("Link pushed successfully", content),
                str(FILE) :  ("" if pushType != FILE  else "File ({}) pushed successfully".format(os.path.split(content)[1]), "Filepath: {}".format(content) )
            }

            if couldBeScreenshot:
                notifs[str(FILE)] = ("Screenshot pushed successfully", '')
            
            # call the relevant push function
            pushFunction[str(pushType)](content)

            # notify user with notify function
            notifInfo = notifs[str(pushType)]
            notify(notifInfo[0], body=notifInfo[1], filePath=notifAttachment)

            somethingPushed = True

        if not somethingPushed:
            notify("No content to push")

    except Exception as e:
        from shared import handleError
        handleError(e, HEADLESS)

    

if __name__ == "__main__":
    sys.exit(main())