"""
use this file to test if the image copying mechanism works on your computer
"""
from pdf_image_clipboard import copy_pdf_image_to_clipboard, PDFImageCopyError

if __name__ == "__main__":
    pdf_path = "example.pdf"
    page_index = 0  # Try copying the first page

    try:
        copy_pdf_image_to_clipboard(page_index, pdf_path)
        print("✅ Image successfully copied to clipboard with the correct format!")
    except PDFImageCopyError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")