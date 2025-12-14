@echo off
REM === Navigate to your Django project ===
cd "C:\Users\samue\OneDrive\Desktop\school work\parttime\PROJECT\project\artist_trends"

REM === Activate virtual environment ===
call venv\Scripts\activate

REM === Run the scheduled update ===
python manage.py update_artist_popularity

REM === Deactivate virtual environment ===
deactivate
