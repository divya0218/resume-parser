
import io
import json
import os
import tempfile

import fitz
import pandas as pd
import pytesseract
import streamlit as st
from PIL import Image

from text_extractor import extract_text_from_pdf
from resume_extractor import extract_resume_information


# --------------------------------------------------
# 1. Application configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Resume Parser",
    page_icon="📄",
    layout="wide"
)

# Tesseract OCR configuration for Windows
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

st.title("📄 Resume Parser")
st.write(
    "Upload a resume in PDF, PNG, JPG, or JPEG format "
    "to extract and organize important information."
)


# --------------------------------------------------
# 2. Extract text from images
# --------------------------------------------------

def extract_text_from_image(image_file):
    """Extract text from an image using OCR."""
    image = Image.open(image_file).convert("RGB")
    return pytesseract.image_to_string(image)


# --------------------------------------------------
# 3. Extract text from PDFs, including scanned PDFs
# --------------------------------------------------

def extract_text_from_uploaded_pdf(uploaded_file):
    """Extract selectable text first, then use OCR if needed."""
    pdf_bytes = uploaded_file.getvalue()

    # First, try normal PDF text extraction.
    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False
    ) as temp_file:
        temp_file.write(pdf_bytes)
        temp_path = temp_file.name

    try:
        extracted_text = extract_text_from_pdf(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    if extracted_text and extracted_text.strip():
        return extracted_text

    # If no selectable text exists, perform OCR on every page.
    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    ocr_pages = []

    try:
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image_bytes = pixmap.tobytes("png")

            image = Image.open(
                io.BytesIO(image_bytes)
            ).convert("RGB")

            page_text = pytesseract.image_to_string(image)
            ocr_pages.append(page_text)
    finally:
        document.close()

    return "\n".join(ocr_pages)


# --------------------------------------------------
# 4. Convert extracted information into CSV format
# --------------------------------------------------

def prepare_csv(information):
    """Convert nested resume data into one CSV row."""
    personal = information.get("personal_information", {})

    csv_data = {
        "full_name": [personal.get("full_name") or ""],
        "email": [personal.get("email") or ""],
        "phone": [personal.get("phone") or ""],
        "location": [personal.get("location") or ""],
        "linkedin": [personal.get("linkedin") or ""],
        "github": [personal.get("github") or ""],
    }

    for category in [
        "education",
        "experience",
        "skills",
        "projects",
        "certifications"
    ]:
        items = information.get(category, [])

        # Dictionaries are converted to JSON strings.
        formatted_items = [
            json.dumps(item, ensure_ascii=False)
            if isinstance(item, dict)
            else str(item)
            for item in items
        ]

        csv_data[category] = ["; ".join(formatted_items)]

    return pd.DataFrame(csv_data).to_csv(index=False).encode("utf-8-sig")


# --------------------------------------------------
# 5. Upload resume
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Choose a resume",
    type=["pdf", "png", "jpg", "jpeg"]
)


# --------------------------------------------------
# 6. Process resume
# --------------------------------------------------

if uploaded_file is not None:
    st.info(f"Selected file: {uploaded_file.name}")

    if st.button("Extract Information", type="primary"):

        try:
            file_name = uploaded_file.name.lower()

            with st.spinner("Reading and processing your resume..."):

                if file_name.endswith(".pdf"):
                    extracted_text = extract_text_from_uploaded_pdf(
                        uploaded_file
                    )

                elif file_name.endswith((".png", ".jpg", ".jpeg")):
                    extracted_text = extract_text_from_image(
                        uploaded_file
                    )

                else:
                    st.error("Unsupported file format.")
                    st.stop()

                if not extracted_text or not extracted_text.strip():
                    st.error(
                        "No readable text was found. "
                        "Please try a clearer resume."
                    )
                    st.stop()

                information = extract_resume_information(extracted_text)


            # 7. Display all extracted information in clean tables

            st.success("Resume processed successfully!")

            # Personal Information
            st.subheader("Personal Information")
            personal = information["personal_information"]

            personal_df = pd.DataFrame([
                {
                    "Field": key.replace("_", " ").title(),
                    "Information": value or "Not detected"
                }
                for key, value in personal.items()
            ])

            st.dataframe(
                personal_df,
                hide_index=True,
                use_container_width=True
            )

            # Education
            st.subheader("Education")
            if information["education"]:
                st.dataframe(
                    pd.DataFrame(information["education"]),
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No education information detected.")

            # Experience
            st.subheader("Experience")
            experience_rows = []

            for item in information["experience"]:
                if isinstance(item, dict):
                    experience_rows.append({
                        "Role and Company": item.get("role_and_company", ""),
                        "Duration": item.get("duration") or "Not detected",
                        "Description": "; ".join(item.get("description", []))
                    })
                else:
                    experience_rows.append({
                        "Role and Company": str(item),
                        "Duration": "Not detected",
                        "Description": ""
                    })

            if experience_rows:
                st.dataframe(
                    pd.DataFrame(experience_rows),
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No experience information detected.")

            # Skills
            st.subheader("Skills")
            if information["skills"]:
                st.dataframe(
                    pd.DataFrame({"Skill": information["skills"]}),
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No skills detected.")

            # Projects
            st.subheader("Projects")
            project_rows = []

            for item in information["projects"]:
                if isinstance(item, dict):
                    project_rows.append({
                        "Project": item.get("name_and_description", ""),
                        "Technologies": ", ".join(
                            item.get("technologies", [])
                        ),
                        "Description": "; ".join(
                            item.get("description", [])
                        )
                    })
                else:
                    project_rows.append({
                        "Project": str(item),
                        "Technologies": "",
                        "Description": ""
                    })

            if project_rows:
                st.dataframe(
                    pd.DataFrame(project_rows),
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No projects detected.")

            # Certifications
            st.subheader("Certifications")
            if information["certifications"]:
                st.dataframe(
                    pd.DataFrame({
                        "Certification": information["certifications"]
                    }),
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No certifications detected.")


            # ------------------------------------------
            # 8. Download JSON
            # ------------------------------------------

            json_data = json.dumps(
                information,
                indent=4,
                ensure_ascii=False
            )

            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="parsed_resume.json",
                mime="application/json",
                key="download_json"
            )

            # ------------------------------------------
            # 9. Download CSV
            # ------------------------------------------

            csv_file = prepare_csv(information)

            st.download_button(
                label="Download CSV",
                data=csv_file,
                file_name="parsed_resume.csv",
                mime="text/csv",
                key="download_csv"
            )

            # ------------------------------------------
            # 10. View original extracted text
            # ------------------------------------------

            with st.expander("View extracted raw text"):
                st.text(extracted_text)

        except Exception as error:
            st.error(f"Something went wrong: {error}")
        