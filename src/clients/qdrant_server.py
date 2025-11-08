from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

# Connect to local Qdrant
client = QdrantClient(host="localhost", port=6333)

# Example embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

docs = ["The Amazon River is the largest by volume.",
        "The Nile River is the longest river in the world."]

vectors = model.encode(docs).tolist()

# Create or recreate collection (new API)
if not client.collection_exists(collection_name="rivers"):
    client.create_collection(
        collection_name="rivers",
        vectors_config=VectorParams(size=len(vectors[0]), distance="Cosine"),
    )

# Insert data
points = [PointStruct(id=i, vector=vectors[i], payload={"text": docs[i]}) for i in range(len(docs))]
client.upsert(collection_name="rivers", points=points)

# Query
query_vector = model.encode("Which river is the longest?").tolist()
hits = client.query_points(
    collection_name="rivers",
    query=query_vector,
    limit=3
).points

for hit in hits:
    print(hit.payload, "score:", hit.score)
# results = client.search(collection_name="rivers", query_vector=query_vector, limit=1)

# print("Top result:", results[0].payload["text"])
