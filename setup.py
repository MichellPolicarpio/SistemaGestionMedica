#!/usr/bin/env python3
"""
Setup Script for Patient Management System
This script helps users set up the patient management system.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['static', 'templates']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")

def check_mysql():
    """Check if MySQL is available"""
    print("\n🗄️ Checking MySQL connection...")
    try:
        import mysql.connector
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password'
        )
        if connection.is_connected():
            print("✅ MySQL connection successful")
            connection.close()
            return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\nPlease ensure:")
        print("1. MySQL server is installed and running")
        print("2. MySQL credentials are correct")
        print("3. Update the database connection in app.py if needed")
        return False

def setup_database():
    """Set up the database"""
    print("\n🗄️ Setting up database...")
    try:
        subprocess.check_call([sys.executable, "database_setup.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🏥 Patient Management System - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Check MySQL
    mysql_ok = check_mysql()
    
    # Setup database if MySQL is available
    if mysql_ok:
        if setup_database():
            print("✅ Database setup completed")
        else:
            print("⚠️ Database setup failed, but you can continue with manual setup")
    else:
        print("⚠️ Skipping database setup due to MySQL connection issues")
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next Steps:")
    print("1. If database setup failed, run: python database_setup.py")
    print("2. Update database credentials in app.py if needed")
    print("3. Run the application: python app.py")
    print("4. Access the system at: http://localhost:5000")
    
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main() 