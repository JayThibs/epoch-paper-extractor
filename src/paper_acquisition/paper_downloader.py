import requests
import os
import tarfile
import gzip
import shutil
from urllib.parse import urlparse
from .arxiv_handler import ArxivHandler

class PaperDownloader:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.arxiv_handler = ArxivHandler()

    def download_paper(self, url):
        if 'arxiv.org' in url:
            return self._download_from_arxiv(url)
        else:
            return self._download_generic(url)

    def _download_from_arxiv(self, url):
        arxiv_id = url.split('/')[-1]
        
        if not self.arxiv_handler.validate_arxiv_id(arxiv_id):
            raise ValueError(f"Invalid arXiv ID: {arxiv_id}")
        
        title, pdf_url, latex_url, abstract = self.arxiv_handler.get_paper_info(arxiv_id)
        
        # Create folders for the paper
        raw_dir = os.path.join(self.base_dir, 'raw', arxiv_id)
        processed_dir = os.path.join(self.base_dir, 'processed', arxiv_id)
        output_dir = os.path.join(self.base_dir, 'output', arxiv_id)
        
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Download PDF
        pdf_path = os.path.join(raw_dir, f"{arxiv_id}.pdf")
        self._download_file(pdf_url, pdf_path)
        
        # Download and extract LaTeX source files
        latex_path = os.path.join(raw_dir, f"{arxiv_id}_latex")
        os.makedirs(latex_path, exist_ok=True)
        source_file = os.path.join(latex_path, f"{arxiv_id}_source")
        self._download_file(latex_url, source_file)
        
        # Check if it's a gzip file or a tar.gz file
        if self._is_gzip_file(source_file):
            self._extract_gzip(source_file, latex_path)
        elif self._is_tar_file(source_file):
            self._extract_tar(source_file, latex_path)
        else:
            print(f"Unknown source file format for {arxiv_id}")
        
        # Clean up the original source file
        os.remove(source_file)
        
        return pdf_path, latex_path, abstract, processed_dir, output_dir

    def _download_generic(self, url):
        response = requests.get(url)
        filename = os.path.basename(urlparse(url).path)
        file_path = os.path.join(self.download_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        return file_path, None, None

    def _download_file(self, url, path):
        response = requests.get(url)
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)

    def _is_gzip_file(self, file_path):
        with open(file_path, 'rb') as f:
            return f.read(2) == b'\x1f\x8b'

    def _is_tar_file(self, file_path):
        return tarfile.is_tarfile(file_path)

    def _extract_gzip(self, gzip_path, extract_path):
        with gzip.open(gzip_path, 'rb') as f_in:
            with open(os.path.join(extract_path, 'source.tex'), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _extract_tar(self, tar_path, extract_path):
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(path=extract_path)