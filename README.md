# Handwriting to LaTeX Converter

This project is a Python-based, semi-automated tool designed to streamline the conversion of handwritten mathematics homework from PDF files into LaTeX code. It cleverly utilizes Large Language Models (LLMs) to perform the conversion, but with a human-in-the-loop approach to ensure accuracy and maintain the user's original wording.

## How It Works

The script processes a PDF page by page, displaying each page to the user and then guiding them through a series of prompts to be used with an LLM. This workflow is designed to ensure that the final LaTeX output is both accurate and faithful to the original handwritten notes.

The process for each page is as follows:

1.  **Image Display**: The script displays an image of the current PDF page.
2.  **Instruction Input**: The user is prompted to provide any special instructions for the LLM, both general (for the entire document) and specific (for the current page).
3.  **Image to Clipboard**: The script copies the image of the page to the clipboard.
4.  **LLM Prompt Generation**: A detailed prompt is generated and copied to the clipboard for the user to paste into their preferred LLM. This prompt instructs the LLM to convert the handwritten math to LaTeX, with a strong emphasis on accuracy and preserving the original wording.
5.  **Verification Step**: After the initial conversion, a second prompt is generated to verify that the LLM's output doesn't significantly deviate from the user's original text.
6.  **Iterative Process**: This process is repeated for every page in the PDF, with the user guiding and verifying each step.
7.  **Final Combination**: Once all pages are processed, the script generates a final prompt to combine all the individual LaTeX outputs into a single, cohesive document.

## Features

*   **Interactive Workflow**: Guides the user through each step of the conversion process.
*   **Clipboard Automation**: Automatically copies images and prompts to the clipboard to streamline the interaction with LLMs.
*   **Robust Error Handling**: Includes checks for common issues, such as multiple PDFs in the input folder.
*   **Clipboard Preservation**: Saves and restores the user's clipboard content from before the script was run.
*   **Mac-Specific Functionality**: Utilizes AppleScript for clipboard operations, making it tailored for macOS environments.

## Getting Started

### Prerequisites

*   Python 3
*   An active virtual environment (recommended)
*   The required Python packages, which can be installed from `requirements.txt` (Note: A `requirements.txt` file is not currently present in the repository, but the necessary packages are `pyperclip`, `PyMuPDF`, `Pillow`, and `pdf2image`).

### Installation and Usage

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/convert-math-homework-to-latex.git
    cd convert-math-homework-to-latex
    ```
2.  **Set up the environment**:
    *   It is highly recommended to use a virtual environment to manage dependencies.
    *   Install the required packages:
        ```bash
        pip install pyperclip PyMuPDF Pillow pdf2image
        ```
3.  **Place your PDF**:
    *   Create a folder named `prelatex-pdf` in the root of the project directory.
    *   Place the single PDF file you want to convert into the `prelatex-pdf` folder.
4.  **Run the script**:
    *   The easiest way to run the script is by using the provided command file:
        ```bash
        ./handwriting2latex.command
        ```
    *   Alternatively, you can run the Python script directly from your terminal:
        ```bash
        python3 process_pdf.py
        ```

## Files in This Repository

*   `process_pdf.py`: The main script that orchestrates the entire PDF-to-LaTeX conversion process.
*   `pdf_image_clipboard.py`: A helper script that handles the functionality of copying images from a PDF to the clipboard on macOS.
*   `test_copying.py`: A utility script to test the image-copying functionality on your system.
*   `handwriting2latex.command`: A convenience script for macOS users to easily run the main `process_pdf.py` script.
*   `example.pdf`: An example PDF file for testing purposes.
*   `.gitignore`: A standard gitignore file to exclude unnecessary files from version control.
