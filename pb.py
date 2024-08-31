import sys
import keyring
import argparse
from enum import Enum
from os import path, getcwd

import pyperclip

script_loc_dir = path.split(path.realpath(__file__))[0]
if script_loc_dir not in sys.path:
    sys.path.append(script_loc_dir)

from scripts.shared import getPushBullet, isLink, setHeadless, notify, getAcessToken, setAccessToken, CRED_SERVICE_NAME
from pc_pushbullet import getClipboardContent, ClipboardContentType, is_file_uri, file_uri_to_file_path
from pc_pullbullet import openInBrowser, openTextWithOS, isCopyableImage, makeFileContainerFromPush, FileContainer, \
    copyImageToClipboard
from scripts.PushBullet import PushType

setHeadless(False)

class ClipAsType(Enum):
    AUTO = "auto"
    NOTE = "note"
    FILE = "file"
    LINK = "link"

def print_token_howtos():
    print(f'Configured Acess Token: "{getAcessToken()}"')
    print(f'Access Token is saved as a Generic Windows Credential under {CRED_SERVICE_NAME}')
    print('Access Token can either be edited in Windows Credential Manager or by running "pb -token <token>" or "pb --configure"')

def ask_for_access_token():
    print('Your access token is required to access your PushBullet account. You can acquire an access token through your account settings.')
    accessToken = input('Paste PushBullet Access Token: ').strip()
    setAccessToken(accessToken)
    print_token_howtos()

def print_token_information():
    token = getAcessToken()
    if token is None:
        print('No access token has been configured')
        print('Set an access token using "pb -set-token <token>" or "pb --configure"')
        return

    print_token_howtos()

def getTypeForValString(enumType, valStr: str):
    valStr = valStr.lower()
    listOfTypes = list(enumType.__members__.values())
    for t in listOfTypes:
        if valStr == t.value:
            return t
    raise Exception(f'Unknown type "{valStr}" for type list: {listOfTypes}')


def err(message: str, code:int =-1):
    notify("Error", message)
    sys.exit(code)

def interpretClipboard(item, contentType:ClipboardContentType, ct:ClipAsType):
    if contentType == ClipboardContentType.FILE_PATH:
        if ct == ClipAsType.LINK:
            err(f'Cannot convert file path "{item}" to link')
        elif ct == ClipAsType.NOTE:
            return item, ClipAsType.NOTE
        else:
            # Clip as file, or clip as auto
            return item, ClipAsType.FILE

    elif contentType == ClipboardContentType.TEXT:
        if ct == ClipAsType.NOTE:
            return item, ClipAsType.NOTE

        elif ct == ClipAsType.LINK:
            return item, ClipAsType.LINK

        elif ct == ClipAsType.FILE:
            fp = item
            if is_file_uri(fp):
                fp = file_uri_to_file_path(fp)
            return fp, ClipAsType.FILE

        else: # auto
            if is_file_uri(item):
                item = file_uri_to_file_path(item)
                return item, ClipAsType.FILE

            return item, ClipAsType.LINK if isLink(item) else ClipAsType.NOTE

def push(file:str = None, link:str = None, note:str = None, title:str = None, clipAs:ClipAsType = None):
    pushingCopiedImage = False
    if clipAs is not None or (file is None and link is None and note is None):
        if clipAs == ClipAsType.AUTO:
            istr = "Automatic interpretation"
        else:
            istr = f"Interpreting as {clipAs.value}"

        print(f"Pushing From Clipboard, {istr}")
        item, contentType, pushingCopiedImage = getClipboardContent()
        item, clipAs = interpretClipboard(item, contentType, clipAs)

        match clipAs:
            case ClipAsType.NOTE:
                note = item
            case ClipAsType.LINK:
                link = item
            case ClipAsType.FILE:
                file = item
            case _:
                raise Exception(f"Invalid ClipAsType: {clipAs}")

    pb = getPushBullet()

    if file is not None:
        if is_file_uri(file):
            file = file_uri_to_file_path(file)

        file = path.abspath(file)
        if not path.exists(file):
            err(f"Selected file '{file}' does not exist")

        pb.pushFile(file)

        if pushingCopiedImage:
            notify(
                'Copied Image pushed successfully'
            )
        else:
            notify(
                'File {} pushed successfully'.format(path.split(file)[1]),
                f'Filepath: {file}'
            )

    elif link is not None:
        pb.pushLink(link, title=title, message=note)
        notify(
            'Link pushed successfully',
            link
        )

    elif note is not None:
        pb.pushText(note, title=title)
        notify(
            'Note pushed successfully',
            note
        )

    else:
        err("No content was detected to push")



def handleLink(link, openLink=False):
    if openLink:
        notify('Opening link in browser')
        openInBrowser(link)
    else:
        pyperclip.copy(link)
        notify('Link copied to clipboard', link)


def handleNote(note, openNote):
    if openNote:
        openTextWithOS(note)
        return

    # Default behaviour: Copy to clipboard
    pyperclip.copy(note)
    notify(
        'Note has been copied to your clipboard',
        str(note)
    )

def handleFile(fc: FileContainer, saveTo:str = None, openFile=False, copyFile=False):
    if copyFile:
        if not isCopyableImage(fc.ext):
            err("Non-image files cannot be copied to clipboard")
        copyImageToClipboard(fc.ext, fc.bytes)
        notify(f'Image {fc.name} has been copied to your clipboard')

    elif openFile:
        notify(f'Opening {fc.name}...')
        openInBrowser(fc.url)

    else:
        if saveTo is None:
            saveTo = path.join(getcwd(), fc.name)

        saveTo = path.abspath(saveTo)

        with open(saveTo, 'wb') as file:
            file.write(fc.bytes)

        msg = f'Destination: {saveTo}'

        saveExt = path.splitext(saveTo)[1].replace('.', '')


        if saveExt != fc.ext:
            msg += f'\nWarning: Save extension ({saveExt}) does not match pushed file extension ({fc.ext})'

        notify(f'File "{fc.name}" saved', msg)


def pull(saveTo: str=None, copyItem: bool = False, openItem: bool = False):
    pushItem = getPushBullet().pull(1)[0]
    match pushItem.type:
        case PushType.TEXT:
            if isLink(pushItem.body):
                handleLink(pushItem.body, openItem)
            else:
                handleNote(pushItem.body, openItem)

        case PushType.LINK:
            handleLink(pushItem.url, openItem)

        case PushType.FILE:
            handleFile(makeFileContainerFromPush(pushItem), saveTo=saveTo, openFile=openItem, copyFile=copyItem)

        case _:
            raise Exception('Unidentified type {}'.format(pushItem['type']))


def peekLink(link):
    notify('Link last pushed', body=link)

def peek():
    pushItem = getPushBullet().pull(1)[0]
    match pushItem.type:
        case PushType.TEXT:
            if isLink(pushItem.body):
                peekLink(pushItem.body)
            else:
                notify('Note last pushed', body=pushItem.body)

        case PushType.LINK:
            peekLink(pushItem.url)

        case PushType.FILE:
            fc = makeFileContainerFromPush(pushItem)
            notify('File last pushed', f'Name:\n{fc.name}\nURL:\n{fc.url}')

        case _:
            raise Exception('Unidentified type {}'.format(pushItem['type']))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-push',
        '-push',
        action='store_true',
        help='Push content to PushBullet. By default pushes content from clipboard with automatic interpretation unless flags specify otherwise'
    )

    parser.add_argument(
        '-pull',
        '-pull',
        action='store_true',
        help='Pull content from PushBullet'
    )

    parser.add_argument(
        '-peek',
        '-peek',
        action='store_true',
        help='Peek at the last pushed item to PushBullet'
    )

    parser.add_argument(
        "-clipas",
        required=False,
        type=str,
        metavar='<string>',
        help='Used with -push, Specifies how to interpret clipboard content for pushing. Can be "file", "link", "note" or "auto"'
    )

    parser.add_argument(
        '-clip',
        '-clip',
        action='store_true',
        help='Used with -push, pushes content from clipboard with auto interpretation (equivalent to -clipas "auto")'
    )

    parser.add_argument(
        "-file",
        required=False,
        type=str,
        metavar='<file path>',
        help='Specifies the source file to push to PushBullet, or the destination path to save the file pulled from PushBullet'
    )

    parser.add_argument(
        "-link",
        required=False,
        type=str,
        metavar='<url>',
        help='Specifies the URL to push to PushBullet as a link'
    )

    parser.add_argument(
        "-note",
        required=False,
        type=str,
        metavar='<string>',
        help='Specifies the note to push to PushBullet, can also be used along with -link to include a body for the URL'
    )

    parser.add_argument(
        "-title",
        required=False,
        type=str,
        metavar='<string>',
        help='Specifies the title of the note to push to PushBullet, can also specify title of link message when used with -link'
    )

    parser.add_argument(
        '-copy',
        '-copy',
        action='store_true',
        help='Used with -pull, copies pushed links, notes and images to your clipboard. Other file types are not supported.'
    )

    parser.add_argument(
        '-view',
        '-view',
        action='store_true',
        help="Used with -pull, opens pushed links and files in your computer's browser"
    )

    parser.add_argument(
        '--headless',
        '--headless',
        action='store_true',
        help="No output to console, notifications are sent through windows"
    )

    parser.add_argument(
        "-set-token",
        required=False,
        type=str,
        metavar='<string>',
        help='Sets the PushBullet access token used by the WinPushBullet services'
    )

    parser.add_argument(
        '--configure',
        '--configure',
        action='store_true',
        help="User input interface for configuring WinPushBullet services"
    )

    parser.add_argument(
        '--get-token',
        '--get-token',
        action='store_true',
        help="Prints access token in use"
    )

    options = parser.parse_args()

    if options.configure:
        ask_for_access_token()
        return 0

    if options.headless:
        setHeadless(True)

    if options.get_token:
        print_token_information()
        return 0

    if options.set_token is not None:
        setAccessToken(options.set_token)
        print_token_information()
        return 0

    clipAs = None
    if options.clip:
        clipAs = ClipAsType.AUTO

    if options.clipas is not None:
        typeVals = [t.value for t in list(ClipAsType.__members__.values())]
        if options.clipas not in typeVals:
            err(f"Invalid argument for -clipas, must be one of the following: {', '.join(typeVals)}")

        clipAs = getTypeForValString(ClipAsType, options.clipas)


    if options.peek:
        peek()
    elif options.push:
        push(file=options.file, link=options.link, note=options.note, title=options.title, clipAs=clipAs)
    elif options.pull:
        pull(saveTo=options.file, copyItem=options.copy, openItem=options.view)
    else:
        err("No action provided")


if __name__ == "__main__":
    sys.exit(main())