#!/bin/bash

cd ./condensation-forum
echo "Installing AWS EB CLI..."
pip3 install awsebcli --user
export PATH="~/Library/Python/3.4/bin":$PATH
export PATH="~/.local/bin":$PATH
echo "Initializing EB. If prompted, choose region us-west-2..."
eb init condensation-forum
echo "Beginning deployment..."
eb deploy
cd ..
