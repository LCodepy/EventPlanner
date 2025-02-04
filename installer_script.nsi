OutFile "EventPlannerInstaller.exe"
InstallDir "$PROGRAMFILES\EventPlanner"
Icon "event_planner.ico"
RequestExecutionLevel admin

Page directory
Page instfiles
UninstPage uninstconfirm
UninstPage instfiles

Section "Install"
    CreateDirectory "$INSTDIR"
    SetOutPath "$INSTDIR"
    
    File "event_planner.exe"
    File "event_planner.ico"
    
    SetOutPath "$LOCALAPPDATA\EventPlanner"
    CreateDirectory "$LOCALAPPDATA\EventPlanner"
    CreateDirectory "$LOCALAPPDATA\EventPlanner\data"
    CreateDirectory "$LOCALAPPDATA\EventPlanner\data\calendars"
    CreateDirectory "$LOCALAPPDATA\EventPlanner\data\todo_lists"
    CreateDirectory "$LOCALAPPDATA\EventPlanner\tokens"
    CreateDirectory "$LOCALAPPDATA\EventPlanner\settings"

    CreateDirectory "$SMPrograms\Event Planner"
    CreateShortcut "$SMPrograms\Event Planner\Event Planner.lnk" "$INSTDIR\event_planner.exe" "$LOCALAPPDATA\EventPlanner" "$INSTDIR\event_planner.ico"

    WriteUninstaller "$INSTDIR\uninstaller.exe"

    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Event Planner" "DisplayName" "Event Planner"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Event Planner" "DisplayIcon" "$INSTDIR\event_planner.ico"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Event Planner" "UninstallString" "$INSTDIR\uninstaller.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Event Planner" "InstallLocation" "$INSTDIR"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Event Planner" "Publisher" "Lovro Gale"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Event Planner" "DisplayVersion" "1.0"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\event_planner.exe"
    Delete "$INSTDIR\event_planner.ico"
    Delete "$INSTDIR\uninstaller.exe"

    RMDir /r "$LOCALAPPDATA\EventPlanner\data\calendars"
    RMDir /r "$LOCALAPPDATA\EventPlanner\data\todo_lists"
    RMDir /r "$LOCALAPPDATA\EventPlanner\tokens"
    RMDir /r "$LOCALAPPDATA\EventPlanner\settings"
    RMDir "$LOCALAPPDATA\EventPlanner"
    
    RMDir "$INSTDIR"
    RMDir "$SMPrograms\Event Planner"
    
    Delete "$SMPrograms\Event Planner\Event Planner.lnk"

    DeleteRegKey HKCU "Software\Event Planner"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Event Planner"
SectionEnd
