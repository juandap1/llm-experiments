from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams
from sentence_transformers import SentenceTransformer
import uuid


class QdrantServerClient:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")


    def upsert_vectors(self, collection_name: str, vectors: list[str], chunks: list[str], ticker: str, timestamp: str, source: str = "", url: str = ""):
        # if collection does not exist, create it
        if not self.client.collection_exists(collection_name=collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=len(vectors[0]), distance="Cosine"),
            )
        
        points = [
            PointStruct(
                id=str(uuid.uuid4()), 
                vector=vectors[i], 
                payload={
                    "text": chunks[i],
                    "ticker": ticker,
                    "timestamp": timestamp,
                    "source": source,
                    "url": url
                }
            )
            for i in range(len(vectors))
        ]
        self.client.upsert(collection_name=collection_name, points=points)

    def encode_texts(self, chunks: list[str]) -> list[list[float]]:
        return self.model.encode(chunks).tolist()

    def query(self, collection_name: str, query_text: str, limit: int = 3):
        query_vector = self.model.encode(query_text).tolist()
        hits = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit
        ).points
        return hits



# docs = ["The Amazon River is the largest by volume.",
#         "The Nile River is the longest river in the world."]

# vectors = model.encode(docs).tolist()

# # Create or recreate collection (new API)
# if not client.collection_exists(collection_name="rivers"):
#     client.create_collection(
#         collection_name="rivers",
#         vectors_config=VectorParams(size=len(vectors[0]), distance="Cosine"),
#     )

# # Insert data
# points = [PointStruct(id=i, vector=vectors[i], payload={"text": docs[i]}) for i in range(len(docs))]
# client.upsert(collection_name="rivers", points=points)

# # Query
# query_vector = model.encode("Which river is the longest?").tolist()
# hits = client.query_points(
#     collection_name="rivers",
#     query=query_vector,
#     limit=3
# ).points

# for hit in hits:
#     print(hit.payload, "score:", hit.score)
# results = client.search(collection_name="rivers", query_vector=query_vector, limit=1)

# print("Top result:", results[0].payload["text"])
