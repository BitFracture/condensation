@echo off
pushd condensation-forum

echo Generating Database
pip install sqlalchemy --user
pip install psycopg2 --user
python3.exe _regenerate_db.py
echo Finished

popd
@echo on
