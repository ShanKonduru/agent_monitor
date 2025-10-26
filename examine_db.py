import sqlite3

# Connect to the database
conn = sqlite3.connect('data/agent_monitor.db')
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in agent_monitor.db:")
for table in tables:
    print(f"  - {table[0]}")

print("\nDatabase size: 299KB")
print("Last modified: 2025-10-24 11:48:36 PM")

# Get row counts for each table
print("\nTable row counts:")
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  - {table_name}: {count} rows")

conn.close()