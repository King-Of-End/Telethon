from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

def main():
    client = QdrantClient(
        url="http://localhost:6333",
    )

    collection_name = 'tasks'

    if not client.collection_exists(collection_name=collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=4,
                distance=Distance.COSINE
            ),
        )

if __name__ == "__main__":
    main()
