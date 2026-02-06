@echo off
setlocal
set ICE_CRAWLER_FORCE_PYTHON=1

where pyw >nul 2>nul
if %ERRORLEVEL%==0 (
  pyw -3 "%~dp0icecrawler.py"
  exit /b %ERRORLEVEL%
)

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 "%~dp0icecrawler.py"
  exit /b %ERRORLEVEL%
)

where pythonw >nul 2>nul
if %ERRORLEVEL%==0 (
  pythonw "%~dp0icecrawler.py"
  exit /b %ERRORLEVEL%
)

python "%~dp0icecrawler.py"
exit /b %ERRORLEVEL%
