from pathlib import Path

from pypdf import PdfReader

from app.models.document import DocumentPage, LoadedDocument


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


class DocumentLoader:
    """Load supported document formats into a normalized representation."""

    def load(self, file_path: Path, document_id: str) -> LoadedDocument:
        extension = file_path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )

        if extension == ".pdf":
            return self._load_pdf(file_path, document_id)

        return self._load_text_file(file_path, document_id)

    def _load_pdf(
        self,
        file_path: Path,
        document_id: str,
    ) -> LoadedDocument:
        reader = PdfReader(str(file_path))

        pages: list[DocumentPage] = []

        for page_number, page in enumerate(reader.pages, start=1):
            content = page.extract_text() or ""

            pages.append(
                DocumentPage(
                    page_number=page_number,
                    content=content.strip(),
                )
            )

        full_content = "\n\n".join(
            page.content
            for page in pages
            if page.content
        )

        return LoadedDocument(
            document_id=document_id,
            filename=file_path.name,
            file_type="pdf",
            content=full_content,
            pages=pages,
        )

    def _load_text_file(
        self,
        file_path: Path,
        document_id: str,
    ) -> LoadedDocument:
        content = file_path.read_text(
            encoding="utf-8",
            errors="replace",
        ).strip()

        return LoadedDocument(
            document_id=document_id,
            filename=file_path.name,
            file_type=file_path.suffix.lower().lstrip("."),
            content=content,
            pages=[],
        )