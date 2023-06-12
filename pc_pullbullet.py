import sys
import keyring
from winotify import Notification
import pyperclip
import os

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]
if script_loc_dir not in sys.path:  
    sys.path.append(script_loc_dir)
from PushBullet import PushBullet

def notify(title, body):
    toast = Notification('PushBullet', title, msg=body, icon=r"C:\Users\omnic\local\GitRepos\pushbullet-pc-integration\pushbullet-icon.png")
    toast.show()


def main():
    try:
        accessToken = keyring.get_password('api.pushbullet.com', 'omnictionarian.xp@gmail.com')
        pb = PushBullet(accessToken)

        push = pb.pull(1)[0]

        if push['type'] == 'note':
            pyperclip.copy(push['body'])
            notify(
                'Text has been copied to your clipboard',
                str(push['body'])
            )

        elif push['type'] == 'link':
            pyperclip.copy(push['url'])

            msg = push['url']

            if push.get('title') is not None:
                msg = "{}\nTitle: {}".format(msg, push['title'])

            if push.get('body') is not None:
                msg = "{}\nMessage: {}".format(msg, push['body'])

            notify(
                'URL has been copied to your clipboard',
                msg
            )

        elif push['type'] == 'file':
            from FileExplorerWindow import FileExplorerWindow
            fex = FileExplorerWindow()
            if fex is not None:
                filename = fex.save(title="Save Pushed File", path=(None, push['name']))
                with open(filename, "wb") as file:
                    file.write(push['content'])

    except Exception as e:
        # something went wrong
        notify("An error occured", str(e))


if __name__ == '__main__':
    sys.exit(main())
