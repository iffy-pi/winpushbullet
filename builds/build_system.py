import os
import shutil
import sys
import time
import subprocess
from enum import Enum
from shutil import rmtree, copytree

BUILDS_DIRECTORY = os.path.split(__file__)[0]
PYINSTALLER = 'C:\\Python\\3.12.5\\Scripts\\pyinstaller.exe'

class Application(Enum):
    PUSHB = 0
    PULLB = 3
    PB_CLI = 2

class BuildFailure(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# relative to builds directory
app_build_info = {
    Application.PUSHB: {
        'name': 'PC_PushBullet',
        'folder': 'pc_pushbullet',
        'spec': 'pc_pushbullet.spec',
        'dist': 'pc_pushbullet\\dist\\PC_PushBullet'
    },
    Application.PULLB: {
        'name': 'PC_PullBullet',
        'folder': 'pc_pullbullet',
        'spec': 'pc_pullbullet.spec',
        'dist': 'pc_pullbullet\\dist\\PC_PullBullet'
    },
    Application.PB_CLI: {
        'name': 'pb',
        'folder': 'pb',
        'spec': 'pb.spec',
        'dist': 'pb\\dist\\pb'
    }

}

def build_application(app: Application):
    info = app_build_info[app]
    os.chdir(os.path.join(BUILDS_DIRECTORY, info['folder']))

    for f in ['build', 'dist']:
        if os.path.exists(f):
            rmtree(f)

    print(f'Building {info['name']}...')
    cmd = [PYINSTALLER, '--clean', info['spec']]
    start = time.time()
    retcode = int(subprocess.call(cmd))
    end = time.time()
    if retcode != 0:
        raise BuildFailure(f'Building {info['name']} failed. PyInstaller has non-zero return code: {retcode}')
    print(f'{info['name']} built - {(time.time() - start):.3f} seconds')


def build_installer_fn(build_pc_push, build_pc_pull, build_pb_cli):
    os.chdir(BUILDS_DIRECTORY)
    dist_srcs = []
    if build_pc_push:
        dist_srcs.append(app_build_info[Application.PUSHB])
    if build_pc_pull:
        dist_srcs.append(app_build_info[Application.PULLB])
    if build_pb_cli:
        dist_srcs.append(app_build_info[Application.PB_CLI])

    for a in dist_srcs:
        if not os.path.exists(a['dist']):
            raise BuildFailure(f'Dist folder: "{a['dist']}" does not exist despite being built')

        dest = os.path.join('fulldist', a['name'])

        if os.path.exists(dest):
            rmtree(dest)

        copytree(a['dist'], dest , dirs_exist_ok=True)



    nsis_path = r'C:\Program Files (x86)\NSIS\makensis.exe'
    print('Starting NSI Installer Build')
    # Use NSIS to create the installers.
    arrCmd = [nsis_path, "winpushbullet_installer.nsi"]
    start = time.time()
    retcode = subprocess.call(arrCmd)
    if retcode != 0:
        raise BuildFailure(f'NSI Compiler returned non-zero: {retcode}')
    print('NSI Installer Build - %.1f seconds' % (time.time() - start))

def main():
    try:
        args = sys.argv[1:]
        build_pc_push = '-pushb' in args
        build_pc_pull = '-pullb' in args
        build_pb_cli = '-pbcli' in args
        build_installer = '-installer' in args

        if '-full' in args:
            build_pc_push = True
            build_pc_pull = True
            build_pb_cli = True
            build_installer = True

        if build_pc_push:
            build_application(Application.PUSHB)

        if build_pc_pull:
            build_application(Application.PULLB)

        if build_pb_cli:
            build_application(Application.PB_CLI)

        if build_installer:
            build_installer_fn(build_pc_push, build_pc_pull, build_pb_cli)

    except Exception as e:
        print('Build stopped due to the following exception:')
        print(e)




if __name__ == '__main__':
    main()