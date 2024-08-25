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
Source: "installer\windows\dist\steam_beautifier.exe"; DestDir: "{app}"
; Add any other application files here

[icons]
Name: "{userstartup}\My Program"; Filename: "{app}\steam_beautifier.exe"; Tasks:StartMenuEntry;
Name: "{commonstartup}\My Program"; Filename: "{app}\steam_beautifier.exe"; Tasks:StartMenuEntry;

[Run]
Filename: "{app}\steam_beautifier.exe"; Flags: postinstall runascurrentuser skipifsilent