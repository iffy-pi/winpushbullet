import os
import sys
from winotify import Notification

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]

ERROR_LOG_FILE = r"C:\Users\omnic\OneDrive\Computer Collection\Pushbullet\error_logs.txt"
NOTIF_ICON = os.path.join(script_loc_dir, "pushbullet-icon.png")

def checkFlags(args:list, flag:str = "", flags:tuple=()):  
    usedList = False
    if len(flags) == 0:
        flags = flag,
    else:
        usedList = True

    results = []

    for fl in flags:
        res = False
        try:
            flInd = args.index(fl)
            # flag is in args lsit
            res = True

            # remove flag from list
            args.pop(flInd)    
        except ValueError:
            pass

        results.append(res)

    if not usedList and len(results) == 1:
        return results[0]
    
    return tuple(results)


def scriptErrNotif(errorObj, logFilePath):
    notif("An error occured", body=str(errorObj), label="See log file", filePath=logFilePath)

def notif(title, body="", label="See Here", url=None, filePath=None):
    if len(body) > 135:
        body = f"{body[:135]}..."

    toast = Notification('PushBullet', title, msg=body, icon=NOTIF_ICON)

    if url is not None:
        toast.add_actions(label=label, launch=url)

    if filePath is not None:
        filePath = os.path.abspath(filePath)
        path = "file:///{}".format(filePath.replace("\\", "/"))
        toast.add_actions(label=label, launch=path)

    toast.show()

def handleError(errorObj, headless):
    import traceback
    # something went wrong
    if headless:
        # save to log file first
        with open(ERROR_LOG_FILE, 'w') as f:
            f.write(traceback.format_exc())

        # do error notification
        scriptErrNotif(errorObj, ERROR_LOG_FILE)
    else:
        traceback.print_exc()