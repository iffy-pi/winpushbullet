import sys
import requests
import os
import mimetypes
import time
import json
import datetime
from enum import Enum

def prettify(d: dict) -> str:
    return json.dumps(d, indent=4)

class PushBulletException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class exceptions:
    class BadServerResponseError(PushBulletException):
        '''Thrown when PushBullet server response is not successful, returns information about the response if available'''
        def __init__(self, code, message=None):
            super().__init__('Code: {}{}'.format(code, ', Response: "{}"'.format(message) if message is not None else ''))


    class InvalidParameters(PushBulletException):
        '''Thrown when given method parameters are invalid or inadequate'''
        def __init__(self, msg):
            super().__init__(msg)

    class InvalidConfiguration(PushBulletException):
        '''Thrown when method encounters an error with the provided parametes'''
        def __init__(self, msg):
            super().__init__(msg)

    class UnreachableServerAddress(PushBulletException):
        '''Thrown when given server path is unreachable, i.e. outside address bounds'''
        def __init__(self, address):
            super().__init__(f'Provided address "{address}" is unreachable!')

    class InvalidServerAddress(PushBulletException):
        def __init__(self, address):
            super().__init__(f'Provided address "{address}" is invalid! Addresses must be absolute!')

class PushType(Enum):
    TEXT = 0
    LINK = 1
    FILE = 2

class PushObject:
    """
    Class used for managing PushObject
    A PushType.Text object will use:
    - title : Message title (None if not present)
    - body: Message body

    A PushType.LINK object will use:
    - title: Link title (None if not present)
    - url : Link URL
    - body: Link body (None if not present)

    A PushType.FILE object will use:
    - filename: The name of the file
    - fileURL: The URL of the file
    - title : If there is a title included, None otherwise

    """
    def __init__(self, pushType:PushType, title:str=None, url:str=None, body:str=None, filename:str=None, fileURL:str=None):
        self.type = pushType
        self.title = title
        self.url = url
        self.body = body
        self.fileURL = fileURL
        self.filename = filename

    def getType(self):
        return self.type

    def getFileBinary(self) -> bytes:
        if self.fileURL is None:
            raise Exception('No file url!')

        resp = requests.get(self.fileURL)
        return resp.content

    def __str__(self):
        propList = [f'type={self.type}']

        propsToCheck = [
            (self.title, 'title'),
            (self.body, 'body'),
            (self.url, 'url'),
            (self.filename, 'filename'),
            (self.fileURL, 'fileURL')
        ]

        for val, key in propsToCheck:
            if val is not None:
                propList.append(f'{key}={val}')

        return 'PushObject({})'.format(", ".join(propList))



class PushBullet:
    PUSHBULLET_API = 'https://api.pushbullet.com/v2'

    def __init__(self, accessToken, premium=False):
        self.__accessToken = accessToken
        self.premium = premium

    def __dateTimeToUnix(date: datetime.datetime):
        return int(time.mktime(date.timetuple()))
    
    def __successCheck(response:requests.Response, raiseException=True) -> bool:
        # based on https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
        if not (200 <= response.status_code <= 299):
            if raiseException:
                # raise a bad server response error
                try:
                    msg = response.json()
                except requests.exceptions.JSONDecodeError:
                    msg = None
                raise exceptions.BadServerResponseError(response.status_code, message=msg)
            return False 
        return True

    def __requestHeaders(self):
        return {
                'Access-Token': self.__accessToken
            }

    def __makePushRequest(self, pushBody:dict) -> requests.Response:
        return requests.post(
            f'{PushBullet.PUSHBULLET_API}/pushes',
            headers={
                'Access-Token': self.__accessToken
            },
            json=pushBody)

    def pushText(self, body, title:str=None):
        if body == '':
            raise exceptions.InvalidConfiguration(f'Empty Body!')
        
        # if it is greater than 63 kb, to big for JSON send as file
        if ( sys.getsizeof(body) / 1024) > 63:
            title = title if title is not None else "Pushed Text"
            self.pushFileContents(body, f"{title}.txt")
            return
        
        pushBody = {
            'type': 'note',
            'body': body
        }

        if title is not None and title != '':
            pushBody['title'] = title

        resp = self.__makePushRequest(pushBody)
        PushBullet.__successCheck(resp)

    def pushLink(self, url, title:str=None, message:str=None):
        if url == '':
            raise exceptions.InvalidConfiguration(f'Empty URL!')
        
        pushBody = {
            'type': 'link',
            'url' : url,
        }

        if title is not None and title != '':
            pushBody['title'] = title

        if message is not None and message != '':
            pushBody['body'] = message

        resp = self.__makePushRequest(pushBody)
        PushBullet.__successCheck(resp)

    def pushFileContents(self, fileContents, filename):
        mimeType, _ = mimetypes.MimeTypes().guess_type(filename)

        # check if its under the limit
        if not self.premium:
            # checks if file is greater than 25 MB
            if ( (sys.getsizeof(fileContents) +33) / (1024*1024)) > 25:
                raise exceptions.InvalidConfiguration('File size is too big!')
            
        reqHeaders = self.__requestHeaders()

        # make upload request
        # by here should have filename, file_mime_type, file_contents
        response = requests.post(
            '{}/upload-request'.format(PushBullet.PUSHBULLET_API),
            headers = reqHeaders,
            json = {
                'file_name': filename,
                'file_type': mimeType,
            }
        )

        PushBullet.__successCheck(response)

        uploadResp = response.json()

        upload_url = uploadResp['upload_url']

        response = requests.post(
            upload_url,
            headers = reqHeaders,
            files = {
                'file' : fileContents
            }
        )
        
        PushBullet.__successCheck(response)

        # populate push body
        pushBody = {
            'type': 'file',
            'file_name': uploadResp['file_name'],
            'file_type': uploadResp['file_type'],
            'file_url': uploadResp['file_url'],
        }

        resp = self.__makePushRequest(pushBody)
        PushBullet.__successCheck(resp)


    def pushFile(self, filepath, newName:str=None):
        '''
        New name is just <filename>.<fileext>
        '''
        # check if the file exists
        if not os.path.exists(filepath):
            raise exceptions.InvalidConfiguration(f'File "{filepath}" does not exist!')
        
        with open(filepath, 'rb') as file:
            fileContents = file.read()

        filename = os.path.split(filepath)[1]
        if newName is not None:
            filename = newName

        self.pushFileContents(fileContents, filename)

    def getPushType(responsePushType: str):
        ty = responsePushType.lower()
        if ty == 'note':
            return PushType.TEXT
        if ty == 'link':
            return PushType.LINK
        if ty == 'file':
            return PushType.FILE
        raise Exception(f'Unknown Push Type in response: "{responsePushType}"')
        
    def pull(self, limit: int = 1, modifiedAfter:datetime.datetime=None) -> list[PushObject]:
        """
        Pulls pushes from the PushBullet server
        :param limit : Sets the maximum pushes to fetch, by default it is onlu one
        :param modifiedAfter : Only fetch pushes modified after a specific date and time
        :return  the list of pushes
        """
        pushURL = f'{PushBullet.PUSHBULLET_API}/pushes?limit={limit}'

        if modifiedAfter is not None:
            pushURL = '{}modified_after={}'.format(pushURL, PushBullet.__dateTimeToUnix(modifiedAfter))

        response = requests.get(
            pushURL,
            headers=self.__requestHeaders()
        )

        PushBullet.__successCheck(response)
        resp = response.json()

        pushes = []
        for push in resp['pushes']:
            ty = PushBullet.getPushType(push['type'])
            pobj = None
            if ty == PushType.TEXT or ty == PushType.LINK:
                pobj = PushObject(ty, title=push.get('title'), url=push.get('url'), body=push.get('body'))

            elif ty == PushType.FILE:
                # its text that was larger than limit so pushed as file
                # automatically push to text
                if push['file_name'] == 'Pushed Text.txt':
                    resp = requests.get(push['file_url'])
                    fileBinary = resp.content
                    pobj = PushObject(PushType.TEXT, title=push.get('title'), body=fileBinary)

                else:
                    pobj = PushObject(PushType.FILE, title=push.get('title'), body=push.get('body'), filename=push['file_name'], fileURL=push['file_url'])

            else:
                raise Exception(f'Unhandled Push Type: "{ty}"')

            pushes.append(pobj)
        return pushes
    
    
def main():
    pass

if __name__ == '__main__':
    sys.exit(main())