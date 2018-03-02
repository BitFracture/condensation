@echo off
pushd .\condensation-forum
echo Installing AWS EB CLI...
pip3.exe install awsebcli --user
echo Initializing EB. If prompted, choose region us-west-2...
eb.exe init condensation-forum
echo Beginning deployment...
eb.exe deploy
popd
@echo on
