@echo checking and installing required packages now
@python -m venv bbdc
@CALL .\bbdc\Scripts\activate.bat
@python -m pip install -r requirements.txt
@start python mainPRAC.py
