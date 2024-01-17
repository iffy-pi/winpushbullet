# pull from clip board first, doing it immediately to improve script speed
import sys
from os import path
import win32clipboard as cb
from enum import Enum
from contextlib import contextmanager
from urllib.parse import urlparse, unquote
from urllib.request import url2pathname

script_loc_dir = path.split(path.realpath(__file__))[0]
if script_loc_dir not in sys.path:
    sys.path.append(script_loc_dir)
from config.userconfig import TEMP_DIRECTORY
from scripts.PushBullet import PushType
from scripts.shared import checkFlags, getPushBullet, isLink, setHeadless, notify



def uri_to_path(uri):
    """
    Takes a file URI e.g. file:///C:/Users/omnic/local/temp/Payment%20Proof.pdf and converts it to a file URL
    """
    parsed = urlparse(uri)
    host = "{0}{0}{mnt}{0}".format(path.sep, mnt=parsed.netloc)
    return str(path.normpath(
        path.join(host, url2pathname(unquote(parsed.path)))
    ))


class ClipboardContentType(Enum):
    FILE_PATH = 0
    TEXT = 1

PUSHING_IMAGE_COPIED_TO_CLIPBOARD = False

@contextmanager
def clipboardOpen():
    cb.OpenClipboard()
    try:
        yield None
    finally:
        cb.CloseClipboard()

def getClipboardContent():
    """
    Gets the contents in the clipboard
    :return: (content, type) : Where content is the clipboard data and a type is a clipboard data type
    """

    with clipboardOpen():
        contentIsFilePointer = cb.IsClipboardFormatAvailable(cb.CF_HDROP)
        if contentIsFilePointer:
            # get the file path as the clipboard item
            item = cb.GetClipboardData(cb.CF_HDROP)[0]
            return item, ClipboardContentType.FILE_PATH

        # try to get thing copied to clipboard
        # causes exception if an image is copied e.g. like a screenshot
        try:
            item = cb.GetClipboardData()
            return item, ClipboardContentType.TEXT
        except TypeError:
            pass

    # Handle the image by saving it to a temp file and then returning the file path as the clipboard item
    # Also set global var
    global PUSHING_IMAGE_COPIED_TO_CLIPBOARD
    PUSHING_IMAGE_COPIED_TO_CLIPBOARD = True

    from PIL import ImageGrab
    tempImagePath = f"{TEMP_DIRECTORY}\\screenshot.png"
    img = ImageGrab.grabclipboard()
    img.save(tempImagePath)

    return tempImagePath, ClipboardContentType.FILE_PATH

def latestFileInTemp():
    import glob
    # get the list of files in the log directory
    dd = TEMP_DIRECTORY
    list_of_files = glob.glob(f'{dd}\\*')
    # get the c time of each file and use that as the key to order the list
    # and identify the maximum
    latest_file = max(list_of_files, key=path.getmtime)
    return path.join(dd, latest_file)

def doPush(pushType, item:str):
    pb = getPushBullet()
    match pushType:
        case PushType.TEXT: # TEXT
            pb.pushText(item)
            notify(
                'Text pushed successfully',
                item
            )

        case PushType.LINK: # LINK
            pb.pushLink(item)
            notify(
                'Link pushed successfully',
                item
            )

        case PushType.FILE: # FILE
            filepath = item.replace('"', '').replace("'", "")

            if not path.exists(filepath):
                raise Exception(f'File "{filepath}" does not exist')

            pb.pushFile(filepath)

            if PUSHING_IMAGE_COPIED_TO_CLIPBOARD:
                notify(
                    'Copied Image pushed successfully'
                )
            else:
                notify(
                    'File {} pushed succcessfully'.format(path.split(filepath)[1]),
                    f'Filepath: {item}'
                )


def main():
    headless = True
    try:
        args = sys.argv[1:]

        # check for flags
        contentArgs = list(args)
        headless, forceText, filePathCopied, useLatestTempFile, hasFilePathArgument, hasTextArgument , argIsFileURI, fileURICopied, testing= checkFlags(args,
            flags=("--headless", "--forceText", "--filePathCopied", "--latestTempFile","-filePathArgument", "-textArgument", "--isFileURI", "--fileURICopied", "--testing"))

        setHeadless(headless)

        item, itemContentType = None, None
        pushType = -1

        if hasFilePathArgument or hasTextArgument:
            item = args[0]
            if argIsFileURI:
                item = uri_to_path(item)

        else:
            item, itemContentType = getClipboardContent()


        # check if there is content to push
        if item is None or item == '':
            notify("No content to push")
            return 0

        # Use arguments to get the push type
        if forceText or hasTextArgument:
            # treat anything copied as text
            pushType = PushType.TEXT
        
        elif hasFilePathArgument or filePathCopied or itemContentType == ClipboardContentType.FILE_PATH:
            pushType = PushType.FILE
        
        elif useLatestTempFile:
            # pushing latest file in temp
            item = latestFileInTemp()
            pushType = PushType.FILE

        elif fileURICopied:
            item = uri_to_path(item)
            pushType = PushType.FILE

        # If we still havent determined the type, it will either be text or link
        if pushType == -1:
            if itemContentType == ClipboardContentType.TEXT:
                pushType = PushType.LINK if isLink(item) else PushType.TEXT
            else:
                raise Exception('Unknown PushType for Copied Item')

        doPush(pushType, item)    
    except Exception as e:
        from scripts.shared import handleError
        handleError(e, headless)

    

if __name__ == "__main__":
    sys.exit(main())