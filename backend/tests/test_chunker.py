import unittest

from app.models.document import LoadedDocument
from app.services.chunker import DocumentChunker


class DocumentChunkerTests(unittest.TestCase):
    def setUp(self):
        self.chunker = DocumentChunker(
            chunk_size=80,
            chunk_overlap=10,
        )

    def test_empty_document_produces_no_chunks(self):
        document = LoadedDocument(
            document_id="doc-empty",
            filename="empty.txt",
            file_type="txt",
            content="   ",
            pages=[],
        )

        self.assertEqual(
            self.chunker.chunk_document(document),
            [],
        )

    def test_text_document_keeps_metadata(self):
        document = LoadedDocument(
            document_id="doc-1",
            filename="notes.md",
            file_type="md",
            content=(
                "Retrieval augmented generation uses relevant context.\n\n"
                "This second paragraph should remain associated with the same document."
            ),
            pages=[],
        )

        chunks = self.chunker.chunk_document(document)

        self.assertGreaterEqual(len(chunks), 1)
        self.assertTrue(all(chunk.document_id == "doc-1" for chunk in chunks))
        self.assertTrue(all(chunk.filename == "notes.md" for chunk in chunks))
        self.assertEqual(
            [chunk.chunk_index for chunk in chunks],
            list(range(len(chunks))),
        )


if __name__ == "__main__":
    unittest.main()
