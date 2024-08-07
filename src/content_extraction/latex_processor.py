import os
from pylatexenc.latex2text import LatexNodes2Text

class LaTeXProcessor:
    def __init__(self, latex_dir):
        self.latex_dir = latex_dir

    def extract_content(self):
        main_file = self._find_main_tex_file()
        if not main_file:
            return None, []

        with open(os.path.join(self.latex_dir, main_file), 'r') as f:
            latex_content = f.read()

        text = LatexNodes2Text().latex_to_text(latex_content)
        images = self._extract_image_references(latex_content)
        return text, images

    def _find_main_tex_file(self):
        for file in os.listdir(self.latex_dir):
            if file.endswith('.tex'):
                with open(os.path.join(self.latex_dir, file), 'r') as f:
                    content = f.read()
                    if '\\begin{document}' in content:
                        return file
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