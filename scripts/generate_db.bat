@echo off
pushd condensation-forum

echo Generating Database
python3.exe _regenerate_db.py
echo Finished

popd
@echo on


