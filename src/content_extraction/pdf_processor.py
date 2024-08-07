import PyPDF2
from PIL import Image
import io

class PDFProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_content(self):
        text = ""
        images = []
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages, start=1):
                text += f"Page {page_num}:\n{page.extract_text()}\n\n"
                for image in page.images:
                    img = Image.open(io.BytesIO(image.data))
                    images.append((page_num, img))
        return text, images