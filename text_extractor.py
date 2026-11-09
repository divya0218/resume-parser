
import fitz


def extract_text_from_pdf(file_path):
    """Extract text from a PDF resume."""
    try:
        document = fitz.open(file_path)
        extracted_text = ""

        for page in document:
            extracted_text += page.get_text() + "\n"

        document.close()
        return extracted_text.strip()

    except Exception as error:
        print(f"Error reading PDF: {error}")
        return ""
