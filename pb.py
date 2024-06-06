import sys
import argparse
from os import path, getcwd

import pyperclip

script_loc_dir = path.split(path.realpath(__file__))[0]
if script_loc_dir not in sys.path:
    sys.path.append(script_loc_dir)

from scripts.shared import getPushBullet, isLink, setHeadless, notify
from pc_pushbullet import getClipboardContent, ClipboardContentType
from pc_pullbullet import openInBrowser, openTextWithOS, isCopyableImage, makeFileContainerFromPush, FileContainer, \
    copyImageToClipboard
from scripts.PushBullet import PushType

setHeadless(False)

def err(message: str, code:int =-1):
    notify("Error", message)
    sys.exit(code)

def push(file:str = None, link:str = None, note:str = None, title:str = None, clipboard: bool = False):
    pushingCopiedImage = False

    if clipboard or (file is None and link is None and note is None):
        print("Pushing From Clibboard...")
        item, contentType, pushingCopiedImage = getClipboardContent()
        if contentType == ClipboardContentType.TEXT:
            note = item
        elif contentType == ClipboardContentType.FILE_PATH:
            file = item
        else:
            raise Exception("Unknown content type!")

    pb = getPushBullet()

    if file is not None:
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



def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-push',
        '-push',
        action='store_true',
        help='Push content to PushBullet. By default pushes content from clipboard unless flags specify otherwise'
    )

    parser.add_argument(
        '-pull',
        '-pull',
        action='store_true',
        help='Pull content from PushBullet'
    )

    parser.add_argument(
        '-clip',
        '-clip',
        action='store_true',
        help='Used with -push, pushes content from clipboard'
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
        '-open',
        '-open',
        action='store_true',
        help="Used with -pull, opens pushed links and files in your computer's browser"
    )

    options = parser.parse_args()

    if options.push:
        push(file=options.file, link=options.link, note=options.note, title=options.title, clipboard=options.clip)
    elif options.pull:
        pull(saveTo=options.file, copyItem=options.copy, openItem=options.open)


if __name__ == "__main__":
    sys.exit(main())