import os
import subprocess
import tempfile
from pdf2image import convert_from_path

class PDFImageCopyError(Exception):
    pass

def copy_pdf_image_to_clipboard(index: int, pdf_path: str) -> None:
    """
    Extracts the image at a given page index from a PDF and copies it to the macOS clipboard.
    Raises PDFImageCopyError for file not found, invalid index, or clipboard failures.
    """
    if not os.path.isfile(pdf_path):
        raise PDFImageCopyError(f"File '{pdf_path}' does not exist.")

    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        raise PDFImageCopyError(f"Could not convert PDF to images: {e}")

    if not images or index < 0 or index >= len(images):
        raise PDFImageCopyError(f"PDF '{pdf_path}' does not have page index {index}.")

    image = images[index]
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_file_path = temp_file.name
        image.save(temp_file_path, "PNG")

    try:
        # Use AppleScript to copy to macOS clipboard
        apple_script = f'''
        set the_image to (read (POSIX file "{temp_file_path}") as TIFF picture)
        set the clipboard to the_image
        '''
        subprocess.run(['osascript', '-e', apple_script], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise PDFImageCopyError(f"Failed to copy image to clipboard (macOS only): {e}")
    finally:
        os.remove(temp_file_path)