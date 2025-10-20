import sqlite3
import os
from pathlib import Path

def view_database():
    # Find the database file
    db_path = Path('instance/tracker.db')
    if not db_path.exists():
        db_path = Path('tracker.db')
    
    if not db_path.exists():
        print("Database file not found! Looking for:")
        print(" - instance/tracker.db")
        print(" - tracker.db")
        return
    
    print(f"Opening database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List all tables
    print("\n" + "="*50)
    print("TABLES IN DATABASE:")
    print("="*50)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n{table_name}:")
        print("-" * 30)
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print("Columns:", ", ".join(column_names))
        
        # Get sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        rows = cursor.fetchall()
        
        for i, row in enumerate(rows, 1):
            print(f"Row {i}: {row}")
    
    # Show chapter progress summary
    print("\n" + "="*50)
    print("CHAPTER PROGRESS SUMMARY:")
    print("="*50)
    
    cursor.execute("""
        SELECT subject, COUNT(*) as total_chapters,
               SUM(theory) as theory_done,
               SUM(pyqs) as pyqs_done,
               SUM(module_a) as module_a_done,
               SUM(module_b) as module_b_done,
               SUM(cengage) as cengage_done,
               SUM(physics_galaxy) as physics_galaxy_done
        FROM chapter
        GROUP BY subject
    """)
    
    summary = cursor.fetchall()
    for row in summary:
        subject, total, theory, pyqs, mod_a, mod_b, cengage, physics_galaxy = row
        print(f"\n{subject}:")
        print(f"  Total chapters: {total}")
        print(f"  Theory done: {theory}/{total}")
        print(f"  PYQs done: {pyqs}/{total}")
        print(f"  Module A done: {mod_a}/{total}")
        print(f"  Module B done: {mod_b}/{total}")
        if subject == "Mathematics":
            print(f"  Cengage done: {cengage}/{total}")
        if subject == "Physics":
            print(f"  Physics Galaxy done: {physics_galaxy}/{total}")
    
    conn.close()

if __name__ == '__main__':
    view_database()