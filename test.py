from qdrant import QDrantVectorDatabase

vector = QDrantVectorDatabase()
vector.client.delete_collection(vector.collection_name)