@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Glitch Survivor: creando el .exe ===
rem Se usa pygame-ce (mismo "import pygame"). Se desinstalan los dos para evitar una instalacion mezclada y rota.
python -m pip uninstall -y pygame pygame-ce >nul 2>&1
python -m pip install pygame-ce pyinstaller
if errorlevel 1 goto error
rem Comprobar que el audio de pygame funciona antes de empaquetar
python -c "import pygame; pygame.mixer; print('pygame', pygame.version.ver, '- audio OK')"
if errorlevel 1 goto error
rem Todo lo temporal de PyInstaller se hace en la carpeta TEMP de Windows, no en esta carpeta
set TRABAJO=%TEMP%\GlitchSurvivor_build
set ICONO=
if exist "%~dp0icono.ico" set ICONO=--icon "%~dp0icono.ico"
python -m PyInstaller --onefile --windowed --clean --collect-all pygame %ICONO% --name GlitchSurvivor --distpath "%~dp0." --workpath "%TRABAJO%" --specpath "%TRABAJO%" "%~dp0main.py"
if errorlevel 1 goto error
rem Limpieza: no queda build, dist, .spec ni __pycache__
if exist "%TRABAJO%" rmdir /s /q "%TRABAJO%"
if exist build rmdir /s /q build
if exist GlitchSurvivor.spec del GlitchSurvivor.spec
if exist __pycache__ rmdir /s /q __pycache__
echo.
echo Listo: GlitchSurvivor.exe (en esta misma carpeta). Al abrirlo crea la carpeta data con tus puntajes y ajustes.
pause
exit /b 0
:error
echo.
echo Hubo un error. Si dice que no encuentra una version de pygame-ce para tu Python,
echo instala Python 3.12 o 3.13 y vuelve a ejecutar este archivo.
pause
exit /b 1
