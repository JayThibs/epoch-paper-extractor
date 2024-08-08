import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from content_extraction.pdf_processor import PDFProcessor

def download_pdf(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded PDF to {save_path}")
    else:
        raise Exception(f"Failed to download PDF. Status code: {response.status_code}")

def visualize_figures(image, figures, output_folder, page_num):
    """
    Extract and save individual figures from the image.
    """
    for i, figure in enumerate(figures):
        bbox = figure['bbox']
        
        # Extract the figure using the bounding box
        figure_image = image[bbox[1]:bbox[3], bbox[0]:bbox[2]]
        
        # Convert to PIL Image if using OpenCV
        if CV2_AVAILABLE:
            figure_image = Image.fromarray(cv2.cvtColor(figure_image, cv2.COLOR_BGR2RGB))
        else:
            figure_image = Image.fromarray(figure_image)
        
        # Save the extracted figure with page number in the filename
        output_path = os.path.join(output_folder, f"page_{page_num}_figure_{i+1}.png")
        figure_image.save(output_path)
        print(f"Saved figure {i+1} from page {page_num} to {output_path}")

def test_figure_extraction(arxiv_id, raw_data_folder, output_folder):
    """
    Test figure extraction on a given arXiv ID PDF and save individual figures.
    """
    # Create folders
    pdf_folder = os.path.join(raw_data_folder, arxiv_id)
    os.makedirs(pdf_folder, exist_ok=True)
    pdf_path = os.path.join(pdf_folder, f"{arxiv_id}.pdf")
    
    # Download PDF if it doesn't exist
    if not os.path.exists(pdf_path):
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        download_pdf(url, pdf_path)
    
    # Create output folders
    output_pdf_folder = os.path.join(output_folder, arxiv_id)
    images_folder = os.path.join(output_pdf_folder, "images")
    os.makedirs(images_folder, exist_ok=True)
    
    processor = PDFProcessor(pdf_path)
    text, images, figures = processor.extract_content()
    
    print(f"Extracted {len(figures)} figures from the PDF.")
    
    for page_num, image in images:
        page_figures = [fig for fig in figures if fig['page'] == page_num]
        visualize_figures(image, page_figures, images_folder, page_num)
    
    # Save extracted text
    text_path = os.path.join(output_pdf_folder, "extracted_text.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved extracted text to {text_path}")
    
    # Save figure metadata
    import json
    metadata_path = os.path.join(output_pdf_folder, "figure_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(figures, f, indent=2)
    print(f"Saved figure metadata to {metadata_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_figure_extraction.py <arxiv_id>")
        sys.exit(1)
    
    arxiv_id = sys.argv[1]
    raw_data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw'))
    output_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'output'))
    
    test_figure_extraction(arxiv_id, raw_data_folder, output_folder)