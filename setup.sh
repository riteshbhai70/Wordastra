#!/bin/bash

echo "========================================"
echo "Wordastra Blog Setup Script"
echo "========================================"
echo ""

echo "Step 1: Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error creating virtual environment!"
    exit 1
fi
echo "Virtual environment created successfully!"
echo ""

echo "Step 2: Activating virtual environment..."
source venv/bin/activate
echo ""

echo "Step 3: Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error installing dependencies!"
    exit 1
fi
echo "Dependencies installed successfully!"
echo ""

echo "Step 4: Checking for .env file..."
if [ ! -f .env ]; then
    echo ".env file not found!"
    echo "Please copy .env.example to .env and configure it."
    cp .env.example .env
    echo ".env file created. Please edit it with your credentials."
    exit 1
fi
echo ".env file found!"
echo ""

echo "Step 5: Running migrations..."
python manage.py makemigrations
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Error running migrations!"
    exit 1
fi
echo "Migrations completed successfully!"
echo ""

echo "Step 6: Collecting static files..."
python manage.py collectstatic --noinput
echo "Static files collected!"
echo ""

echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Create superuser: python manage.py createsuperuser"
echo "3. Run server: python manage.py runserver"
echo ""
