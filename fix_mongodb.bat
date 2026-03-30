@echo off
echo ========================================
echo MongoDB Setup Fix for Wordastra
echo ========================================
echo.

echo Step 1: Uninstalling old packages...
pip uninstall djongo pymongo sqlparse -y

echo.
echo Step 2: Installing correct versions...
pip install pymongo==4.6.0
pip install sqlparse==0.2.4
pip install djongo==1.3.6

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo IMPORTANT: You MUST setup MongoDB Atlas!
echo.
echo 1. Go to: https://www.mongodb.com/cloud/atlas/register
echo 2. Create FREE account
echo 3. Create cluster (M0 FREE tier)
echo 4. Create database user
echo 5. Whitelist IP: 0.0.0.0/0
echo 6. Get connection string
echo 7. Update .env file with your MongoDB URI
echo.
echo See MONGODB_SETUP.md for detailed instructions
echo.
pause
