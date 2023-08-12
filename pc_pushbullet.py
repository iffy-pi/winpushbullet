# pull from clip board first, doing it immediately to improve script speed
import win32clipboard as cb
CLIPBOARD_ITEM = None
couldBeScreenshot = False

cb.OpenClipboard()
FILE_COPIED = cb.IsClipboardFormatAvailable(cb.CF_HDROP)

if FILE_COPIED:
    CLIPBOARD_ITEM = cb.GetClipboardData(cb.CF_HDROP)[0]
else:
    try:
        CLIPBOARD_ITEM = cb.GetClipboardData()
    except TypeError:
        CLIPBOARD_ITEM = None
        couldBeScreenshot = True
cb.CloseClipboard()

if couldBeScreenshot:
    # screenshots copied to clipboard cause this exception
    # grab the screenshow with Pillow, save to file and return the file handler
    from PIL import ImageGrab
    tempSc = r"C:\Users\omnic\local\temp\screenshot.png"
    img = ImageGrab.grabclipboard()
    img.save(tempSc)
    CLIPBOARD_ITEM = tempSc
    FILE_COPIED = True

import sys
import os

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]
if script_loc_dir not in sys.path:  
    sys.path.append(script_loc_dir)
from shared import checkFlags, getPushBullet, isLink, setHeadless, notify

TEXT = 0
LINK = 1
FILE = 2
        
def determineType(content, inferFileAllowed=False):
    if FILE_COPIED:
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
    if isLink(content):
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

def doPush(pushType, item:str):
    pb = getPushBullet()
    match pushType:
        case 0: # TEXT
            pb.pushNote(item)
            notify(
                'Text pushed successfully',
                item
            )

        case 1: # LINK
            pb.pushLink(item)
            notify(
                'Link pushed successfully',
                item
            )

        case 2: # FILE
            filepath = item.replace('"', '').replace("'", "")

            pb.pushFile(filepath)

            if couldBeScreenshot:
                notify(
                    'Screenshot pushed successfully'
                )
            else:
                notify(
                    'File {} pushed succcessfully'.format(os.path.split(filepath)[1]),
                    f'Filepath: {item}'
                )


def main():
    try:
        args = sys.argv[1:]
        
        headless = False

        # check for flags
        headless, forceText, filePathCopied, useLatestTempFile = checkFlags(args, flags=("--headless", "--forceText", "--filePathCopied", "--latestTempFile"))
        setHeadless(headless)

        item = CLIPBOARD_ITEM
        pushType = -1

        # apply arguments
        if forceText:
            # treat anything copied as text
            pushType = TEXT
        
        elif filePathCopied:
            pushType = FILE
        
        elif useLatestTempFile:
            # pushing latest file in temp
            item = latestFileInTemp()
            pushType = FILE

        # check if there is content to push
        if item is None or item == '':
            notify("No content to push")
            return 0

        if pushType == -1:
            pushType = determineType(item, inferFileAllowed=False)

        doPush(pushType, item)    
    except Exception as e:
        from shared import handleError
        handleError(e, headless)

    

if __name__ == "__main__":
    sys.exit(main())