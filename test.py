# """
# this is an example how to implement the callback feature in winotify
# """
# import os.path
# import random
# import string
# import time
# import sys

# import winotify

# # instantiate Notifier and Registry class
# app_id = "winotify test"
# app_path = os.path.abspath(__file__)

# r = winotify.Registry(app_id, winotify.PY_EXE, app_path, force_override=True)
# notifier = winotify.Notifier(r)


# @notifier.register_callback
# def do_somethin():
#     print('yo hey')
#     for x in range(3, 0, -1):
#         print(f"toast in {x} secs")
#         time.sleep(1)

#     toast = notifier.create_notification("a new notification", "this is called from another thread",
#                                          launch=quit_)
#     toast.add_actions("Clear all")
#     toast.show()


# @notifier.register_callback(run_in_main_thread=True)  # register quit func
# def quit_():
#     # this wont work if called from another thread
#     print('YESSSSSS')
#     sys.exit()


# @notifier.register_callback
# def spam():
#     for i in range(3):
#         rand = ''.join(random.choice(string.ascii_letters) for _ in range(10))  # random toast body
#         t = notifier.create_notification(f"spam motification {i}", rand)
#         t.add_actions("clear all", clear)
#         # t.add_actions("sys.exit", notifier.callback_to_url(sys.exit))
#         t.show()
#         time.sleep(1)

# def main():
#     # no need to specify app_id every time
#     toast = notifier.create_notification("a notification", 'a notification test with callback',
#                                          launch=do_somethin)
#     # generic url still works
#     toast.add_actions("Open Github", "https://github.com/versa-syahptr/winotify")
#     toast.add_actions("Quit app", quit_)
#     toast.add_actions("spam", spam)
#     toast.show()

#     print(toast.script)


# @notifier.register_callback
# def clear(): notifier.clear()


# if __name__ == '__main__':
#     notifier.start()
#     main()

#     while True:
#         notifier.update()
#         time.sleep(1)
#         print("i'm running")

from winotify import Notification
import traceback
import os

def notify(title, body=""):
    path = r"C:\Users\omnic\local\temp\EnitreCode.ino"
    path = "file:///{}".format(path.replace("\\", "/"))
    toast = Notification('test', title, msg=body, icon=r"C:\Users\omnic\local\GitRepos\pushbullet-pc-integration\pushbullet-icon.png")
    toast.add_actions(label="Log file", launch=path)
    toast.show()


def exceptionNofication(appId, errorObj, logFilePath):
    title = 'An error occured.'
    body = str(errorObj)
    logFilePath = os.path.abspath(logFilePath)
    path = "file:///{}".format(logFilePath.replace("\\", "/"))

    toast = Notification(appId, title, msg=body, icon=r"C:\Users\omnic\local\GitRepos\pushbullet-pc-integration\pushbullet-icon.png")
    toast.add_actions(label="Open log file", launch=path)
    toast.show()

try:
    1/0 
except Exception as e:
    exceptionNofication("test", e, "./.gitignore")