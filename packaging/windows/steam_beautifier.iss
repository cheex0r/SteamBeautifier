[Setup]
AppName=Steam Beautifier
AppVersion=1.0
UsePreviousAppDir=no
DefaultDirName={pf}\Steam Beautifier
DefaultGroupName=Steam Beautifier
OutputDir=Output
OutputBaseFilename=Setup_SteamBeautifier
Compression=lzma
SolidCompression=yes

[Files]
Source: "..\..\installer\windows\dist\steam_beautifier.exe"; DestDir: "{app}"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Icons]
Name: "{group}\Steam Beautifier"; Filename: "{app}\steam_beautifier.exe";
Name: "{userdesktop}\Steam Beautifier"; Filename: "{app}\steam_beautifier.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\steam_beautifier.exe"; Flags: postinstall runascurrentuser skipifsilent
