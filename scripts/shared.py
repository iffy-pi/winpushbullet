import os
import keyring
from winotify import Notification
from scripts.PushBullet import PushBullet
from config.userconfig import TEMP_DIRECTORY
from config.save_access_token import CRED_SERVICE_NAME, CRED_USER_NAME

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]

ERROR_LOG_FILE = f"{TEMP_DIRECTORY}\\error_logs.txt"
NOTIF_ICON = os.path.join(script_loc_dir, "pushbullet-icon.png")

def getPushBullet():
    accessToken = keyring.get_password(CRED_SERVICE_NAME, CRED_USER_NAME)
    if accessToken is None:
        text = f'''Could not find PushBullet access token
Check Credential Manager > Generic Credentials for the user "{CRED_USER_NAME}" under the service {CRED_SERVICE_NAME}.
Alternatively, reregister your access token using config.savePushBulletAccessToken'''
        raise Exception(text)

    return PushBullet(accessToken)

def setHeadless(val):
    global HEADLESS
    HEADLESS = val

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

def notify(title, body="", attachmentLabel=None, attachmentPath=None):
    if HEADLESS:
        notif(title, body=body, filePath=attachmentPath, label=attachmentLabel)
    else:
        # just print the console
        print(title)
        if body != "":
            if len(body) > 200:
                print(f'   {body[:197]}...')
            else:
                print(f'    {body}')
        if attachmentLabel is not None:
            print('Label: ', attachmentLabel)
        if attachmentPath is not None:
            print('Attached File: ', attachmentPath)


def isLink(text) -> bool:
    for p in ['http://', 'https://', 'www.']:
        if text.startswith(p):
            return True
        
    for p in ['.com', '.ca', '.org']:
        if text.endswith(p):
            return True
        
    return False

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