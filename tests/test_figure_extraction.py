import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from content_extraction.pdf_processor import PDFProcessor

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

def test_figure_extraction(pdf_path, output_folder):
    """
    Test figure extraction on a given PDF and save individual figures.
    """
    processor = PDFProcessor(pdf_path)
    text, images, figures = processor.extract_content()
    
    print(f"Extracted {len(figures)} figures from the PDF.")
    
    # Create a subfolder for images
    images_folder = os.path.join(output_folder, "images")
    os.makedirs(images_folder, exist_ok=True)
    
    for page_num, image in images:
        page_figures = [fig for fig in figures if fig['page'] == page_num]
        visualize_figures(image, page_figures, images_folder, page_num)
    
    # Save extracted text
    text_path = os.path.join(output_folder, "extracted_text.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved extracted text to {text_path}")
    
    # Save figure metadata
    import json
    metadata_path = os.path.join(output_folder, "figure_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(figures, f, indent=2)
    print(f"Saved figure metadata to {metadata_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_figure_extraction.py <path_to_pdf> <output_folder>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_folder = sys.argv[2]
    
    test_figure_extraction(pdf_path, output_folder)