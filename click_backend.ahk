SendMode "Input"
SetWorkingDir A_ScriptDir
CoordMode "Mouse", "Screen"

if (A_Args.Length < 2) {
    ExitApp
}

x := A_Args[1]
y := A_Args[2]

clickCount := A_Args.Length >= 3 ? A_Args[3] : 1

BlockInput "MouseMove"
MouseMove x, y, 0
BlockInput "MouseMoveOff"

loop clickCount {
    Click
}

ExitApp