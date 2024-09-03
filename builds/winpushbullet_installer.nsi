; BKIN Dexterity Installer Creation Script
; Copyright (C) 2005-2021 BKIN Technologies
;
; The installer created by this script writes the information to the registry at:
;   HKLM/Software/${COMPANY}/${PRODUCT} ${VERSION}, e.g. HKLM/Software/BKIN Technologies/BKIN Dexterity 2.3.1
;
; The values written are:
;   InstallDir (REG_SZ) - the full install path of the product, e.g. "C:\Program Files\BKIN Technologies\BKIN Dexterity 2.3"

;--------------------------------------------------------------------------------------------------------------------------------
; Header Files
;--------------------------------------------------------------------------------------------------------------------------------

!include MUI2.nsh
!include LogicLib.nsh

!addplugindir "plugins"


;--------------------------------------------------------------------------------------------------------------------------------
; Defines
;--------------------------------------------------------------------------------------------------------------------------------

!define VER_MAJOR 2
!define VER_MINOR 0
!define VER_REVISION 1

!define INPUT_DIR ".\fulldist"           ; directory to pack
!define OUTPUT_DIR ".\installers"										   ; directory in which to write installer exe

!define PRODUCT "WinPushBullet"                                ; product name
!define VERSION "${VER_MAJOR}.${VER_MINOR}.${VER_REVISION}"      ; product's full version string
!define COMPANY "IEM Development"                                            ; company name
!define COMPANY_FULL "IEM Development"                              ; company name
!define APP_DATA_DIR "${PRODUCT}" ; product name

!define REG_KEY "Software\${COMPANY}\${PRODUCT} ${VERSION}"      ; registry key used for this product and version

;--------------------------------------------------------------------------------------------------------------------------------
; Basic Configuration
;--------------------------------------------------------------------------------------------------------------------------------

Name "${PRODUCT} ${VERSION}"                                     ; product name appearing throughout the installer
Caption "${PRODUCT} ${VERSION} Setup"                            ; installer name used throughout the installer
AllowRootDirInstall false                                        ; prevent installation to a drive's root directory
OutFile "${OUTPUT_DIR}\${PRODUCT} ${VERSION} Setup.exe"          ; installer filename
BrandingText "${COMPANY}"                                        ; text appearing at bottom of the installer window
SetCompressor  lzma                                              ; lzma compression provides best results at this writing

;--------------------------------------------------------------------------------------------------------------------------------
; Variables
;--------------------------------------------------------------------------------------------------------------------------------

;--------------------------------------------------------------------------------------------------------------------------------
; Interface Configuration
;--------------------------------------------------------------------------------------------------------------------------------

; Use the "orange theme" graphics packaged with NSIS.
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\orange-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\orange-uninstall.ico"

!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_LEFT
!define MUI_HEADERIMAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Header\orange.bmp"
!define MUI_HEADERIMAGE_UNBITMAP "${NSISDIR}\Contrib\Graphics\Header\orange-uninstall.bmp"

!define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\orange.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\orange-uninstall.bmp"

; Ensure warnings are shown on attempts to abort.
!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING

;--------------------------------------------------------------------------------------------------------------------------------
; Version Information
;--------------------------------------------------------------------------------------------------------------------------------

; These commands add version information to the file properties of the installer and uninstaller.
VIProductVersion "${VERSION}.0"

VIAddVersionKey "ProductName"      "${PRODUCT}"
VIAddVersionKey "CompanyName"      "${COMPANY}"
VIAddVersionKey "FileDescription"  "${COMPANY} ${PRODUCT} Installer"
VIAddVersionKey "FileVersion"      "${VERSION}"

;--------------------------------------------------------------------------------------------------------------------------------
; Pages
;--------------------------------------------------------------------------------------------------------------------------------

; Define installer pages.
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
Page custom ConfigPage ConfigPageLeave
!insertmacro MUI_PAGE_FINISH

; Define uninstaller pages.
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE un.onWelcomeLeave
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

;--------------------------------------------------------------------------------------------------------------------------------
; Page Functions
;--------------------------------------------------------------------------------------------------------------------------------
Function .onInit
	; Page Function
	; The onInit function runs after the installer starts, right before the user sees the first window. This function handles
	; checking whether the installer is already running and prompting the user with warnings based on version information in
	; the registry.
	StrCpy $INSTDIR "C:\${APP_DATA_DIR}"
FunctionEnd


Var ConfigPageDlg
var LblAccessToken
var TxtAccessToken
Var BtnNext
var LblHotkeyGen
var TxtHotkeyScriptAddr
var BtnBrowseHotkeyAddr
var ChkBxAddToStart
var ChkBxState
var ChkBxRunHotKeyNow

Function ConfigPage
	; ConfigPage page creation function - populates the page with the dialogs and controls we want
	!insertmacro MUI_HEADER_TEXT "Configure ${PRODUCT}" "Configure ${PRODUCT} settings"

	nsDialogs::Create 1018
	Pop $ConfigPageDlg

	${If} $ConfigPageDlg == error
		Abort
	${EndIf}

	GetDlgItem $BtnNext $HWNDPARENT 1 ;  Index 1 is the next button for the page

	${NSD_CreateLabel} 0 0 100% 20u "Enter your PushBullet access token below.$\nYou can obtain an access token from your account settings."
	Pop $LblAccessToken

	; Get the pushbullet access token if it exists
	ExecDos::exec /TIMEOUT=5000 /TOSTACK '$INSTDIR\pb\pb.exe --get-token-only'
	Pop $0
	; $0 has access token value
	; If it is -1, put nothing in the field
	; Else gen text box with value
	Pop $0

	${If} $0 == "-1"
		StrCpy $0 ""
		EnableWindow $BtnNext 0 ;
	${EndIf}

	${NSD_CreateText} 0 19u 100% 13u "$0"
	Pop $TxtAccessToken
	${NSD_OnChange} $TxtAccessToken ConfigPage_OnTxtAccessTokenChange

	${NSD_CreateLabel} 0 45u 100% 12u "Save address of generated HotKey script"
	Pop $LblHotkeyGen

	${NSD_CreateText} 0 57u 78% 13u "$INSTDIR\WinPushBullet_Hotkeys.ahk"
	Pop $TxtHotkeyScriptAddr

	
	${NSD_CreateButton} -20% 57u 20% 14u "Browse..."
	Pop $BtnBrowseHotkeyAddr
	${NSD_OnClick} $BtnBrowseHotkeyAddr ConfigPage_OnBtnBrowse

	${NSD_CreateCheckBox} 0 72u 100% 13u "Load hotkey script after install is complete (requires AutoHotKey)"
	Pop $ChkBxRunHotKeyNow

	${NSD_CreateCheckBox} 0 85u 100% 13u "Automatically load hotkey script at start up"
	Pop $ChkBxAddToStart

	nsDialogs::Show
FunctionEnd


Function ConfigPageLeave
	; Runs when user leaves the ConfigPage, now you can read the data put in by the user

	; Save the access token
	${NSD_GetText} $TxtAccessToken $0
	Exec '"$INSTDIR\pb\pb.exe" "-set-token" "$0"'

	; Generate the hotkey script at the required address
	${NSD_GetText} $TxtHotkeyScriptAddr $0
	${If} $0 != "$INSTDIR\WinPushBullet_Hotkeys.ahk"
		Exec '"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -WindowStyle Hidden -Command "(Get-Content \"$INSTDIR\hotkeys_template.ahk\").replace(\"<INSTDIR>\", \"$INSTDIR\") | Set-Content \"$0\""'
	${EndIf}

	; Load hotkey script if requested
	${NSD_GetState} $ChkBxRunHotKeyNow $ChkBxState
	${If} $ChkBxState == ${BST_CHECKED}
		${NSD_GetText} $TxtHotkeyScriptAddr $0
		ExecShell "" "$0"
	${EndIf}

	; If they wanted it added at start up
	${NSD_GetState} $ChkBxAddToStart $ChkBxState
	${If} $ChkBxState == ${BST_CHECKED}
		${NSD_GetText} $TxtHotkeyScriptAddr $0
		SetShellVarContext current
		CreateShortCut "$SMSTARTUP\WinPushBullet hotkeys.lnk" "$0"
		SetShellVarContext all
	${EndIf}

FunctionEnd

Function ConfigPage_OnTxtAccessTokenChange
	${NSD_GetText} $TxtAccessToken $0
	StrCmp $0 "" disable_next
	EnableWindow $BtnNext 1
	Return
	disable_next:
	EnableWindow $BtnNext 0
FunctionEnd

Function ConfigPage_OnBtnBrowse
	${NSD_GetText} $TxtHotkeyScriptAddr $0
	nsDialogs::SelectFileDialog save "$0" "*.ahk"
	Pop $0
	StrCmp $0 "" go_back update_addr
	go_back:
		Return
	
	update_addr:
		${NSD_SetText} $TxtHotkeyScriptAddr $0
FunctionEnd


Function .onInstSuccess
	; Runs when installation is successful
	; Gives user the chance to edit configuration
FunctionEnd


Function un.onInit
	; StrCpy $replacedVersion ""
FunctionEnd


Function un.onWelcomeLeave
	; Prompts the user for whether or not to retain their config file as they leave the Welcome page in the uninstaller.

	; MessageBox MB_YESNO|MB_ICONQUESTION "Would you like to retain the shared ${PRODUCT} configuration, for future installations of ${PRODUCT} ${VERSION} or later?" IDYES configRetain
	; StrCpy $replacedVersion ${VERSION}

	; configRetain:
FunctionEnd

;--------------------------------------------------------------------------------------------------------------------------------
; Called Functions
;--------------------------------------------------------------------------------------------------------------------------------
Function AddFileExplorerContextMenuItems
	; Adds explorer context menu items
	; This is all done by modifying registry

	; Add "Push file" to file context menu
	WriteRegStr HKCR "*\shell\${PRODUCT} Push File" "" "&Push file"
	WriteRegStr HKCR "*\shell\${PRODUCT} Push File" "Icon" "$INSTDIR\PC_PushBullet\PC_PushBullet.exe"
	WriteRegStr HKCR "*\shell\${PRODUCT} Push File\command" "" '"$INSTDIR\PC_PushBullet\PC_PushBullet.exe" "--headless" "-arg" "%1" "--file"'

	; Add "Push path of selected directory"
	WriteRegStr HKCR "Directory\shell\${PRODUCT} Push Selected Directory" "" "&Push path to selected directory"
	WriteRegStr HKCR "Directory\shell\${PRODUCT} Push Selected Directory" "Icon" "$INSTDIR\PC_PushBullet\PC_PushBullet.exe"
	WriteRegStr HKCR "Directory\shell\${PRODUCT} Push Selected Directory\command" "" '"$INSTDIR\PC_PushBullet\PC_PushBullet.exe" "--headless" "-arg" "%V" "--text"'

	; Add "Push path of here"
	WriteRegStr HKCR "Directory\Background\shell\${PRODUCT} Push Background Directory" "" "&Push path to current directory"
	WriteRegStr HKCR "Directory\Background\shell\${PRODUCT} Push Background Directory" "Icon" "$INSTDIR\PC_PushBullet\PC_PushBullet.exe"
	WriteRegStr HKCR "Directory\Background\shell\${PRODUCT} Push Background Directory\command" "" '"$INSTDIR\PC_PushBullet\PC_PushBullet.exe" "--headless" "-arg" "%V" "--text"'
	
	; Add "Pull file to here"
	WriteRegStr HKCR "Directory\Background\shell\${PRODUCT} Pull File" "" "&Pull file to here"
	WriteRegStr HKCR "Directory\Background\shell\${PRODUCT} Pull File" "Icon" "$INSTDIR\PC_PullBullet\PC_PullBullet.exe"
	WriteRegStr HKCR "Directory\Background\shell\${PRODUCT} Pull File\command" "" '"$INSTDIR\PC_PullBullet\PC_PullBullet.exe" "--headless" "--handleAsFile" "-behaviour" "save" "-saveToDir" "%V"'

	; Add "Pull file to here and rename...."
	WriteRegStr HKCR "Directory\Background\shell\${PRODUCT} Pull File And Rename" "" "&Pull file to here and rename..."
	WriteRegStr HKCR "Directory\Background\shell\${PRODUCT} Pull File And Rename" "Icon" "$INSTDIR\PC_PullBullet\PC_PullBullet.exe"
	WriteRegStr HKCR "Directory\Background\shell\${PRODUCT} Pull File And Rename\command" "" '"$INSTDIR\PC_PullBullet\PC_PullBullet.exe" "--headless" "--handleAsFile" "-behaviour" "save" "-saveToDirWithDlg" "%V"'
FunctionEnd

;--------------------------------------------------------------------------------------------------------------------------------
; Install Section
;--------------------------------------------------------------------------------------------------------------------------------

Section "Install"

	; Use the All Users context for shell variables like $SMPROGRAMS.
	SetShellVarContext all

	; Extract application files.
	SetOutPath $INSTDIR
	File /r "${INPUT_DIR}\*"

	; Generate hot keys to install
	File "${INPUT_DIR}\..\hotkeys_template.ahk"
	Exec '"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -WindowStyle Hidden -Command "(Get-Content hotkeys_template.ahk).replace(\"<INSTDIR>\", \"$INSTDIR\") | Set-Content WinPushBullet_Hotkeys.ahk"'

	; Add explorer context menu items
	Call AddFileExplorerContextMenuItems
	
	; Write the uninstaller.
	WriteUninstaller "Uninstall.exe"

SectionEnd

;--------------------------------------------------------------------------------------------------------------------------------
; Uninstall Section
;--------------------------------------------------------------------------------------------------------------------------------

Section "un.Install"

	; Use the All Users context for shell variables like $SMPROGRAMS.
	SetShellVarContext all


	; Delete application files
	RMDir /r "$INSTDIR\PC_PullBullet"
	RMDir /r "$INSTDIR\PC_PushBullet"
	RMDir /r "$INSTDIR\pb"
	Delete "$INSTDIR\hotkeys_template.ahk"
	Delete "$INSTDIR\WinPushBullet_Hotkeys.ahk"
	
	SetShellVarContext current
	Delete "$SMSTARTUP\WinPushBullet hotkeys.lnk"
	SetShellVarContext all

	; Remove explorer context menu items
	DeleteRegKey HKCR "*\shell\${PRODUCT} Push File"
	DeleteRegKey HKCR "Directory\shell\${PRODUCT} Push Selected Directory"
	DeleteRegKey HKCR "Directory\Background\shell\${PRODUCT} Push Background Directory"
	DeleteRegKey HKCR "Directory\Background\shell\${PRODUCT} Pull File"
	DeleteRegKey HKCR "Directory\Background\shell\${PRODUCT} Pull File And Rename"

	; Delete the uninstaller.
	Delete "$INSTDIR\Uninstall.exe"

SectionEnd

