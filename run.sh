#!/bin/bash

#NOTE!!
#For debian/ubuntu environments only! If you run something else you will need to create your own script

#If .venv doesn't exist, test install all dependencies then create
if [ ! -d ".venv/" ]; then
    echo "Creating Python Virtual Environment Directory..."
    sudo apt-get install python3
    sudo apt-get install python3.10-venv
    python3 -m venv .venv
else
    echo "Python Virtual Environment Directory Exists"
fi

#Once we've checked, changed directory to the activation script and create a new environment (source command) using .venv
cd .venv/bin/
source activate

cd ..
cd ..

#Install all necessary dependencies on the new environment
python -m pip install --upgrade pip
pip install fastapi[standard]
pip install requests
pip install numpy
pip install pandas
pip install matplotlib

#Run application
fastapi dev main.py

sleep 1d
