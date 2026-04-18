; Song Clipper - Inno Setup Script
; Requires Inno Setup 6+: https://jrsoftware.org/isinfo.php
; Run with: iscc installer.iss
; Or double-click installer.iss if Inno Setup is installed

#define AppName "Song Clipper"
#define AppVersion "1.0.0"
#define AppPublisher "Song Clipper"
#define AppURL "https://github.com/yourusername/music_clipper_local_offline"
#define AppExeName "SongClipper.exe"
#define SourceDir "dist\SongClipper"

[Setup]
AppId={{A3F2E8B1-4C5D-4E6F-9A7B-8C3D2E1F0A5B}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
; Compression
Compression=lzma2/ultra64
SolidCompression=yes
; Output
OutputDir=installer_output
OutputBaseFilename=SongClipper-Setup-v{#AppVersion}
; Appearance
WizardStyle=modern
SetupIconFile=
; Require admin to install to Program Files
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Windows version requirement
MinVersion=6.1sp1
; Architecture
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenu"; Description: "Create Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; Main executable
Source: "{#SourceDir}\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Bundled runtime and dependencies
Source: "{#SourceDir}\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; FFmpeg placeholder folder and readme
Source: "tools\ffmpeg\.gitkeep"; DestDir: "{app}\tools\ffmpeg"; DestName: "README.txt"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Comment: "Extract precise segments from MP3 files"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

; Desktop (optional)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; Offer to launch the app after install
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up generated files on uninstall
Type: filesandordirs; Name: "{app}"

[Code]
// Check if FFmpeg is available on the system
function FFmpegInPath(): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/C where ffmpeg >nul 2>nul', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := Result and (ResultCode = 0);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if not FFmpegInPath() then
    begin
      MsgBox(
        'FFmpeg was not found on your system.' + #13#10 + #13#10 +
        'Song Clipper requires FFmpeg to cut audio files.' + #13#10 + #13#10 +
        'To install FFmpeg:' + #13#10 +
        '  Option A (Recommended): Run in a terminal:' + #13#10 +
        '    winget install Gyan.FFmpeg' + #13#10 + #13#10 +
        '  Option B: Download from https://ffmpeg.org/download.html' + #13#10 +
        '  and copy ffmpeg.exe + ffprobe.exe to:' + #13#10 +
        '    ' + ExpandConstant('{app}') + '\tools\ffmpeg\' + #13#10 + #13#10 +
        'The app will work once FFmpeg is available.',
        mbInformation, MB_OK
      );
    end;
  end;
end;
