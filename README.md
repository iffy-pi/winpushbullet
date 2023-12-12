# PushBullet PC Integration
This is a set of scripts I designed that uses PushBullet to achieve AirDrop-like functionality between my Windows Laptop and Apple Devices.

## Computer Extensions
If you follow the steps in the Configure section, then these are the features available to you

### Pushing Content HotKeys
- Default: `Ctrl + Alt + ]`
    - Gets content from clipboard, infers text, link, file or file from copied file path
- Push As Text: `Ctrl + Alt + '`
    - Gets content from clipboard, always treats as text
- Push From Temp Directory: `Ctrl + Alt + /`
    - Pushes latest file in specified directory `configs.userconfig.TEMP_DIRECTORY`

### Pulling Content HotKeys
- Default: `Ctrl + Alt + [`
    - Copies text to clipboard
    - Copies images (jpeg, jpg and png) to clipboard
    - Opens URLs in browser
    - Save File Dialog for other files
- Copy Content: `Ctrl + Alt + ;`
    - Copies text to clipboard
    - Copies URLs to clipboard
    - Copies image files to clipboard
    - Save File Dialog for other files
- Open In Browser: `Ctrl + Alt + > `
    - Copies text to clipboard
    - Opens URLs in browser
    - Opens images and other files in browser
- Save Content To File: `Ctrl + Alt + <`
    - Copies text to clipboard
    - Opens URLs in browser
    - Save File Dialog for images and files

### File Explorer Context Menu Actions
The following actions are also added to the context menu through the registry editor:

#### Right Click Explorer Background
- Pull File To Here
  - Takes the last push (which is assumed to be a file) and saves it as its pushed name to the open directory
- Pull File To Here and Rename
  - Takes the last push (which is assumed to be a file) and opens a save file dialog
- Push Path of Current Directory
  - Pushes the current directory path as a file

#### Right Click on Selected Folder
- Push Directory Path
  - Pushes the current directory path as a file

#### Right Click on Selected File
- Push File
  - Pushes the selected file to PushBullet

## Configure Your PC
### Required Programs
- Python 3.10
- AutoHotKey - https://www.autohotkey.com/

### Clone the repository and install required packages
Clone this repository onto your local PC and install the required packages, as specified in requirements.txt

```batch
pip install -r requirements.txt
```

### Update `config/userconfig.py`
Populate all the fields in userconfig.py with paths on your system

### Configure HotKeys
Firstly, run `config.configure_hotkeys.py`. This will generate a `hotkeys.ahk` in config/ file which maps the hotkeys specified above to the appropriate script calls.

Double click `hotkeys.ahk` to run the file. You can also configure it to run on startup by:
1. Press Win + R
2. Type `shell:startup`
3. Add a shortcut to `hotkeys.ahk` to the opened folder


### Configure Explorer Context Menu Actions
Run the script `config/configure_explorer_actions.py` **as an administator** to add the explorer context menu actions.

## Script Specification
### `pc_pushbullet.py`
This script is used to push content from the computer to PushBullet. The script reads the content of the clipboard and pushes it as text, URL or file based on the clipboard content type.

The current specification:

```
pc_pushbullet 
[--headless] [--forceText] [--filePathCopied] [--latestTempFile] 
[--filePathArgument <arg>] [--textArgument <arg>]
```

- `--headless` : When used, the script will run windowless, communicating only through Windows notifications
- `--forceText` : Treat the clipboard content only as text, no link or file inferring
- `--filePathCopied` : Treat the clipboard content as a path for the file to be pushed
- `--latestTempFile` : Copy the latest file from C:\local\temp directory
- `--filePathArgument <arg>` : Treat `<arg>` as path for the file to be pushed.
- `--textArgument <arg>` : Treat `<arg>` as raw text

### `pc_pullbullet.py`
This is the script used to get content from PushBullet onto the computer. It is designed to get the latest push from PushBullet and handles the content based on its type. The default behaviour (no flag behaviour changes) for the types:

- Text is copied to the clipboard
- Links are opened in the browser (Brave)
- Image files (jpegs, pngs, gifs) are copied to the clipboard
- Other files are presented with a Save File Dialog

Flags are used to override the default behaviour:

```
pc_pullbullet
[--headless] [--strictlyCopy] [--strictlyBrowser] [--strictlyFile] 
[--saveToDir <arg>] [--saveToDirAndRename <arg>]
```

- `--headless` : When used, the script will run windowless, communicating only through Windows notifications
- `--strictlyCopy` : All text, files and links are copied to the clipboard
- `--strictlyBrowser` : Text is copied to the clipboard but all files and links are opened in the browser.
- `--strictlyFile` : All files are presented with save file dialog
- `--saveToDir <arg>` : Saves the pushed file in the directory specified with `<arg>`
- `--saveToDirAndRename <arg>` : Presents the Save File dialog for the pushed file, opened to the directory specified with `<arg>`