import streamlit as st
import os
import yaml
from dotenv import load_dotenv
from anthropic import Anthropic
from src.paper_acquisition.paper_downloader import PaperDownloader
from src.content_extraction.latex_processor import LaTeXProcessor
from src.content_extraction.pdf_processor import PDFProcessor
from src.content_extraction.image_processor import ImageProcessor
from src.information_extraction.text_analyzer import TextAnalyzer
from src.information_extraction.image_analyzer import ImageAnalyzer
from src.information_extraction.combined_analyzer import CombinedAnalyzer
from src.reasoning.calculator import ReasoningCalculator
import json

def load_questions():
    with open('config/questions.yaml', 'r') as file:
        return yaml.safe_load(file)

def load_paper_list():
    with open('config/paper_list.yaml', 'r') as file:
        return yaml.safe_load(file)['papers']

def process_paper(url, download_dir, openai_api_key, anthropic_api_key):
    st.write("Starting paper analysis...")
    
    # Download paper
    st.write("Downloading paper...")
    downloader = PaperDownloader(download_dir)
    pdf_path, latex_path, abstract, processed_dir, output_dir = downloader.download_paper(url)
    st.write(f"Paper downloaded: {pdf_path}")

    # Extract content
    if latex_path:
        st.write("Extracting content from LaTeX...")
        processor = LaTeXProcessor(latex_path)
        text, image_references = processor.extract_content()
        if text is None:  # If LaTeX processing fails, fall back to PDF
            st.write("LaTeX processing failed, falling back to PDF...")
            processor = PDFProcessor(pdf_path)
            text, images, figures = processor.extract_content()
            st.write(f"Extracted {len(images)} images and {len(figures)} figures from the PDF")
            image_paths = ImageProcessor.save_images(images, processed_dir)
            st.write(f"Saved {len(image_paths)} images")
        else:
            st.write("Extracted content from LaTeX successfully")
            image_paths = [(1, path) for path in image_references]  # Assume all images are on page 1 for LaTeX
            figures = []  # No figure extraction for LaTeX yet
    else:
        st.write("Extracting content from PDF...")
        processor = PDFProcessor(pdf_path)
        text, images, figures = processor.extract_content()
        st.write(f"Extracted {len(images)} images and {len(figures)} figures from the PDF")
        image_paths = ImageProcessor.save_images(images, processed_dir)
        st.write(f"Saved {len(image_paths)} images")

    # Save figures metadata
    with open(os.path.join(output_dir, 'figure_metadata.json'), 'w') as f:
        json.dump(figures, f, indent=2)

    # Prepend abstract to the text
    if abstract:
        text = f"Abstract:\n{abstract}\n\n{text}"

    # Load questions
    questions = load_questions()
    st.write(f"Loaded {len(questions)} questions for analysis")

    # Extract information
    st.write("Analyzing text and images...")
    text_analyzer = TextAnalyzer(anthropic_api_key)
    image_analyzer = ImageAnalyzer(openai_api_key)
    combined_analyzer = CombinedAnalyzer(text_analyzer, image_analyzer)
    
    text_summary, image_summary = combined_analyzer.analyze(text, image_paths)
    combined_responses = combined_analyzer.answer_questions(text_summary, image_summary, questions)

    # Reason and calculate
    st.write("Performing final reasoning and calculations...")
    calculator = ReasoningCalculator(anthropic_api_key)
    final_answers = calculator.reason_and_calculate(combined_responses, questions)

    # Save results to output directory
    with open(os.path.join(output_dir, 'results.json'), 'w') as f:
        json.dump(final_answers, f, indent=2)

    st.write("Analysis complete!")
    return final_answers, text, image_paths, pdf_path, combined_responses

def main():
    st.title("AI Paper Analyzer")

    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    download_dir = "data/raw"

    if not openai_api_key or not anthropic_api_key:
        st.error("Please set both OPENAI_API_KEY and ANTHROPIC_API_KEY in your .env file.")
        return

    papers = load_paper_list()
    paper_names = [paper['name'] for paper in papers]
    
    # Add selection mode
    selection_mode = st.radio("Select papers to analyze:", 
                              ["Single paper", "Multiple papers", "All papers"])
    
    if selection_mode == "Single paper":
        selected_papers = [st.selectbox("Select a paper to analyze", paper_names)]
    elif selection_mode == "Multiple papers":
        selected_papers = st.multiselect("Select papers to analyze", paper_names)
    else:  # All papers
        selected_papers = paper_names
    
    if st.button("Analyze Paper(s)"):
        for selected_paper in selected_papers:
            with st.spinner(f"Analyzing paper: {selected_paper}..."):
                selected_url = next(paper['url'] for paper in papers if paper['name'] == selected_paper)
                results, text, image_paths, pdf_path, combined_responses = process_paper(selected_url, download_dir, openai_api_key, anthropic_api_key)
                
                st.subheader(f"Analysis Results for {selected_paper}")
                for question, answer in results.items():
                    st.write(f"**{question}**")
                    st.write(answer)
                    
                    with st.expander("Show relevant text"):
                        st.write(combined_responses[question]['text_response'])
                    
                    with st.expander("Show relevant image analysis"):
                        st.write(combined_responses[question]['image_response'])
                    
                    st.write("---")

                with st.expander("Show Extracted Text"):
                    st.text_area("Paper Content", text, height=300)

                with st.expander("Show Extracted Images"):
                    for i, (page, path) in enumerate(image_paths):
                        st.image(path, caption=f"Image {i+1} (Page {page})")

                with st.expander("View PDF"):
                    st.write(f"[Open PDF]({pdf_path})")
                
                st.write("\n\n")  # Add some space between papers

if __name__ == "__main__":
    main()