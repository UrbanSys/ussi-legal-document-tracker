"""
Initialize the database by running the schema SQL file.
Run this once to create all tables and seed data.
"""
from sqlalchemy import text
from app.database import engine

def init_database():
    """Execute the database_schema.sql file to create tables."""
    
    # Read the SQL file
    with open("database_schema.sql", "r") as f:
        sql_content = f.read()
    
    # Split into individual statements (SQL Server uses GO or semicolons)
    # Remove comments and split by semicolon
    statements = []
    current_statement = []
    
    for line in sql_content.split('\n'):
        # Skip comment-only lines
        stripped = line.strip()
        if stripped.startswith('--') or not stripped:
            continue
        current_statement.append(line)
        if stripped.endswith(';'):
            statements.append('\n'.join(current_statement))
            current_statement = []
    
    # Add any remaining statement
    if current_statement:
        statements.append('\n'.join(current_statement))
    
    # Execute each statement
    with engine.connect() as conn:
        for i, stmt in enumerate(statements, 1):
            stmt = stmt.strip()
            if stmt:
                try:
                    conn.execute(text(stmt))
                    print(f"✓ Statement {i} executed successfully")
                except Exception as e:
                    print(f"✗ Statement {i} failed: {e}")
                    print(f"  SQL: {stmt[:100]}...")
        
        conn.commit()
        print("\n✓ Database initialization complete!")

if __name__ == "__main__":
    print("Initializing database with schema from database_schema.sql...")
    print(f"Connecting to: {engine.url}\n")
    init_database()

