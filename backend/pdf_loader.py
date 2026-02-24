from pypdf import PdfReader

def load_questions_from_pdf(pdf_path: str) -> list:
    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    # Keep only question lines
    questions = [
        line.strip().lower()
        for line in text.split("\n")
        if line.strip().endswith("?")
    ]

    return questions