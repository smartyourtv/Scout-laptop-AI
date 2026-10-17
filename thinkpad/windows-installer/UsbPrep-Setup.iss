; ══════════════════════════════════════════════════════════════════
; UsbPrep-Setup.iss — Inno Setup script for the Scout USB Prep tool.
;
; Produces ONE installer: UsbPrep-Setup.exe
;   - per-user install (NO admin needed to install)
;   - installs UsbPrep.exe + its data tree (thinkpad\ + files\)
;   - Start Menu + Desktop shortcuts
;   - uninstaller registered in Windows Settings > Apps
; The APP itself still asks for Administrator at run time (UAC),
; because making a USB drive bootable requires it — that is the
; tool's own relaunch, unchanged.
;
; Build (from the repo root, after the PyInstaller step):
;   iscc /DDataDir=build\installer-data thinkpad\windows-installer\UsbPrep-Setup.iss
; Defines:
;   ExeFile  — path to the PyInstaller output (default: dist\UsbPrep.exe)
;   DataDir  — staged data tree containing thinkpad\ and files\
;              (default: build\installer-data)
;   OutDir   — where UsbPrep-Setup.exe is written (default: dist-installer)
; The GitHub Actions workflow (windows-latest) runs both steps.
; ══════════════════════════════════════════════════════════════════

#ifndef ExeFile
  #define ExeFile AddBackslash(SourcePath) + "..\..\dist\UsbPrep.exe"
#endif
#ifndef DataDir
  #define DataDir AddBackslash(SourcePath) + "..\..\build\installer-data"
#endif
#ifndef OutDir
  #define OutDir AddBackslash(SourcePath) + "..\..\dist-installer"
#endif

#define MyAppName "Scout USB Prep"
#define MyAppVersion "3.0"
#define MyAppPublisher "Scout Van AI"
#define MyAppExeName "UsbPrep.exe"

[Setup]
AppId={{F48B78F5-E628-410D-8D68-230E5E8378DF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Per-user install: no administrator rights needed to install.
PrivilegesRequired=lowest
DefaultDirName={autopf}\UsbPrep
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir={#OutDir}
OutputBaseFilename=UsbPrep-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; The single-file PyInstaller executable.
Source: "{#ExeFile}"; DestDir: "{app}"; Flags: ignoreversion
; The data tree the tool resolves next to the exe when installed:
; thinkpad\ (installer scripts, parts DB, knowledge base) and
; files\ (knowledge libraries + van manuals).
Source: "{#DataDir}\thinkpad\*"; DestDir: "{app}\thinkpad"; \
  Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#DataDir}\files\*"; DestDir: "{app}\files"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; \
  Description: "Launch {#MyAppName} now"; \
  Flags: nowait postinstall skipifsilent
