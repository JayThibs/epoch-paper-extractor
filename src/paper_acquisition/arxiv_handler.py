import arxiv
from typing import Tuple, Optional

class ArxivHandler:
    def __init__(self):
        self.client = arxiv.Client()

    def get_paper_info(self, arxiv_id: str) -> Tuple[str, str, str, Optional[str]]:
        """
        Retrieve paper information from arXiv.
        
        Args:
            arxiv_id (str): The arXiv ID of the paper.
        
        Returns:
            Tuple[str, str, str, Optional[str]]: A tuple containing the paper title,
            PDF URL, LaTeX source URL, and abstract.
        """
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        
        title = paper.title
        pdf_url = paper.pdf_url
        latex_url = f"https://arxiv.org/e-print/{arxiv_id}"
        abstract = paper.summary
        
        return title, pdf_url, latex_url, abstract

    def validate_arxiv_id(self, arxiv_id: str) -> bool:
        """
        Validate if the given arXiv ID exists.
        
        Args:
            arxiv_id (str): The arXiv ID to validate.
        
        Returns:
            bool: True if the ID is valid, False otherwise.
        """
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            next(search.results())
            return True
        except StopIteration:
            return False

    def get_paper_abstract(self, arxiv_id: str) -> str:
        """
        Retrieve the abstract of a paper from arXiv.
        
        Args:
            arxiv_id (str): The arXiv ID of the paper.
        
        Returns:
            str: The abstract of the paper.
        """
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        return paper.summary