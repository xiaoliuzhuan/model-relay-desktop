!macro NSIS_HOOK_POSTINSTALL
  IfFileExists "$INSTDIR\resources\pyembed\python\python313.dll" 0 +2
    CopyFiles /SILENT "$INSTDIR\resources\pyembed\python\python313.dll" "$INSTDIR\python313.dll"
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  Delete "$INSTDIR\python313.dll"
!macroend
