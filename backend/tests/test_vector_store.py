import tempfile
import unittest
from pathlib import Path

from app.models.chunk import DocumentChunk
from app.models.embedding import EmbeddedChunk
from app.rag.vector_store import FAISSVectorStore


class FAISSVectorStoreTests(unittest.TestCase):
    def make_chunk(self, chunk_id: str, document_id: str, text: str) -> DocumentChunk:
        return DocumentChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            filename=f"{document_id}.txt",
            file_type="txt",
            text=text,
            page_number=None,
            chunk_index=0,
            metadata={},
        )

    def test_add_search_reload_and_delete(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            store = FAISSVectorStore(
                dimension=3,
                storage_dir=storage_dir,
            )

            chunks = [
                self.make_chunk("c1", "doc-1", "alpha"),
                self.make_chunk("c2", "doc-2", "beta"),
            ]
            embeddings = [
                EmbeddedChunk(chunk_id="c1", vector=[1.0, 0.0, 0.0]),
                EmbeddedChunk(chunk_id="c2", vector=[0.0, 1.0, 0.0]),
            ]

            store.add_chunks(chunks, embeddings)

            self.assertEqual(store.size, 2)
            self.assertTrue(store.is_persisted)
            self.assertEqual(store.document_count, 2)

            results = store.search([1.0, 0.0, 0.0], top_k=1)
            self.assertEqual(results[0][0].chunk_id, "c1")

            reloaded = FAISSVectorStore(
                dimension=3,
                storage_dir=storage_dir,
            )
            self.assertEqual(reloaded.size, 2)
            self.assertEqual(reloaded.document_count, 2)

            removed = reloaded.remove_document("doc-1")
            self.assertEqual(removed, 1)
            self.assertEqual(reloaded.size, 1)
            self.assertEqual(reloaded.document_count, 1)

            after_delete = FAISSVectorStore(
                dimension=3,
                storage_dir=storage_dir,
            )
            self.assertEqual(after_delete.size, 1)
            self.assertEqual(
                after_delete.list_documents()[0].document_id,
                "doc-2",
            )

    def test_rejects_mismatched_chunk_and_embedding_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FAISSVectorStore(
                dimension=3,
                storage_dir=Path(temp_dir),
            )

            chunk = self.make_chunk("chunk-a", "doc-a", "alpha")
            embedding = EmbeddedChunk(
                chunk_id="different-id",
                vector=[1.0, 0.0, 0.0],
            )

            with self.assertRaises(ValueError):
                store.add_chunks([chunk], [embedding])


if __name__ == "__main__":
    unittest.main()
