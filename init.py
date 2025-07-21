import psycopg2

# Connection config — change to match your Docker config
conn = psycopg2.connect(
    host="localhost",       # or 'db' if you're connecting from another Docker container
    port=5432,
    dbname="vectordb",
    user="user",
    password="password"
)

cur = conn.cursor()

# Enable pgvector extension (if not already enabled)
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

# Create a table with a vector column
cur.execute("""
    DROP TABLE IF EXISTS Biomateriales;
    CREATE TABLE Biomateriales (
        id SERIAL PRIMARY KEY,
        origin TEXT, 
        content TEXT,
        embedding VECTOR(1536)
    );
""")


conn.commit()
cur.close()
conn.close()
