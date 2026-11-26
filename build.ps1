# exe로 묶고 바탕화면에 바로가기를 만든다. 실행: powershell -ExecutionPolicy Bypass -File build.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path engine\stockfish.exe)) { python get_stockfish.py }

pyinstaller --noconfirm --windowed --name BoardGames main.py
New-Item -ItemType Directory -Force dist\BoardGames\engine | Out-Null
Copy-Item engine\stockfish.exe dist\BoardGames\engine\ -Force

$exe = Join-Path $PSScriptRoot "dist\BoardGames\BoardGames.exe"
$lnk = Join-Path ([Environment]::GetFolderPath("Desktop")) "보드게임.lnk"
$s = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$s.TargetPath = $exe
$s.WorkingDirectory = Split-Path $exe
$s.Save()
Write-Host "완료: $lnk"
