# AI Model Information Extractor

This project is designed to automatically extract and analyze information about AI models from academic papers. It processes both PDF and LaTeX sources, extracts text and images, and uses advanced natural language processing techniques to answer specific questions about the models described in the papers.

## Features

- Paper acquisition from sources like arXiv
- Content extraction from PDF and LaTeX files
- Text and image analysis using advanced AI models (Claude and GPT-4)
- Information extraction for various model fields (e.g., parameters, training compute, dataset size)
- Reasoning and calculation based on extracted information
- User interface for validation and results viewing

## Installation

1. Clone the repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Set up your environment variables:

Create a `.env` file in the root directory and add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the main script to process a paper:

```
python main.py
```

The script will download the paper, extract information, and present a user interface for validation and viewing results.

## Project Structure

- `src/`: Contains the main source code
  - `paper_acquisition/`: Handles downloading papers
  - `content_extraction/`: Processes PDF and LaTeX files
  - `information_extraction/`: Analyzes text and images
  - `reasoning/`: Performs calculations and reasoning on extracted data
  - `user_interface/`: Provides GUI for validation and results viewing
- `tests/`: Contains unit tests
- `data/`: Stores downloaded papers and extracted data
- `config/`: Contains configuration files, including `questions.yaml`

## Key Components

1. PaperDownloader: Downloads papers from sources like arXiv
2. PDFProcessor and LaTeXProcessor: Extract content from papers
3. TextAnalyzer and ImageAnalyzer: Analyze extracted content
4. PromptingSystem: Manages interactions with AI models for information extraction
5. ReasoningCalculator: Performs final calculations and reasoning
6. ValidationInterface and ResultsViewer: Provide user interfaces for interaction

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.