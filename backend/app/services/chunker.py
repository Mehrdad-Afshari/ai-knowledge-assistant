import re
from uuid import uuid4

from app.models.chunk import DocumentChunk
from app.models.document import DocumentPage, LoadedDocument


class DocumentChunker:
    """Split documents into overlapping, semantically reasonable chunks."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        document: LoadedDocument,
    ) -> list[DocumentChunk]:
        if document.file_type == "pdf":
            return self._chunk_pdf(document)

        return self._chunk_text_document(document)

    def _chunk_pdf(
        self,
        document: LoadedDocument,
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []

        for page in document.pages:
            page_chunks = self._split_text(page.content)

            for text in page_chunks:
                chunks.append(
                    self._create_chunk(
                        document=document,
                        text=text,
                        page_number=page.page_number,
                    )
                )

        return self._reindex_chunks(chunks)

    def _chunk_text_document(
        self,
        document: LoadedDocument,
    ) -> list[DocumentChunk]:
        texts = self._split_text(document.content)

        chunks = [
            self._create_chunk(
                document=document,
                text=text,
                page_number=None,
            )
            for text in texts
        ]

        return self._reindex_chunks(chunks)

    def _split_text(self, text: str) -> list[str]:
        normalized_text = self._normalize_text(text)

        if not normalized_text:
            return []

        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(
                r"\n\s*\n",
                normalized_text,
            )
            if paragraph.strip()
        ]

        chunks: list[str] = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(paragraph) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""

                chunks.extend(
                    self._split_long_text(paragraph)
                )
                continue

            if not current_chunk:
                current_chunk = paragraph
                continue

            candidate = f"{current_chunk}\n\n{paragraph}"

            if len(candidate) <= self.chunk_size:
                current_chunk = candidate
            else:
                chunks.append(current_chunk)

                overlap = self._get_overlap(current_chunk)

                if overlap:
                    current_chunk = f"{overlap}\n\n{paragraph}"
                else:
                    current_chunk = paragraph

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _split_long_text(self, text: str) -> list[str]:
        chunks: list[str] = []

        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(
                start + self.chunk_size,
                text_length,
            )

            if end < text_length:
                boundary = text.rfind(" ", start, end)

                if boundary > start:
                    end = boundary

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            next_start = max(
                end - self.chunk_overlap,
                start + 1,
            )

            start = next_start

        return chunks

    def _get_overlap(self, text: str) -> str:
        if len(text) <= self.chunk_overlap:
            return text

        overlap = text[-self.chunk_overlap:]

        first_space = overlap.find(" ")

        if first_space != -1:
            overlap = overlap[first_space + 1:]

        return overlap.strip()

    def _normalize_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        lines = [
            re.sub(r"[ \t]+", " ", line).strip()
            for line in text.split("\n")
        ]

        return "\n".join(lines).strip()

    def _create_chunk(
        self,
        document: LoadedDocument,
        text: str,
        page_number: int | None,
    ) -> DocumentChunk:
        return DocumentChunk(
            chunk_id=str(uuid4()),
            document_id=document.document_id,
            filename=document.filename,
            file_type=document.file_type,
            text=text,
            page_number=page_number,
            chunk_index=0,
            metadata={
                "filename": document.filename,
                "file_type": document.file_type,
                "page_number": page_number,
            },
        )

    def _reindex_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:
        for index, chunk in enumerate(chunks):
            chunk.chunk_index = index

        return chunks