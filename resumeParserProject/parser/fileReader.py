import fitz
import docx

def extractTextFromPdf(path):
    text = []
    with fitz.open(path) as doc:
        for page in doc:
            text.append(page.get_text())
    return "\n".join(text)

def extractTextFromDocx(path):
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def extractText(path):
    if path.lower().endswith('.pdf'):
        return extractTextFromPdf(path)
    elif path.lower().endswith('.docx'):
        return extractTextFromDocx(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")
