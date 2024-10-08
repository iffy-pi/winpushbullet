# Technical Documentation
This documentation provides further information on the configuration of WinPushBullet: How the hotkeys work, the available scripts under the hood etc. This is intended for users who would like to understand its inner workings or tweak the scripts for their own experience.

## WinPushBullet Hotkeys
The hotkeys for WinPushBullet are implemented as an AutoHotKey v2 script. This script is always running in the background and performs different actions based on the set of keys pressed.

The hotkeys listed below are the ones configured by WinPushBullet by default. You can edit the hotkey script yourself to change the hotkeys used or what actions are performed for each hotkey. (To change the actions performed for each key you will need to read the [Script Specification](#script-specification) to understand the command line parameters for each script).

![Hotkey Picture](./media/hotkey_picture.png?raw=true "Hotkey Picture")

| No. | Hotkey           | Title                               | Description                                                                                                               |
|-----|------------------|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| 1   | `Ctrl`+`Alt`+`[` | Pull content to clipboard           | Copies text, links and images to clipboard.                                                                               |
| 2   | `Ctrl`+`Alt`+`]` | Push content on clipboard           | Push clipboard content (copied text, link and files), if file address is on clipboard pushes the file at the address      |
| 3   | `Ctrl`+`Alt`+`;` | Pull and Paste                      | Pulls content from clipboard, and pastes by using Ctrl+V                                                                  |
| 4   | `Ctrl`+`Alt`+`'` | Copy and Push                       | Copies content with Ctrl+C, and then pushes copied content                                                                |
| 5   | `Ctrl`+`Alt`+`,` | Save to File                        | Opens Save File Dialog for pushed text, links and files                                                                   |
| 6   | `Ctrl`+`Alt`+`.` | View Content                        | Opens text in default text editor, opens links and files in browser                                                       |
| 7   | `Ctrl`+`Alt`+`/` | Push Browser URL (Brave and Chrome) | Selects browser URL with Alt+D, copies it with Ctrl+C, and pushes it. If valid file URI, file being pointed to is pushed. |


# Script Specification
WinPushBullet installs three programs:
- PC_PushBullet : Handles pushing content to PushBullet
- PC_PullBullet : Handles pulling content from PushBullet
- PB : A command line tool for both pushing and pulling content, also used for configuration

## `PB\pb.exe`
This is a command line that allows you to push and pull files from the command line. To see its usage run `pb.exe --help`

## `PC_PushBullet\PC_PushBullet.exe`
This script is used to push content from the computer to PushBullet.
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
- Source Options - These determine where the item to be pushed is gotten from
    - `--clip` (Default): Push item is the item in the clipboard. To override this you have the following:
    - `-arg <arg>`: Push item is the string passed with the flag i.e. `<arg>`
    - `-staging <directory path>`: Takes the latest item in the directory, pushes it as a file and then deletes the file.
- Type Flags - An item must either be pushed as text, a link or a file. These flags determine how the item selected is treated
    - Without any flags specified, the script automatically determines the type of the items:
        - Treats item as file if it is a file handler, or is a file path string
        - Treats as link if it goes to a URL
        - Treats as text for every other case
        - If a file URI is copied, it is converted to a file path for a file to be pushed
            - If the file does not exist or is invalid, it will not be changed and instead be pushed as text
    - `--text`: Treats the push item as a text
        - This will disable file URI conversions, to enable them use `--convertFileURI`
    - `--link`: Treats the push item as a link
        - This will disable file URI conversions, to enable them use `--convertFileURI`
    - `--file`: Treats the push item as a path to the file to be pushed, retrieves and pushes the specified file
- Modifier flags:
    - `--convertFileURI`: If a file URI is detected as the push item, it will be converted to a file path and will push the resulting file.
        - If the conversion fails or the converted file path does not exist, the item will not be overridden, the other flags passed in will determine what is done with the item


## `PC_PullBullet\PC_PullBullet.exe`
This is the script used to get content from PushBullet onto the computer. It is designed to get only the latest push from PushBullet and handles the content based on its type.
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
    - The 'behaviour' for the script is the actions that are performed with the retrieved push item: The item can be copied to clipboard, saved, opened in the browser etc.
    - If the flag not specified, the `default` behaviour will be used
    - Available Behaviour Types:
        - Default: `default`
            - Text        : Copied to clipboard
            - URLs        : Opened in browser
            - Image Files : (png,jpg) Copied to clipboard
            - Other Files : Saved to system using **save method**
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
            - Text        : Text is treated as text file, saved to system using **save method** (same as using `--handleAsFile`)
            - URLs        : Link is treated as text file, saved to system using **save method** (same as using `--handleAsFile`)
            - Image Files : Saved to system using **save method**
            - Other Files : Saved to system using **save method**
    - The **save method** is the method used for saving a given file
        - Default: Save using a file explorer dialog opened to default location
        - Save To Directory (specified with `-saveToDir <path>` flag): Saves the file to a specified directory
            - If there is already a file with the pushed file name in that directory, the file explorer dialog will be given to allow the user to rename the file
        - Save To Directory with Dialog (specified with `-saveToDirWithDlg <path>` flag): Opens File Explorer Dialog in the specified directory