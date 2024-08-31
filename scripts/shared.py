import os
import keyring
from winotify import Notification
from scripts.PushBullet import PushBullet

CRED_SERVICE_NAME = "WinPushBullet-Access-Token"
CRED_USER_NAME = "WinPushBullet"

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]

TEMP_DIRECTORY = os.path.join(script_loc_dir, 'temp')
ERROR_LOG_FILE = os.path.join(script_loc_dir, "error_logs.txt")
NOTIF_ICON = os.path.join(os.getcwd(), "pushbullet-icon.png")
NOTIF_APP_ID = 'WinPushBullet'

def config_working_files(home_dir):
    # This makes sure that when the application is built, temp and error logs will map to its program files folder
    global TEMP_DIRECTORY
    global ERROR_LOG_FILE
    TEMP_DIRECTORY = os.path.join(home_dir, 'temp')
    ERROR_LOG_FILE = os.path.join(home_dir, "error_logs.txt")

    if not os.path.exists(TEMP_DIRECTORY):
        os.makedirs(TEMP_DIRECTORY, exist_ok=True)


def getAcessToken():
    return keyring.get_password(CRED_SERVICE_NAME, CRED_USER_NAME)

def setAccessToken(token):
    keyring.set_password(
        CRED_SERVICE_NAME,
        CRED_USER_NAME,
        token
    )

def getPushBullet():
    accessToken = getAcessToken()
    if accessToken is None:
        text = f'''Could not find WinPushBullet access token in Windows Credentials. Configure your access token using "pb --configure"'''
        raise Exception(text)

    return PushBullet(accessToken)

def setHeadless(val):
    global HEADLESS
    HEADLESS = val

def checkFlags(args:list[str], flag:str=None, flags:tuple=None):
    """
    Checks the passed in args for the given flags
    If a flag is found, it is removed from the list of arguments
    :param args: The list of command line arguments
    :param flag: One flag to check against
    :param flags: A tuple of command line flags to check
    :return: If the flag argument is used, it returns a boolean value for if the flag is in the command line arguments
            If the flags argument is ued, it returns a tuple of boolean values,
            where boolean value at index i, corresponds to if flags[i] is in the command line
    """

    listOfFlagsPassedIn = flags is not None

    if not listOfFlagsPassedIn:
        if flag is None:
            raise Exception('No flags to parse!')
        flags = flag,

    results = [ False ] * len(flags)

    for i, fl in enumerate(flags):
        if fl not in args:
            continue

        # find the flag index in the list
        flInd = args.index(fl)
        results[i] = True
        # remove flag from list
        args.pop(flInd)

    if not listOfFlagsPassedIn and len(results) == 1:
        return results[0]
    
    return tuple(results)

def getArgumentForFlag(args:list[str], flag:str) -> str|None:
    """
    Returns an argument associated with a given flag,
    Expects that a flag argument comes immediately after the flag itself
    If the flag is found and argument is found, then both are removed from list of arguments
    :param args: The list of command line arguments
    :param flag: The flag to check against
    :return: Returns the found argument or None if no argument is found
    """
    if flag not in args:
        return None

    flIndex = args.index(flag)
    argIndex = flIndex + 1

    if argIndex >= len(args):
        return None

    arg = args[argIndex]

    args.pop(argIndex)
    args.pop(flIndex)
    return arg

def scriptErrNotif(errorObj, logFilePath):
    notif("An error occured", body=str(errorObj), label="See log file", filePath=logFilePath)

def config_notif(app_id, icon):
    global NOTIF_ICON
    global NOTIF_APP_ID
    NOTIF_ICON = icon
    NOTIF_APP_ID = app_id

def notif(title, body="", label="See Here", url=None, filePath=None):
    if len(body) > 135:
        body = f"{body[:135]}..."

    toast = Notification(NOTIF_APP_ID, title, msg=body, icon=NOTIF_ICON)

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
        from shutil import get_terminal_size
        dispChars = get_terminal_size().columns - 10
        # just print the console
        print(title)
        if body != "":
            if len(body) > 200:
                body = f'{body[:197]}...'

            lines = body.split('\n')
            for line in lines:
                if len(line) < dispChars:
                    print(f'\t{line}')
                    continue

                # k = 0
                # l = len(line)
                # while k < l:
                #     # First get the stopping index
                #     st = k + dispChars
                #     # Check the character, if it is not a space, then go back till we reach a space
                #     if

                for i in range(0, len(line), dispChars):
                    print(f'\t{line[i:i+dispChars]}')

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