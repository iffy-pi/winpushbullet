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
from scripts.shared import checkFlags, getPushBullet, getArgumentForFlag, isLink, setHeadless, notify


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


def file_uri_to_file_path(uri):
    """
    Takes a file URI e.g. file:///C:/Users/omnic/local/temp/Payment%20Proof.pdf and converts it to a file URL
    """
    try:
        parsed = urlparse(uri)
        host = "{0}{0}{mnt}{0}".format(path.sep, mnt=parsed.netloc)
        filepath = str(path.normpath(
            path.join(host, url2pathname(unquote(parsed.path)))
        ))
        return filepath if path.exists(filepath) else None
    except Exception:
        return None


def is_file_uri(text: str):
    if type(text) != str:
        return False
    return text.startswith('file:///')


def sanitize_file_path(fp):
    return fp.replace('"', '').replace("'", "")


def valid_file_path(fp):
    return path.exists(fp) and not path.isdir(fp)


def latestFileInTemp():
    import glob
    # get the list of files in the log directory
    dd = TEMP_DIRECTORY
    list_of_files = glob.glob(f'{dd}\\*')
    # get the c time of each file and use that as the key to order the list
    # and identify the maximum
    latest_file = max(list_of_files, key=path.getmtime)
    return path.join(dd, latest_file)


def doPush(pushType, item: str):
    pb = getPushBullet()
    match pushType:
        case PushType.TEXT:  # TEXT
            pb.pushText(item)
            notify(
                'Text pushed successfully',
                item
            )

        case PushType.LINK:  # LINK
            pb.pushLink(item)
            notify(
                'Link pushed successfully',
                item
            )

        case PushType.FILE:  # FILE
            filepath = item
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


def infer_type(item):
    if type(item) != str:
        raise Exception('Unknown item type')

    if isLink(item):
        return item, PushType.LINK

    # check if it is a file uri
    if is_file_uri(item):
        fp = file_uri_to_file_path(item)
        if fp is not None:
            return fp, PushType.FILE

    # check if it can be evaluated to a file path
    fp = sanitize_file_path(item)
    if valid_file_path(fp):
        return fp, PushType.FILE

    # otherwise return as text
    return item, PushType.TEXT


def main():
    headless = True
    try:
        args = sys.argv[1:]
        # check for flags
        headless, isText, itemIsLink, isFile, isLatestTempFile, convertFileURI, testing = checkFlags(
            args,
            flags=(
                "--headless", "--text", "--link", "--file", "--latestTempFile", "--convertFileURI", "--testing"
            ))

        setHeadless(headless)

        argFlagValue = getArgumentForFlag(args, "-arg")

        item, itemContentType = None, None
        pushType = -1

        # default is copy to clipboard
        if argFlagValue is not None:
            item = argFlagValue

        elif isLatestTempFile:
            item = latestFileInTemp()

        else:
            item, itemContentType = getClipboardContent()

        # check if there is content to push
        if item is None or item == '':
            notify("No content to push")
            return 0

        # If convert file URI is set, do it first
        convertedURI = None
        if (convertFileURI or isFile) and is_file_uri(item):
            convertedURI = file_uri_to_file_path(item)
            if convertedURI is not None:
                item = convertedURI

        # Set types
        if isFile or isLatestTempFile or convertedURI is not None or itemContentType == ClipboardContentType.FILE_PATH:
            item = sanitize_file_path(item)

            if not valid_file_path(item):
                raise Exception(f'Invalid file path: {item}')

            pushType = PushType.FILE

        elif itemIsLink:
            pushType = PushType.LINK

        elif isText:
            pushType = PushType.TEXT

        else:
            # default type inferencing
            item, pushType = infer_type(item)

        # print(f'Item: {item}')
        # print(f'Type: {pushType}')
        # input('')
        doPush(pushType, item)
        return 0

    except Exception as e:
        from scripts.shared import handleError
        handleError(e, headless)


if __name__ == "__main__":
    sys.exit(main())