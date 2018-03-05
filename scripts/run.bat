@echo off

echo.
echo Creating virtual environment
echo.
pip3.exe install virtualenv --user
python3.exe -m venv ./.virtualenv

echo.
echo Running virtual environment
echo.
call .\.virtualenv\Scripts\activate.bat py35

pushd condensation-forum

echo installing prerequisites
echo.
pip3 install -r requirements.txt
echo.
echo running application
echo.
python3 ./application.py

popd

call .\.virtualenv\Scripts\deactivate.bat
@echo on
