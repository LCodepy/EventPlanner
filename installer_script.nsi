OutFile "EventPlannerInstaller.exe"
InstallDir "$PROGRAMFILES\EventPlanner"  ; Use a user-writable directory
Icon "event_planner.ico"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "Install"
    CreateDirectory "$INSTDIR"
    SetOutPath "$INSTDIR"
    
    File "event_planner.exe"  ; Ensure the file exists at this location
    File "event_planner.ico"  ; Ensure the icon exists at this location
    
    SetOutPath "$LOCALAPPDATA\EventPlanner"
    CreateDirectory "$LOCALAPPDATA\EventPlanner"
    CreateDirectory "$LOCALAPPDATA\EventPlanner\data"
    CreateDirectory "$LOCALAPPDATA\EventPlanner\data\calendars"
    CreateDirectory "$LOCALAPPDATA\EventPlanner\data\todo_lists"
    CreateDirectory "$LOCALAPPDATA\EventPlanner\tokens"
    CreateDirectory "$LOCALAPPDATA\EventPlanner\settings"

    CreateShortcut "$DESKTOP\EventPlanner.lnk" "$INSTDIR\event_planner.exe" "$LOCALAPPDATA\EventPlanner" "$INSTDIR\event_planner.ico"
SectionEnd
