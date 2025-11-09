import datetime

from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings, StorageContext, VectorStoreIndex, Document, load_index_from_storage
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

Settings.embed_model = HuggingFaceEmbedding(
    model_name="intfloat/e5-large-v2",
    embed_batch_size=32,
    normalize=True,
    query_instruction="passage: "
)


class QDrantVectorDatabase:
    def __init__(self) -> None:
        self.client = QdrantClient(
            url="http://localhost:6333",
            grpc_port=6334,
            prefer_grpc=True
        )

        self.collection_name = 'tasks'

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(self.collection_name)

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            dimension=1024,
            distance=Distance.COSINE,
            on_disk_payload=True,
            shard_number=2,
            replication_factor=2
        )

        try:
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store,
                persist_dir=r'C:\Users\NIKITA\PycharmProjects\Telethon\databases\index'
            )
        except FileNotFoundError:
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store,
            )
            self.storage_context.persist(
                persist_dir=r'C:\Users\NIKITA\PycharmProjects\Telethon\databases\index'
            )

        try:
            self.index = load_index_from_storage(self.storage_context)
        except ValueError:
            self.index = VectorStoreIndex.from_documents(
                documents=[],
                storage_context=self.storage_context,
                show_progress=True
            )

        self.node_parser = SentenceSplitter(
            chunk_size=512,
            chunk_overlap=50,
            paragraph_separator="\n\n"
        )

    def add_task(self, task: str, time: datetime.datetime) -> None:
        """Добавление задачи в векторную базу данных"""
        if not task.strip():
            return
        metadata = {
            'time': str(time),
            'priority': int,
        }
        doc = Document(
            text=task,
            metadata=metadata,
        )
        try:
            nodes = self.node_parser.parse_document(doc)
            self.index.insert(nodes)
        except Exception:
            pass
        return

    def delete_task(self, task_id: int) -> None:
        """Удаление точек по id задачи"""
        self.index.delete_ref_doc(
            ref_doc_id=str(task_id),
            delete_from_docstore=True
        )

    def get_task(self, query: str, k: int) -> str:
        """Получение задачи из векторной базы данных"""
        query_engine = self.index.as_query_engine(

        )

vector = QDrantVectorDatabase()