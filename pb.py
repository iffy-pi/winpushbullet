import sys
import os
import argparse
from PushBullet import PushBullet
import keyring

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]
if script_loc_dir not in sys.path:  
    sys.path.append(script_loc_dir)

def pull(pb:PushBullet, copyPush, openInBrowser, fname=None):
    push = pb.pull(1)[0]

    # default:
    # note and links : echo to console
    # file : saves to directory of fname, otherwise opens file dialog

    # copyPush
    # copy notes and links
    # open file dialog

    # openInBrowser
    # echo note
    # copy link
    # open file in browser

    if copyPush:
        import pyperclip

    if openInBrowser:
        import subprocess
        def brave(link):
            child = subprocess.Popen([r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", link])
    

    if push['type'] == 'note':
        if copyPush:
            pyperclip.copy(push['body'])
            print('Note copied to clipboard')
            return
        
        # default
        print(push['body'])
    
    elif push['type'] == 'link':
        if copyPush:
            pyperclip.copy(push['url'])
            print('URL copied to clipboard')
            return
        
        if openInBrowser:
            brave(push['url'])
            return
        
        # default
        print(push['url'])

    elif push['type'] == 'file':
        if openInBrowser:
            # open the url in the browser
            brave(push['url'])

        # default
        # save to file
        from FileExplorerWindow import FileExplorerWindow
        fex = FileExplorerWindow()
        
        path=os.path.split(push['name'])
        if fname is not None:
            fname = os.path.abspath(fname)
            path = os.path.split(fname)
        
        filename = fex.save(title="Save Pushed File", path=path)
        
        if filename is not None:
            with open(filename, "wb") as file:
                file.write(push['content'])
            print(f'File saved to {filename}')
        else:
            print('File not saved')

def latestFileInTemp():
    import glob
    # get the list of files in the log directory
    dd = "C:\\Users\\omnic\\local\\temp"
    list_of_files = glob.glob(f'{dd}\\*')
    # get the c time of each file and use that as the key to order the list
    # and identify the maximum
    latest_file = max(list_of_files, key=os.path.getmtime)
    return os.path.join(dd, latest_file)

def push(pb:PushBullet, text:str=None, link:str=None, filepath:str=None, title:str=None, message:str=None, fname:str=None, latestTemp:bool=False, clipBoard:bool=False ):
    # text, link and file are contents
    # title and message are optional
    # fname for push to directory

    if latestTemp:
        filepath = latestFileInTemp()

    if clipBoard:
        import win32clipboard as cb
        cb.OpenClipboard()
        hasFile = cb.IsClipboardFormatAvailable(cb.CF_HDROP)
        if hasFile:
            content = cb.GetClipboardData(cb.CF_HDROP)
        else:
            content = (cb.GetClipboardData(), ) 
        cb.CloseClipboard()

        # call on each of the items
        for c in content:
            push(pb, filepath=c, title=title, message=message, fname=fname)


    if text is not None and text != "":
        
        pb.pushNote(text, title=title)
        print("Note Pushed:")

        if len(text) > 100:
            t = text[:97]
            t += '...'
            print(t)
        else:
            print(text)
    
    elif link is not None and link != "":
        pb.pushLink(link, title=title, message=message)
        print("Link Pushed:")
        print(link)

    elif filepath is not None and filepath != "":
        filepath = os.path.abspath(filepath)
        if not os.path.exists(filepath):
            print(f"Could not find {filepath}")
            return

        newName = None
        if fname is not None:
            newName = os.path.split(fname)[1]

        pb.pushFile(filepath, newName)
        print("File Pushed{}:".format("(as {})".format(newName) if newName is not None else ""))
        print(filepath)

def printKeyInfo():
    print(
'''Push:
Ctrl + Alt + ] : Push content from clipboard, infer text, link or file path
Ctrl + Alt + ' : Push content from clipboard, always treat as text
Ctrl + Alt + / : Push latest file in C:\\Users\\local\\temp

Pull:
Ctrl + Alt + [ : Pull content, can copy to clipboard, open in browser or save to file
Ctrl + Alt + . : Pull content, always save to file if file
Ctrl + Alt + ; : Pull content, open in browser if possible''')

def main():
    
    parser = argparse.ArgumentParser()


    parser.add_argument(
        "-f",
        required=False,
        type = str,
        metavar='<file path>',
        help = "Push the file at given path"
    )

    parser.add_argument(
        "-n",
        required=False,
        type = str,
        metavar='<string>',
        help = "Pushes the given text"
    )

    parser.add_argument(
        "-l",
        required=False,
        type = str,
        metavar='<URL>',
        help = "Pushes the given text as a link"
    )

    parser.add_argument(
        "-title",
        required=False,
        type = str,
        metavar='<title>',
        help = "Title appended to the push"
    )

    parser.add_argument(
        "-msg",
        required=False,
        type = str,
        metavar='<Message>',
        help = "Message appended to the push"
    )

    parser.add_argument(
        "-fname",
        required=False,
        type = str,
        metavar='<filename/filepath>',
        help = "File name that overrides the file path given"
    )

    parser.add_argument(
        '--clip',
        '--clip',
        action='store_true',
        help='Get content from clipboard and push as text'
    )

    parser.add_argument(
        '--temp',
        '--temp',
        action='store_true',
        help='Push latest file in temp'
    )

    parser.add_argument(
        '--keys',
        '--keys',
        action='store_true',
        help='Show the hotkeys we have configured'
    )


    parser.add_argument(
        '--cpy',
        '--cpy',
        action='store_true',
        help='Pull content and copies notes and links to clipboard'
    )

    parser.add_argument(
        '--b',
        '--b',
        action='store_true',
        help='Pulls content and opens it in browser if applicabke, otherwise it will be printed to the screen'
    )

    options = parser.parse_args()

    if options.keys:
        printKeyInfo()
        return

    # default: print, note and links to screen, ask to save file
    accessToken = keyring.get_password('api.pushbullet.com', 'omnictionarian.xp@gmail.com')
    pb = PushBullet(accessToken)
    
    if (options.temp or options.clip) or any(arg is not None for arg in (options.f, options.n, options.l)):
        push(pb, options.n, options.l, options.f, title=options.title, message=options.msg, 
                fname=options.fname, latestTemp=options.temp, clipBoard=options.clip)
        return

    pull(pb, options.cpy, options.b)
    





if __name__ == '__main__':
    sys.exit(main())