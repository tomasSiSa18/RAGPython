from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
import psycopg2

load_dotenv()

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
loader = PyMuPDFLoader("Taller2SolucionMonitores.pdf")

documents = loader.load()

"""
# Let's inspect what we got
print(f"Loaded {len(documents)} pages")
print(documents[0].page_content[:500]) 
"""

# Configure the splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,    # You can tweak this
    chunk_overlap=200   # Overlap helps preserve context across chunks
)

# Split the loaded documents into chunks
chunks = text_splitter.split_documents(documents)

texts = [chunk.page_content for chunk in chunks]
embeddings = embedding_model.embed_documents(texts)

# Connection config — change to match your Docker config
conn = psycopg2.connect(
    host="localhost",       # or 'db' if you're connecting from another Docker container
    port=5432,
    dbname="vectordb",
    user="user",
    password="password"
)

cur = conn.cursor()

for text, embedding in zip(texts, embeddings):
    cur.execute(
        "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
        (text, embedding)
    )

conn.commit()
cur.close()
conn.close()

