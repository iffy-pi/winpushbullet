import sys
import datetime
from PushBullet import PushBullet

def main():

    # Create new pushbullet object with access token, also specify if you use premium
    accessToken = 'accesstoken'
    pb = PushBullet(accessToken, premium=False)

    # push text
    pb.pushText('This is the body', title='New title')

    # push a link
    pb.pushLink('https://google.com', title='Google Homepage')

    # push a file
    # can change the name of the file for when it is pushed
    filepath = 'example.py'
    pb.pushFile(filepath, newName='Pushed File.py')

    # to get pushes
    # takes the number of pushes to get
    # and a datetime object for when it is modified after
    # returns a list of pushes in the format
    pushes = pb.pull(2, modifiedAfter=datetime.datetime.now())

    # possible push types, i.e. the 'type' field of push object
    # PushBullet.PushType.TEXT: has dictionary fields 'body', 'title'
    # PushBullet.PushType.LINK: has dictionary fields 'url', 'title' and 'body'
    # PushBullet.PushType.FILE: has dictionary fields 'url' for file url, 'name' for file name and 'content' for file binary content

    # so to save the pushed file above to file
    # it will be the last pushed file
    ps = pushes[0]

    with open(ps['name'], 'wb') as file:
        file.write(ps['content'])

    return 0

if __name__ == "__main__":
    sys.exit(main())