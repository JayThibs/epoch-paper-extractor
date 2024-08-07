import os
from src.paper_acquisition.paper_downloader import PaperDownloader
from src.content_extraction.latex_processor import LaTeXProcessor
from src.content_extraction.pdf_processor import PDFProcessor
from src.content_extraction.image_processor import ImageProcessor
from src.information_extraction.text_analyzer import TextAnalyzer
from src.information_extraction.image_analyzer import ImageAnalyzer
from src.information_extraction.combined_analyzer import CombinedAnalyzer
from src.reasoning.calculator import ReasoningCalculator
from src.user_interface.validation_interface import ValidationInterface
from src.user_interface.results_viewer import ResultsViewer
import tkinter as tk
import yaml
from dotenv import load_dotenv

def load_questions():
    with open('config/questions.yaml', 'r') as file:
        return yaml.safe_load(file)

def process_paper(url, download_dir, openai_api_key):
    # Download paper
    downloader = PaperDownloader(download_dir)
    pdf_path, source_path = downloader.download_paper(url)

    # Extract content
    if source_path:
        processor = LaTeXProcessor(source_path)
        text, image_references = processor.extract_content()
        image_paths = [(1, path) for path in image_references]  # Assume all images are on page 1 for LaTeX
    else:
        processor = PDFProcessor(pdf_path)
        text, images = processor.extract_content()
        image_paths = ImageProcessor.save_images(images, download_dir)

    # Load questions
    questions = load_questions()

    # Extract information
    text_analyzer = TextAnalyzer()
    image_analyzer = ImageAnalyzer(openai_api_key)
    combined_analyzer = CombinedAnalyzer(text_analyzer, image_analyzer)
    
    text_summary, image_summary = combined_analyzer.analyze(text, image_paths)
    combined_responses = combined_analyzer.answer_questions(text_summary, image_summary, questions)

    # Reason and calculate
    calculator = ReasoningCalculator()
    final_answers = calculator.reason_and_calculate(combined_responses, questions)

    # Run validation interface
    root = tk.Tk()
    validation_app = ValidationInterface(root, final_answers, text, image_paths)
    root.mainloop()

    # After validation, show results viewer
    root = tk.Tk()
    results_app = ResultsViewer(root, final_answers, pdf_path)
    root.mainloop()

    return final_answers

if __name__ == "__main__":
    load_dotenv()
    url = "https://arxiv.org/abs/2307.09288"  # Llama 2 paper
    download_dir = "data/raw"
    openai_api_key = os.getenv("OPENAI_API_KEY")

    result = process_paper(url, download_dir, openai_api_key)
    print(result)