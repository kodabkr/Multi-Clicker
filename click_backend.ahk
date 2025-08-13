; #NoEnv is deprecated in v2, so we remove it. Modern scripts don't need it.
SendMode "Input"  ; Use a more reliable method for sending clicks, good for games. String syntax is preferred in v2.
SetWorkingDir A_ScriptDir  ; Ensures the script's working directory is its own folder.
CoordMode "Mouse", "Screen" ; Make sure coordinates are relative to the entire screen.

; This script is designed to be called from the command line by our Python GUI.
; It expects arguments like: click_backend.ahk [X] [Y] [ClickCount]
; Example: click_backend.ahk 800 600 5

; Check if we received enough arguments (at least X and Y)
if (A_Args.Length < 2) {
    ExitApp ; Not enough info, just exit.
}

; Assign arguments to variables for clarity
x := A_Args[1]
y := A_Args[2]

; Assign click count if it was provided, otherwise default to 1
clickCount := A_Args.Length >= 3 ? A_Args[3] : 1

; Move the mouse to the target coordinates
BlockInput "MouseMove" ; Temporarily freeze user mouse movement
MouseMove x, y, 0 ; Move instantly
BlockInput "MouseMoveOff" ; Unfreeze user mouse movement

; Perform the clicks
Loop clickCount
{
    Click
}

; Exit the script immediately after the task is done.
ExitApp