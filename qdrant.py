from typing import List
import os

from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Settings, StorageContext, VectorStoreIndex, Document
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.models import Distance

# Настройка embeddings
Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url='http://star-curriculum.gl.at.ply.gg:58596',
    embed_batch_size=10,
)


class QDrantVectorDatabase:
    def __init__(self) -> None:
        self.collection_name = 'tasks'
        self.persist_dir = "databases/index"  # Корректный путь

        # Создаем директорию для сохранения
        os.makedirs(self.persist_dir, exist_ok=True)

        # Инициализация клиента Qdrant
        self._init_qdrant_client()

        # Инициализация vector store
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            dimension=768,
            distance=Distance.COSINE,
        )

        # Инициализация индекса
        self._init_index()

        # Инициализация парсера
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
            # Попытка загрузить существующий индекс
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store,
                persist_dir=self.persist_dir
            )
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                storage_context=self.storage_context
            )
            print("Индекс успешно загружен из хранилища")
        except Exception as e:
            print(f"Ошибка при загрузке индекса: {e}")
            # Создание нового индекса
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store,
            )
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                storage_context=self.storage_context
            )
            self.storage_context.persist(persist_dir=self.persist_dir)
            print("Создан новый индекс")

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
            # Создаем узел вручную для большего контроля
            node = TextNode(
                text=task,
                metadata=metadata
            )

            # Добавляем документ напрямую в индекс
            self.index.insert_nodes([node])

            # Сохраняем изменения
            self.storage_context.persist(persist_dir=self.persist_dir)

            print(f"Задача успешно добавлена с ID: {node.node_id}")
            return node.node_id
        except Exception as e:
            print(f"Ошибка при добавлении задачи: {e}")
            return None

    def delete_task(self, task_id: str) -> None:
        """Удаление задачи по ID"""
        try:
            self.index.delete_ref_doc(
                ref_doc_id=task_id,
                delete_from_docstore=True
            )
            self.storage_context.persist(persist_dir=self.persist_dir)
            print(f"Задача с ID {task_id} успешно удалена")
        except Exception as e:
            print(f"Ошибка при удалении задачи: {e}")

    def get_task(self, query: str, k: int = 3) -> List[NodeWithScore]:
        """Получение задач по запросу"""
        try:
            # Используем простой retriever вместо query engine
            retriever = self.index.as_retriever(similarity_top_k=k)
            results = retriever.retrieve(query)
            print(f"Найдено {len(results)} результатов по запросу '{query}'")
            return results
        except Exception as e:
            print(f"Ошибка при поиске задач: {e}")
            return []


# Тестирование
if __name__ == "__main__":
    vector = QDrantVectorDatabase()
    task_id = vector.add_task('Ютуб крутой')

    results = vector.get_task('ютуб')

    if results:
        for node in results:
            print(f"Текст: {node.node.text}")
            print(f"Метаданные: {node.node.metadata}")
            print(f"Релевантность: {node.score}")
    else:
        print("Ничего не найдено")