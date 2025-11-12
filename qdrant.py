from typing import List

from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Settings, StorageContext, VectorStoreIndex, Document, load_index_from_storage
from llama_index.core.schema import NodeWithScore
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance

Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url='http://star-curriculum.gl.at.ply.gg:58596/api',
    embed_batch_size=10,
)


class QDrantVectorDatabase:
    def __init__(self) -> None:
        self.collection_name = 'tasks'
        try:
            self.client = QdrantClient(
                url="http://localhost:6333",
            )
            if not self.client.collection_exists(self.collection_name):
                self.client.create_collection(self.collection_name)

        except Exception:
            self.client = QdrantClient(path="/tmp/qdrant_local")
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

    def add_task(self,
                 task: str | None = None,
                 date: str | None = None,
                 time: str | None = None,
                 priority: int | None = None) -> str | None:
        """Добавление задачи в векторную базу данных, возвращает id документа при успехе"""
        if not task.strip():
            return None
        metadata = {
            'date': date,
            'time': time,
            'priority': priority,
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
        return doc.doc_id

    def delete_task(self, task_id: int) -> None:
        """Удаление точек по id задачи"""
        self.index.delete_ref_doc(
            ref_doc_id=str(task_id),
            delete_from_docstore=True
        )

    def get_task(self, query: str, k: int = 3) -> List[NodeWithScore]:
        """Получение задачи из векторной базы данных"""
        query_engine = self.index.as_query_engine(
            similarity_top_k=k
        )

        return query_engine.query(query).source_nodes

QDrantVectorDatabase()