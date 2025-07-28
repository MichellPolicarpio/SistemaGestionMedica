#!/usr/bin/env python3
"""
Database Setup Script for Patient Management System
This script creates the MySQL database and tables for the patient management system.
"""

import mysql.connector
from mysql.connector import Error

def create_database():
    """Create the patient_management database"""
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password'  # Change this to your MySQL password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS patient_management")
            print("✅ Database 'patient_management' created successfully")
            
            # Use the database
            cursor.execute("USE patient_management")
            
            # Create tables
            create_tables(cursor)
            
            cursor.close()
            connection.close()
            print("✅ Database setup completed successfully!")
            
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        print("\nPlease make sure:")
        print("1. MySQL is installed and running")
        print("2. MySQL credentials are correct")
        print("3. You have permission to create databases")

def create_tables(cursor):
    """Create all necessary tables"""
    
    # Patient table
    patient_table = """
    CREATE TABLE IF NOT EXISTS patient (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        phone VARCHAR(20) NOT NULL,
        date_of_birth DATE NOT NULL,
        address TEXT NOT NULL,
        height FLOAT NOT NULL,
        weight FLOAT NOT NULL,
        past_illnesses TEXT,
        current_medications TEXT,
        allergies TEXT,
        food_habits TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    
    # Disease table
    disease_table = """
    CREATE TABLE IF NOT EXISTS disease (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        diagnosis_date DATE NOT NULL,
        status VARCHAR(50) DEFAULT 'Active',
        notes TEXT,
        patient_id INT NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
    )
    """
    
    # Medication table
    medication_table = """
    CREATE TABLE IF NOT EXISTS medication (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        dosage VARCHAR(50) NOT NULL,
        frequency VARCHAR(50) NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE,
        status VARCHAR(50) DEFAULT 'Active',
        notes TEXT,
        patient_id INT NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
    )
    """
    
    try:
        cursor.execute(patient_table)
        print("✅ Patient table created")
        
        cursor.execute(disease_table)
        print("✅ Disease table created")
        
        cursor.execute(medication_table)
        print("✅ Medication table created")
        
    except Error as e:
        print(f"❌ Error creating tables: {e}")

def insert_sample_data(cursor):
    """Insert sample data for testing"""
    try:
        # Sample patient
        patient_data = """
        INSERT INTO patient (name, email, phone, date_of_birth, address, height, weight, past_illnesses, current_medications, allergies, food_habits) 
        VALUES ('John Doe', 'john.doe@email.com', '+1234567890', '1985-03-15', '123 Main St, City, State 12345', 175.0, 70.0, 'None', 'None', 'None', 'Regular diet')
        """
        cursor.execute(patient_data)
        
        # Sample disease
        disease_data = """
        INSERT INTO disease (name, diagnosis_date, status, notes, patient_id) 
        VALUES ('Hypertension', '2023-01-10', 'Active', 'Mild hypertension, monitoring required', 1)
        """
        cursor.execute(disease_data)
        
        # Sample medication
        medication_data = """
        INSERT INTO medication (name, dosage, frequency, start_date, status, patient_id) 
        VALUES ('Lisinopril', '10mg', 'Once daily', '2023-01-15', 'Active', 1)
        """
        cursor.execute(medication_data)
        
        print("✅ Sample data inserted successfully")
        
    except Error as e:
        print(f"❌ Error inserting sample data: {e}")

if __name__ == "__main__":
    print("🏥 Patient Management System - Database Setup")
    print("=" * 50)
    
    # Create database and tables
    create_database()
    
    print("\n📋 Next Steps:")
    print("1. Update the database connection in app.py if needed")
    print("2. Install Python dependencies: pip install -r requirements.txt")
    print("3. Run the application: python app.py")
    print("4. Access the system at: http://localhost:5000") 