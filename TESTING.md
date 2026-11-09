# Resume Parser — Testing Report

## 1. Objective

To verify that the Resume Parser accepts supported resume formats, extracts information, displays the results, and generates downloadable output files.

## 2. Test Cases

| Test ID | Test Case                             | Expected Result                                                   | Actual Result               |
| ------- | ------------------------------------- | ----------------------------------------------------------------- | --------------------------- |
| TC01    | Upload a text-based PDF resume        | Text is extracted and organized into fields                       | Passed on the tested sample |
| TC02    | Extract personal information          | Available name, email, and phone details are displayed            | Passed on the tested sample |
| TC03    | Extract education details             | Education records are displayed in a table                        | Passed on the tested sample |
| TC04    | Extract work experience               | Available roles, durations, and descriptions are displayed        | Passed on the tested sample |
| TC05    | Extract skills and projects           | Detected skills and project information are displayed             | Passed on the tested sample |
| TC06    | Download JSON output                  | Extracted data is available in JSON format                        | Passed                      |
| TC07    | Download CSV output                   | Extracted data is available in CSV format                         | Passed                      |
| TC08    | Upload an image resume                | OCR extracts readable text from the image                         | Not tested yet              |
| TC09    | Upload a scanned PDF                  | OCR attempts to extract text from scanned pages                   | Not tested yet              |
| TC10    | Upload a resume with missing sections | Available information is displayed without inventing missing data | Not tested yet              |

## 3. Testing Summary

The application has been tested using a sample PDF resume. The main extraction workflow and the available JSON and CSV downloads were verified.

Further testing is required for image resumes, scanned PDFs, and documents with missing information before making broader claims about reliability.

## 4. Conclusion

The initial tests demonstrate that the Resume Parser can extract and display resume information from the tested sample and provide downloadable structured outputs. Additional test cases will help identify limitations and improve reliability.
