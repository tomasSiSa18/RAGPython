from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
import psycopg2

load_dotenv()

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
id = 1000
# Connection config — change to match your Docker config
conn = psycopg2.connect(
    host="localhost",       # or 'db' if you're connecting from another Docker container
    port=5432,
    dbname="vectordb",
    user="user",
    password="password"
)

cur = conn.cursor()

print("Bienvenido a la carga de datos.")
tableName = input("Ingrese el nombre de la tabla: ")

inputUser = input("Por favor ingrese la ruta del archivo, o presione 0 para salir: ") 

while inputUser != "0":

    loader = TextLoader(inputUser, encoding="utf-8")

    documents = loader.load()

    # Configure the splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,    # You can tweak this
        chunk_overlap=200   # Overlap helps preserve context across chunks
    )

    # Split the loaded documents into chunks
    chunks = text_splitter.split_documents(documents)

    docFrom = [chunk.metadata["source"] for chunk in chunks]
    texts = [chunk.page_content for chunk in chunks]
    embeddings = embedding_model.embed_documents(texts)

    
    for docFrom, text, embedding in zip(docFrom, texts, embeddings):
        cur.execute(
            f"INSERT INTO {tableName} (id, origin, content, embedding) VALUES (%s, %s, %s, %s)",
            (id, docFrom, text, embedding)
        )
        id += 1


    conn.commit()
    print("Archivo cargado correctamente.")
    inputUser = input("Por favor ingrese la ruta del archivo, o presione 0 para salir:") 

cur.close()
conn.close()


