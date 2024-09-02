# WinPushBullet
WinPushBullet is a set of hot keys and File Explorer context menu options which allow you to quickly push and pull content to/from your PushBullet account.
PushBullet is a service that allows you to share files between your different devices.

I use WinPushBullet to quickly share files between my Windows PC and my Apple devices, achieving AirDrop like functionality.
[How To Install](#installing-and-configuring-winpushbullet)

# Functions and Features
WinPushBullet comes with the following features:

## Hotkeys 
WinPushBullet generates a hotkey script (which can be loaded using AutoHotKey v2) with the following functions
_Note: Hotkeys can be edited to match your desired usecase, simply edit the generated hot key script file and reload it in AutoHotKey. You can also view the [Script Specification](#script-specification) to customize the actions of WinPushBullet itself_

![Hotkey Picture](/docs/media/hotkey_picture.png?raw=true "Hotkey Picture")

| No. | Hotkey           | Title                               | Description                                                                                                               |
|-----|------------------|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| 1   | `Ctrl`+`Alt`+`[` | Pull content to clipboard           | Copies text, links and images to clipboard.                                                                               |
| 2   | `Ctrl`+`Alt`+`]` | Push content on clipboard           | Push clipboard content (copied text, link and files), if file address is on clipboard pushes the file at the address      |
| 3   | `Ctrl`+`Alt`+`;` | Pull and Paste                      | Pulls content from clipboard, and pastes by using Ctrl+V                                                                  |
| 4   | `Ctrl`+`Alt`+`'` | Copy and Push                       | Copies content with Ctrl+C, and then pushes copied content                                                                |
| 5   | `Ctrl`+`Alt`+`,` | Save to File                        | Opens Save File Dialog for pushed text, links and files                                                                   |
| 6   | `Ctrl`+`Alt`+`.` | View Content                        | Opens text in default text editor, opens links and files in browser                                                       |
| 7   | `Ctrl`+`Alt`+`/` | Push Browser URL (Brave and Chrome) | Selects browser URL with Alt+D, copies it with Ctrl+C, and pushes it. If valid file URI, file being pointed to is pushed. |

## File Explorer Context Menu Actions
You also have access to the following actions when you right-click in File Explorer.

### Right-Click Explorer Background
- Pull File To Here
  - Takes the last push (which is assumed to be a file) and saves it as its pushed name to the open directory
- Pull File To Here and Rename
  - Takes the last push (which is assumed to be a file) and opens a save file dialog
- Push Path of Current Directory
  - Pushes the current directory path as a file

### Right-Click on Selected Folder
- Push Directory Path
  - Pushes the current directory path as a file

### Right-Click on Selected File
- Push File
  - Pushes the selected file to PushBullet

# Installing and Configuring WinPushBullet
### Requirements
- A PushBullet Account and your access token
- To generate your access token, go to https://www.pushbullet.com/#settings/account > Access Tokens > Create Access Token
- AutoHotKey v2: https://www.autohotkey.com/v2/

### How-To
Download and run the latest released installer.

### Configure Your Apple Device(s) (Optional)
I also designed some Apple shortcuts which use the PushBullet API to allow you to use PushBullet on your Apple devices.

#### Requirements
- A PushBullet Account (premium not required) and your access token
	- To generate your access token, go to https://www.pushbullet.com/#settings/account > Access Tokens > Create Access Token
- Apple Shortcuts
  - Make sure to allow "Download shortcuts from untrusted sources" in your settings.

#### Install the shortcuts
You can download and install the PushBullet and PullBullet shortcuts to push and pull content from the PushBullet Server:
- PushBullet: https://routinehub.co/shortcut/15515/
- PullBullet: https://routinehub.co/shortcut/15516/

# Script Specification
WinPushBullet installs three programs:
- PC_PushBullet : Handles pushing content to PushBullet
- PC_PullBullet : Handles pulling content from PushBullet
- PB : A command line tool for both pushing and pulling content, also used for configuration

## `PB\pb.exe`
This is a command line that allows you to push and pull files from the command line. To see its usage run `pb.exe --help`

## `PC_PushBullet\PC_PushBullet.exe`
This script is used to push content from the computer to PushBullet. The script reads the content of the clipboard and pushes it as text, URL or file based on the clipboard content type.
The current specification:
```
pc_pushbullet 
[--clip] [-arg <arg>] [-staging <directory path>]
[--text] [--link] [--file]
[--headless]

[--forceText] [--filePathCopied]
[--convertFileURI] [--linkCopied]
[--filePathArgument <arg>] [--textArgument <arg>]
```

- `--headless` : When used, the script will run windowless, communicating only through Windows notifications
- Source Options:
    - `--clip` (Default): Push item is the item in the clipboard. To override this you have the following:
    - `-arg <arg>`: Push item is the passed in argument (O)
    - `-staging <directory path>`: Takes the latest item in the directory, pushes it as a file and then deletes the file.
- Type Flags:
    - Without any flags specified, the script infers type
        - Treats as file if file path is found or is file object
        - Treats as link if it goes to a URL
        - Treats as text for every other case
        - If file URI is copied, it is converted to a file path for a file to be pushed
            - If the file does not exist or is invalid, it will not be changed and instead be pushed as text
    - `--text`: Treats the push item as a text
        - This will disable file URI conversions, to enable them use `--convertFileURI`
    - `--link`: Treats the push item as a link
        - This will disable file URI conversions, to enable them use `--convertFileURI`
    - `--file`: Treats the push item as a path to the file to be pushed
- Modifier flags:
    - `--convertFileURI`: If a file URI is detected as the push item, it will be converted to a file path and will push the resulting file.
        - If the conversion fails or the converted file path does not exist, the item will not be overridden, the other flags passed in will determine what is done with the item


## `PC_PullBullet\PC_PullBullet.exe`
This is the script used to get content from PushBullet onto the computer. It is designed to get the latest push from PushBullet and handles the content based on its type.
```
pc_pullbullet
[--headless] [--handleAsFile]
[-behaviour <behaviour string>]
[-saveToDir <directory path>] [-saveToDirWithDlg <directory path>]
```

- `--headless`
    - When used, the script will run windowless, communicating only through Windows notifications
- `--handleAsFile`
    - This will force all other push types (text, url) to be treated as if they were a pushed file.
        - Text pushes are treated as text files
        - URL pushes are treated as text files
- `-behaviour <behaviour string>`
    - This specifies the behaviour to be used by the script. A behaviour specifies the way a push type is handled by the script.
    - If not specified, the `default` behaviour will be used
    - Available Behaviour Types:
        - Default: `default`
            - Text        : Copied to clipboard
            - URLs        : Opened in browser
            - Image Files : (png,jpg) Copied to clipboard
            - Other Files : Saved to system using save method
        - Copy Only: `copy`
            - Text        : Copied to clipboard
            - URLs        : Copied to clipboard
            - Image Files : Copied to clipboard
            - Other Files : Same as `default` behaviour
        - View Content: `view`
            - Text        : A temporary text file is created and opened
            - URLs        : Opened in browser
            - Image Files : Opened in browser
            - Other Files : Opened in browser
        - Save Files: `save`
            - Text        : Text is treated as text file (same as using `--handleAsFile`)
            - URLs        : Link is treated as text file (same as using `--handleAsFile`)
            - Image Files : Saved to system using save method
            - Other Files : Saved to system using save method
    - The 'save method' is the method used for saving a given file
        - Default: Save using a file explorer dialog opened to default location
        - Save To Directory (specified with `-saveToDir <path>` flag): Saves the file to a specified directory
            - If there is already a file with the pushed file name in that directory, the file explorer dialog will be given to allow the user to rename the file
        - Save To Directory with Dialog (specified with `-saveToDirWithDlg <path>` flag): Opens File Explorer Dialog in the specified directory