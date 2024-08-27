# pull from clip board first, doing it immediately to improve script speed
import sys
from os import path, remove
import win32clipboard as cb
from enum import Enum
from contextlib import contextmanager
from urllib.parse import urlparse, unquote
from urllib.request import url2pathname

script_loc_dir = path.split(path.realpath(__file__))[0]
if script_loc_dir not in sys.path:
    sys.path.append(script_loc_dir)
from scripts.PushBullet import PushType
from scripts.shared import checkFlags, getPushBullet, getArgumentForFlag, isLink, setHeadless, notify, config_notif, config_working_files, TEMP_DIRECTORY

config_notif('PC PushBullet', path.join(script_loc_dir, 'pushbullet-icon.ico'))
config_working_files(script_loc_dir)

class ClipboardContentType(Enum):
    FILE_PATH = 0
    TEXT = 1

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
    :return: (content, type, bool) : Where content is the clipboard data and a type is a clipboard data type,
    bool -> If pushing an image copied to the clipboard
    """

    pushingCopiedImage = False

    with clipboardOpen():
        contentIsFilePointer = cb.IsClipboardFormatAvailable(cb.CF_HDROP)
        if contentIsFilePointer:
            # get the file path as the clipboard item
            item = cb.GetClipboardData(cb.CF_HDROP)[0]
            return item, ClipboardContentType.FILE_PATH, pushingCopiedImage

        # try to get thing copied to clipboard
        # causes exception if an image is copied e.g. like a screenshot
        try:
            item = cb.GetClipboardData()
            return item, ClipboardContentType.TEXT, pushingCopiedImage
        except TypeError:
            pass

    pushingCopiedImage = True

    from PIL import ImageGrab
    tempImagePath = f"{TEMP_DIRECTORY}\\screenshot.png"
    img = ImageGrab.grabclipboard()
    img.save(tempImagePath)

    return tempImagePath, ClipboardContentType.FILE_PATH, pushingCopiedImage


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


def lastChangedFileInDir(folder: str):
    """
    Returns the latest file in the folder, if no files are in the directory then it returns none
    """
    import glob
    # get the list of files in the log directory
    list_of_files = glob.glob(f'{folder}\\*')

    if len(list_of_files) == 0:
        return None

    # get the c time of each file and use that as the key to order the list
    # and identify the maximum
    latest_file = max(list_of_files, key=path.getmtime)
    return path.join(folder, latest_file)


def latestFileInTemp():
    return lastChangedFileInDir(TEMP_DIRECTORY)


def doPush(pushType, item: str, pushingStagingFile=False, pushingCopiedImage=False):
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

            if pushingCopiedImage:
                notify(
                    'Copied Image pushed successfully'
                )

            elif pushingStagingFile:
                # notify and delete staging file
                remove(filepath)
                notify(
                    'File {} pushed successfully from staging'.format(path.split(filepath)[1]),
                    'The file has been deleted from staging'
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
        headless, isText, itemIsLink, isFile, pushLatestTempFile, convertFileURI, testing = checkFlags(
            args,
            flags=(
                "--headless", "--text", "--link", "--file", "--latestTempFile", "--convertFileURI", "--testing"
            ))

        setHeadless(headless)

        argFlagValue = getArgumentForFlag(args, "-arg")
        stagingDir = getArgumentForFlag(args, '-staging')
        stagingFile = None
        latestTempFile = None

        if stagingDir is not None:
            if not path.exists(stagingDir):
                raise Exception(f'Staging directory: "{stagingDir}" does not exist')

            stagingFile = lastChangedFileInDir(stagingDir)
            if stagingFile is None:
                raise Exception(f'No file found in staging directory: "{stagingDir}"')

        if pushLatestTempFile:
            latestTempFile = latestFileInTemp()
            if latestTempFile is None:
                raise Exception(f'No file in temp directory: {TEMP_DIRECTORY} to push')


        item, itemContentType = None, None
        pushingCopiedImage = False
        pushType = -1

        # default is copy to clipboard
        if argFlagValue is not None:
            item = argFlagValue

        elif stagingFile is not None:
            item = stagingFile

        elif latestTempFile is not None:
            item = latestTempFile

        else:
            item, itemContentType, pushingCopiedImage = getClipboardContent()

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
        if (isFile or
                latestTempFile is not None or
                stagingFile is not None or
                convertedURI is not None or
                itemContentType == ClipboardContentType.FILE_PATH):

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
        # print(stagingFile)
        # print(stagingDir)
        # input('')
        doPush(pushType, item, pushingStagingFile=stagingFile is not None, pushingCopiedImage=pushingCopiedImage)
        return 0

    except Exception as e:
        from scripts.shared import handleError
        handleError(e, headless)


if __name__ == "__main__":
    sys.exit(main())