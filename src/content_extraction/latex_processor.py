import os
import chardet
from pylatexenc.latex2text import LatexNodes2Text

class LaTeXProcessor:
    def __init__(self, latex_dir):
        self.latex_dir = latex_dir

    def extract_content(self):
        main_file = self._find_main_tex_file()
        if not main_file:
            return None, []

        latex_content = self._read_file_with_encoding(os.path.join(self.latex_dir, main_file))
        if latex_content is None:
            return None, []

        text = LatexNodes2Text().latex_to_text(latex_content)
        images = self._extract_image_references(latex_content)
        return text, images

    def _find_main_tex_file(self):
        for file in os.listdir(self.latex_dir):
            if file.endswith('.tex'):
                content = self._read_file_with_encoding(os.path.join(self.latex_dir, file))
                if content and '\\begin{document}' in content:
                    return file
        return None

    def _read_file_with_encoding(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            detected = chardet.detect(raw_data)
            encoding = detected['encoding']
            
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return None

    def _extract_image_references(self, latex_content):
        image_commands = ['\\includegraphics', '\\figure']
        images = []
        for line in latex_content.split('\n'):
            for command in image_commands:
                if command in line:
                    image_file = line.split('{')[-1].split('}')[0]
                    images.append(os.path.join(self.latex_dir, image_file))
        return images