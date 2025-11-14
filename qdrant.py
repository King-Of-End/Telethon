from typing import List
import os

from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Settings, StorageContext, VectorStoreIndex, Document, load_index_from_storage
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.models import Distance

Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url='http://star-curriculum.gl.at.ply.gg:58596',
    embed_batch_size=10,
)


class QDrantVectorDatabase:
    def __init__(self) -> None:
        self.collection_name = 'tasks'
        self.persist_dir = "databases/index"

        os.makedirs(self.persist_dir, exist_ok=True)

        self._init_qdrant_client()

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
                persist_dir=r'C:databases\index'
            )
        except LookupError:
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store,
            )
            self.storage_context.persist(
                persist_dir=r'databases\index'
            )
        try:
            self.index = load_index_from_storage(self.storage_context)
        except ValueError as e:
            self.index = VectorStoreIndex.from_documents(
                documents=[],
                storage_context=self.storage_context,
                show_progress=True
            )
            self.storage_context.persist(
                persist_dir=r'databases\index'
            )

        self.node_parser = SentenceSplitter(
            chunk_size=512,
            chunk_overlap=50,
            paragraph_separator="\n\n"
        )

    def _init_qdrant_client(self):
        """Инициализация Qdrant клиента с правильной обработкой ошибок"""
        try:
            self.client = QdrantClient(
                url="reviews-phones.gl.at.ply.gg:42376",
            )
            self._ensure_collection_exists()
        except Exception as e1:
            try:
                self.client = QdrantClient(
                    url="http://localhost:6333",
                )
                self._ensure_collection_exists()
            except Exception as e2:
                self.client = QdrantClient(path="/tmp/qdrant_local")
                self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Гарантирует существование коллекции"""
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=rest.VectorParams(
                    size=768,
                    distance=rest.Distance.COSINE
                )
            )

    def _init_index(self):
        """Корректная инициализация индекса"""
        try:
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store,
                persist_dir=self.persist_dir
            )
            self.index = load_index_from_storage(
                storage_context=self.storage_context
            )
        except Exception as e:
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store,
            )
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                storage_context=self.storage_context
            )
            self.storage_context.persist(persist_dir=self.persist_dir)

    def add_task(self,
                 task: str | None = None,
                 date: str | None = None,
                 time: str | None = None,
                 priority: int | None = None) -> str | None:
        """Добавление задачи в векторную базу данных"""
        if not task or not task.strip():
            return None

        metadata = {
            'date': date,
            'time': time,
            'priority': priority,
        }

        try:
            node = TextNode(
                text=task,
                metadata=metadata
            )

            self.index.insert_nodes([node])

            self.storage_context.persist(persist_dir=self.persist_dir)
            return node.node_id
        except Exception as e:
            return None

    def delete_task(self, task_id: str) -> None:
        """Удаление задачи по ID"""
        try:
            self.index.delete_ref_doc(
                ref_doc_id=task_id,
                delete_from_docstore=True
            )
            self.storage_context.persist(persist_dir=self.persist_dir)
        except Exception as e:
            pass

    def get_task(self, query: str, k: int = 3) -> List[NodeWithScore]:
        """Получение задач по запросу"""
        try:
            retriever = self.index.as_retriever(similarity_top_k=k)
            results = retriever.retrieve(query)
            return results
        except Exception as e:
            return []
