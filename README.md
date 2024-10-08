# WinPushBullet
WinPushBullet is a set of hot keys and File Explorer context menu options which allow you to quickly push and pull content to/from your PushBullet account.
PushBullet is a service that allows you to share files between your different devices.

I use WinPushBullet to quickly share files between my Windows PC and my Apple devices, achieving AirDrop like functionality.

# Use Cases
WinPushBullet is great for sharing text, link and files between your Windows computer and Apple devices. Here's a few examples of what you can do when it is fully configured.

## Sending text from my computer to my phone


# How To Install
## Installing WinPushBullet on your computer
1. Obtain your PushBullet access token
    1. Create a PushBullet account on https://www.pushbullet.com/ if you  don't have one already (free)
    2. Go to https://www.pushbullet.com/#settings > Account > Access Tokens
    3. Click "Create Access Token" and copy the generated text. You will need this in later steps
2. Download and Install AutoHotKey v2 (required for hotkeys)
    1. Go to https://www.autohotkey.com/
    2. Click the "Download" button and then "Download v2.0"
    3. Run the installer executable to install 
3. Download the latest release of the WinPushBullet installer
    1. Go to https://github.com/iffy-pi/winpushbullet/releases
    2. Go to the top level card on the page (labelled Latest)
    3. Click the .Setup.exe file to download it
4. Run the downloaded installer
    1. When prompted, enter the access token you obtained in Step 1 into the access token text box

## Installing on your Apple Devices
You can access the PushBullet service using Apple Shortcuts I designed
Note: You will need to have the access token you generated in the above steps accessible on your Apple device to complete the install.

1. Download and configure PushBullet shortcut - for pushing items from your device
    1. Go to https://routinehub.co/shortcut/15515/
    2. Click "Get Shortcut" option, or scan the QR code on your phone
    3. Install the shortcut when prompted
    4. Navigate to the shortcut in the Apple Shortcuts app, and tap it to run
    5. **Select "Change Shortcut Settings", and then "Set PushBullet Access Token"**
    6. Enter the access token you generated earlier
2. Download and configure PullBullet shortcut - for pulling items to your device
    1. Go to https://routinehub.co/shortcut/15516/
    2. Click "Get Shortcut" option, or scan the QR code on your phone
    3. Install the shortcut when prompted (No other configuration is required as your configured access token is remembered)
3. Download PushList shortcut - To view and download multiple pushes at once
    1. Go to https://routinehub.co/shortcut/15517/
    2. Click "Get Shortcut" option, or scan the QR code on your phone
    3. Install the shortcut when prompted (No other configuration is required as your configured access token is remembered) 

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