from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
import psycopg2
from tabulate import tabulate

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

print("Bienvenido al retrieval del RAG")

prompt = input("Ingrese un prompt:")

while prompt != "0":

    query_embedding = embedding_model.embed_query(prompt)
    cur = conn.cursor()

    distancias = ["<->", "<#>", "<=>"]
    tipoDist = ["Euclideana", "Coseno", "Producto Interno"]

    for dist, tipo in zip(distancias, tipoDist):

        cur.execute(
            f"""
            SELECT origin, content, embedding {dist} %s::vector AS distance
            FROM biomateriales
            ORDER BY distance
            LIMIT 5;
            """,
            (query_embedding,)
        )

        results = cur.fetchall()
        finalList = []
        headers = ["Origin", "Content", "Distance"]
        for row in results:
            origin, content, distance = row
            rowTb = [origin, content[:200], round(distance, 4)]
            finalList.append(rowTb)
        
        print(f"El resultado para la distancia {tipo} son:")
        print(tabulate(finalList, headers=headers, tablefmt="grid"))
    prompt = input("Ingrese un prompt:")


cur.close()
conn.close()