import sys
import requests
import os
import mimetypes
import json
import shlex
import keyring

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

class PushBullet:
    PUSHBULLET_API = 'https://api.pushbullet.com/v2'
    def __init__(self, accessToken, premium=False):
        self.__accessToken = accessToken
        self.premium = premium
    
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

    def pushNote(self, body, title:str=None):
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
        if self.premium:
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

        
    def pull(self, count=1, modifiedAfter:int=None) -> list:
        pushURL = f'{PushBullet.PUSHBULLET_API}/pushes?limit={count}'

        if modifiedAfter is not None:
            pushURL = '{}&modified_after={}'.format(pushURL, modifiedAfter)


        response = requests.get(
            pushURL,
            headers=self.__requestHeaders()
        )

        PushBullet.__successCheck(response)
        resp = response.json()

        pushes = []
        for push in resp['pushes']:
            retPush = {
                'type': push['type'],
                'title': push.get('title'),
                'url': push.get('url'),
                'body': push.get('body'),
            }

            if push['type'] == 'file':
                # need to get file contents
                fileBinary = requests.get(push['file_url']).content
                retPush = {
                    'type': 'file',
                    'url': push['file_url'],
                    'name': push['file_name'],
                    'content': fileBinary
                }
            
            pushes.append(retPush)
        return pushes
    
def main():
    accessToken = keyring.get_password('api.pushbullet.com', 'omnictionarian.xp@gmail.com')
    pb = PushBullet(accessToken)

if __name__ == '__main__':
    sys.exit(main())