import streamlit as st
from db import get_connection

def migrate_database():
    try:
        conn = get_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            
            # Drop verification columns one by one
            try:
                cursor.execute("ALTER TABLE users DROP COLUMN verified")
            except Exception as e:
                print(f"Note: verified column not found or already removed: {str(e)}")
                
            try:
                cursor.execute("ALTER TABLE users DROP COLUMN verification_token")
            except Exception as e:
                print(f"Note: verification_token column not found or already removed: {str(e)}")
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Database migration completed successfully!")
            return True
    except Exception as e:
        print(f"❌ Database migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_database() 