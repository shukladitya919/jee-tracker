import os
import sys

def check_postgresql_simple():
    """Simple PostgreSQL database check without psycopg2 issues"""
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not found!")
        return
    
    print(f"📊 Checking PostgreSQL Database...")
    print(f"Database URL present: Yes")
    print(f"Database URL starts with: {database_url[:20]}...")
    
    # Check if we can import PostgreSQL libraries
    try:
        # Try psycopg2 first
        import psycopg2
        print("✅ psycopg2 imported successfully")
        
        # Fix URL format
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        # Test connection
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get basic info
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to PostgreSQL: {version.split(',')[0]}")
        
        # Count tables
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        print(f"📊 Tables in database: {table_count}")
        
        # List tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print("📋 Table names:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if our tables exist
        expected_tables = ['chapter', 'subject_books']
        for expected_table in expected_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (expected_table,))
            exists = cursor.fetchone()[0]
            status = "✅" if exists else "❌"
            print(f"{status} {expected_table} table: {'Exists' if exists else 'Missing'}")
        
        # Count rows in chapter table
        if any('chapter' in table[0] for table in tables):
            cursor.execute("SELECT COUNT(*) FROM chapter")
            chapter_count = cursor.fetchone()[0]
            print(f"📚 Chapters in database: {chapter_count}")
            
            # Show subject distribution
            cursor.execute("SELECT subject, COUNT(*) FROM chapter GROUP BY subject")
            subjects = cursor.fetchall()
            print("📖 Chapters by subject:")
            for subject, count in subjects:
                print(f"  - {subject}: {count} chapters")
        
        conn.close()
        
    except ImportError as e:
        print(f"❌ Could not import psycopg2: {e}")
        print("💡 Try updating requirements.txt to use psycopg2-binary==2.9.9")
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("This might be normal if the database is still initializing")

def check_python_environment():
    """Check Python environment details"""
    print("🐍 Python Environment:")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check installed packages
    try:
        import pkg_resources
        packages = ['Flask', 'Flask-SQLAlchemy', 'psycopg2', 'psycopg2-binary', 'pg8000']
        for package in packages:
            try:
                version = pkg_resources.get_distribution(package).version
                print(f"✅ {package}: {version}")
            except:
                print(f"❌ {package}: Not installed")
    except:
        print("⚠️  Could not check package versions")

if __name__ == '__main__':
    print("🔍 PostgreSQL Database Diagnostic Tool")
    print("=" * 50)
    
    check_python_environment()
    print("\n")
    check_postgresql_simple()

init_db()

if __name__ == '__main__':
    app.run(debug=False)

# ⭐ ADD THIS LINE - fixes Gunicorn error ⭐
app = app
