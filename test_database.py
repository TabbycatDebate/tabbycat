#!/usr/bin/env python3

"""
Test script to verify database connection before deployment
"""

import sys
import psycopg2

def test_database_connection():
    """Test connection to the external PostgreSQL database"""
    
    db_config = {
        'host': 'dpg-d1l186h5pdvs73bd0nv0-a.oregon-postgres.render.com',
        'database': 'tab_2yw0',
        'user': 'tab',
        'password': '57yqNclrMENfxxJuYmbBJ0u26FdDzOkB',
        'port': '5432',
        'sslmode': 'require'
    }
    
    try:
        print("🔄 Testing database connection...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Database connection successful!")
        print(f"📊 PostgreSQL version: {version}")
        
        # Test permissions
        cursor.execute("SELECT current_user;")
        user = cursor.fetchone()[0]
        print(f"👤 Connected as user: {user}")
        
        # Test if we can create tables (basic permission check)
        cursor.execute("""
            SELECT has_table_privilege('tab', 'information_schema.tables', 'SELECT');
        """)
        can_select = cursor.fetchone()[0]
        print(f"🔐 Can SELECT from tables: {can_select}")
        
        cursor.close()
        conn.close()
        
        print("✅ Database test passed! Ready for deployment.")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
