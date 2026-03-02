import os
from pypdf import PdfReader
from app.retrieval import add_document

DOCUMENT_FOLDER = "documents"

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text_pages = []

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text()

        if text:
            text_pages.append((page_number + 1, text))

    return text_pages


def load_all_pdf():
    for filename in os.listdir(DOCUMENT_FOLDER):
        if filename.endswith(".pdf"):
            file_path = os.path.join(DOCUMENT_FOLDER, filename)

            print(f"Loading {file_path}")

            pages = extract_text_from_pdf(file_path)

            for page_number, page_text in pages:
                add_document(
                    page_text, 
                    metadata={
                        "source": filename,
                        "page": page_number
                    }
                )
                
    print("All Pdf file readed")