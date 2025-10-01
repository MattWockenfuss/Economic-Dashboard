:: alright this batch file, when run, will create a .venv if it doest exist,
::use .venv
::upgrade pip and packages
::doesnt currently handle upgrading the packages or anything
::
::Written by a probably dumb Matt Wockenfuss 9-21-2025
@echo off

color 0f

IF NOT EXIST ".venv\" (
    echo "Python Virtual Environment (.venv) DOESNT EXIST, CREATING"
    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install fastapi[standard]
    pip install requests
    pip install numpy
    pip install pandas
    pip install matplotlib
    fastapi dev main.py
    pause
) ELSE (
    .venv\Scripts\activate
    echo "Python Virtual Environment (.venv) ALREADY EXISTS"
    fastapi dev main.py
    pause
)

