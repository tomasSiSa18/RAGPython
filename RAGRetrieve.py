from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
import psycopg2

load_dotenv()

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

# Connection config — change to match your Docker config
conn = psycopg2.connect(
    host="localhost",       # or 'db' if you're connecting from another Docker container
    port=5432,
    dbname="vectordb",
    user="user",
    password="password"
)

query_embedding = embedding_model.embed_query("Fundamental concepts of atomic structure")
cur = conn.cursor()

cur.execute(
    """
    SELECT content, embedding <-> %s::vector AS distance
    FROM documents
    ORDER BY distance
    LIMIT 5;
    """,
    (query_embedding,)
)

results = cur.fetchall()
for row in results:
    content, distance = row
    print(f"[{distance:.4f}] {content[:200]}...\n")