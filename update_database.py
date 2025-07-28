#!/usr/bin/env python3
"""
Database Update Script for Patient Management System
Adds new tables for prescriptions and diagnoses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Prescription, Diagnosis, Payment

def update_database():
    """Update database with new tables"""
    with app.app_context():
        try:
            # Create new tables
            db.create_all()
            print("✅ Database updated successfully!")
            print("✅ New tables created:")
            print("   - prescriptions")
            print("   - diagnoses")
            print("   - payments")
            
            # Add professional_license column to existing tables if it doesn't exist
            try:
                # Add column to diagnosis table
                db.engine.execute("ALTER TABLE diagnosis ADD COLUMN professional_license VARCHAR(50) DEFAULT '12345678'")
                print("✅ Added professional_license column to diagnosis table")
            except Exception as e:
                print(f"ℹ️  professional_license column already exists in diagnosis table or error: {e}")
            
            try:
                # Add column to prescription table
                db.engine.execute("ALTER TABLE prescription ADD COLUMN professional_license VARCHAR(50) DEFAULT '12345678'")
                print("✅ Added professional_license column to prescription table")
            except Exception as e:
                print(f"ℹ️  professional_license column already exists in prescription table or error: {e}")
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n📊 Current tables in database:")
            for table in tables:
                print(f"   - {table}")
                
        except Exception as e:
            print(f"❌ Error updating database: {e}")
            return False
    
    return True

if __name__ == "__main__":
    update_database() 