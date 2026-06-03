from pypdf import PdfReader


def extract_pdf_text(file):

    try:

        reader = PdfReader(file)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception as e:

        print("PDF ERROR:", e)

        return ""