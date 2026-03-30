@echo off
echo ========================================
echo Wordastra Blog Setup Script
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error creating virtual environment!
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate
echo.

echo Step 3: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo Step 4: Checking for .env file...
if not exist .env (
    echo .env file not found!
    echo Please copy .env.example to .env and configure it.
    copy .env.example .env
    echo .env file created. Please edit it with your credentials.
    pause
    exit /b 1
)
echo .env file found!
echo.

echo Step 5: Running migrations...
python manage.py makemigrations
python manage.py migrate
if %errorlevel% neq 0 (
    echo Error running migrations!
    pause
    exit /b 1
)
echo Migrations completed successfully!
echo.

echo Step 6: Collecting static files...
python manage.py collectstatic --noinput
echo Static files collected!
echo.

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your credentials
echo 2. Create superuser: python manage.py createsuperuser
echo 3. Run server: python manage.py runserver
echo.
pause
