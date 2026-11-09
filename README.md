# Resume Parser — Resume Data Extraction

## 1. Project Overview

The Resume Parser is a Python-based application that extracts structured information from resumes in PDF and image formats. It uses text extraction, Optical Character Recognition (OCR), and rule-based processing to identify important resume details.

The application provides a simple web interface built with Streamlit and displays the extracted information in organized tables.

## 2. Features

- Upload resumes in PDF, PNG, JPG, and JPEG formats.
- Extract text from text-based PDF documents.
- Use OCR to process scanned PDFs and image-based resumes.
- Extract personal information, education, work experience, skills, projects, and certifications.
- Display extracted information in separate sections.
- Export extracted information to CSV and JSON formats.

## 3. Technologies Used

- **Python:** Core programming language.
- **Streamlit:** Web application interface.
- **PyMuPDF:** PDF text extraction.
- **Tesseract OCR:** Optical character recognition.
- **pytesseract:** Python interface for Tesseract OCR.
- **Pillow:** Image processing.
- **Pandas:** Tabular data handling and CSV preparation.
- **Regular Expressions (Regex):** Pattern-based information extraction.
- **JSON:** Structured data representation.

## 4. Project Structure

Resume_Parser_final/
├── app.py
├── text_extractor.py
├── resume_extractor.py
├── requirements.txt
├── README.md
├── TESTING.md
├── LIMITATIONS.md
├── sample_output.csv
├── sample_output.json
└── sample_resumes/

## 5. Installation and Setup

### Prerequisites

- Python installed on the system.
- Tesseract OCR installed for OCR functionality.
- Visual Studio Code or another Python editor.

### Install Dependencies

Open the terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal to access the application.

## 6. How to Use

1. Launch the Streamlit application.
2. Upload a resume in a supported format.
3. Click the **Extract Information** button.
4. Review the extracted personal information, education, experience, skills, projects, and certifications.
5. Download the available CSV or JSON output.

## 7. Testing

The application has been tested using sample resumes with different layouts.

Testing focuses on:

- Text extraction from PDF resumes.
- OCR-based extraction from image-based documents.
- Handling resumes with different layouts.
- Displaying extracted information in organized sections.
- Verifying CSV and JSON output.

Detailed test cases and their actual results are documented separately in the project submission report.

## 8. Limitations

- Extraction accuracy may vary depending on resume layout and formatting.
- OCR may produce errors when processing blurry or low-quality images.
- Rule-based extraction may not identify every field correctly in unusual resume formats.
- Missing or ambiguous information may result in incomplete output.

## 9. Future Improvements

- Improve extraction across different resume layouts.
- Add more automated test cases.
- Improve error handling for invalid or unreadable files.
- Add confidence scores and manual correction of extracted fields.
- Improve recognition of tables, columns, and complex formatting.

## 10. Conclusion

The Resume Parser demonstrates how Python, text extraction, OCR, and rule-based processing can be combined to convert resume content into structured information through a simple web application.
