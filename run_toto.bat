@echo off
REM Runner for TOTO Playwright scraper
SETLOCAL ENABLEEXTENSIONS
CD /D %~dp0

REM If you use a virtualenv, activate it here, e.g.:
REM call .venv\Scripts\activate.bat

python -m notifier.toto_main
SET EXITCODE=%ERRORLEVEL%
echo Exited with code %EXITCODE%
exit /b %EXITCODE%
