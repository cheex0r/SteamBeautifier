[Setup]
AppId={{3a7441d1-22be-49f6-b612-b34b2b8bae26}}
AppName=Steam Beautifier
AppVersion=1.0
UsePreviousAppDir=no
DefaultDirName={pf}\Steam Beautifier
DefaultGroupName=Steam Beautifier
OutputDir=Output
OutputBaseFilename=Setup_SteamBeautifier
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\steam_beautifier.exe
AllowNoIcons=yes
AlwaysRestart=no

[Files]
Source: "..\..\installer\windows\dist\steam_beautifier.exe"; DestDir: "{app}"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Icons]
Name: "{group}\Steam Beautifier"; Filename: "{app}\steam_beautifier.exe";
Name: "{userdesktop}\Steam Beautifier"; Filename: "{app}\steam_beautifier.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\steam_beautifier.exe"; Flags: postinstall runascurrentuser skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: files; Name: "{userappdata}\Microsoft\Windows\Start Menu\Programs\Startup\SteamBeautifier.lnk"
