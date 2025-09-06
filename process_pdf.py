# Save this script as "process_pdf.py" in the same folder as your PDF.

import glob
import sys
import pyperclip
import fitz  # PyMuPDF
from PIL import Image
import io
import os

# --- User-Provided Function ---
# Ensure the file 'pdf_image_clipboard.py' is in the same directory.
try:
    from pdf_image_clipboard import copy_pdf_image_to_clipboard, PDFImageCopyError
except ImportError:
    print("ERROR: Could not find the required 'pdf_image_clipboard.py' file.")
    print("Please make sure it's in the same folder as this script.")
    sys.exit(1)
# -----------------------------


def find_single_pdf(prelatex_pdf_dir):
    """Finds a single PDF in the given 'prelatex-pdf' directory."""
    pdfs = glob.glob(os.path.join(prelatex_pdf_dir, "*.pdf"))
    if len(pdfs) == 0:
        print("❌ Error: No PDF file found in the 'prelatex-pdf' folder.")
        return None
    if len(pdfs) > 1:
        print("❌ Error: Multiple PDFs found in 'prelatex-pdf'. Please delete old PDFs so there is only one.")
        print("Found:", ", ".join(pdfs))
        return None
    return pdfs[0]

def display_page_and_get_input(pdf_path, page_num, prompt_text):
    """Displays a specific page of a PDF and gets user input."""
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_num)
        
        # Render page to a pixmap (an image)
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        
        # Show the image using the default system viewer
        image.show()
        
        print("\n" + "="*50)
        print(f"📄 Displaying Page {page_num + 1}")
        print("="*50)
        user_input = input(prompt_text + " ")
        doc.close()
        return user_input
        
    except Exception as e:
        print(f"�� Error displaying page {page_num + 1}: {e}")
        return None


def main():
    """Main function to run the PDF processing workflow."""
    # --- Clipboard check before script ---
    prior_clipboard = None
    try:
        prior_content = pyperclip.paste()
        if prior_content and prior_content.strip():
            # Truncate to 300 characters if needed
            short_clipboard = prior_content[:300]
            suffix = "..." if len(prior_content) > 300 else ""
            print(f'Saved clipboard from before script: "{short_clipboard}{suffix}"')
            prior_clipboard = prior_content
    except Exception as e:
        print(f"Warning: could not read clipboard at start: {e}")
        prior_clipboard = None

    # Always use path relative to the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prelatex_pdf_dir = os.path.join(script_dir, "prelatex-pdf")
    os.makedirs(prelatex_pdf_dir, exist_ok=True)
    pdf_path = find_single_pdf(prelatex_pdf_dir)
    if not pdf_path:
        sys.exit(1)

    print(f"✅ Found PDF: {pdf_path}")

    try:
        pdf_document = fitz.open(pdf_path)
        num_pages = len(pdf_document)
    except Exception as e:
        print(f"🚨 Error opening PDF file: {e}")
        sys.exit(1)

    # 1. Get general instructions
    general_instructions = display_page_and_get_input(
        pdf_path,
        0,
        "Are there any special instructions you have for the LLM regarding your PDF as a whole?\n(This first page is an example to remind you. Press Enter to skip):"
    )

    all_latex_outputs = []

    # 2. Loop through each page
    for i in range(num_pages):
        page_num = i + 1
        page_approved = False
        
        # This loop allows retrying a page if the transcription is bad
        while not page_approved:
            specific_instructions = display_page_and_get_input(
                pdf_path,
                i,
                f"Are there any special instructions for this specific image (Page {page_num})?\n(Press Enter to skip):"
            )
            
            # --- First LLM Interaction: Transcription ---
            try:
                copy_pdf_image_to_clipboard(i, pdf_path)
                print(f"\n📋 Image of Page {page_num} copied to clipboard.")
            except PDFImageCopyError as e:
                print(f"🚨 CRITICAL ERROR: Could not copy image to clipboard. {e}")
                sys.exit(1)

            input("   Hit Enter once you have pasted it into the LLM...")

            prompt_1 = (
                "Look over the math problem in this picture and more importantly the work to solve that problem. "
                "If you see any glaring issues, tell the user that and don’t do anything else. Just so they know there is a mistake. "
                "Otherwise, don’t tell the user anything and just output the entire problem and solution converted into LaTeX. "
                "It is imperative that you copy the text EXACTLY AS THE USER WROTE IT, "
                "inferring from context what they meant when necessary but never making big leaps or fixing anything more complicated than a misspelling of a word "
                "(anything worse should cause you to not output latex and instead tell the user what’s wrong)"
            )
            if general_instructions:
                prompt_1 += f"\n\nGeneral instructions from the user that may not apply to this image, but likely do:\n{general_instructions}"
            if specific_instructions:
                prompt_1 += f"\n\nSpecific instructions from the user about this particular image:\n{specific_instructions}"

            pyperclip.copy(prompt_1)
            print("\n📋 Prompt copied to clipboard.")
            input(
                "   Paste it into the LLM, wait for a response, then copy the FULL LaTeX response to your clipboard and hit Enter here..."
            )
            
            latex_output = pyperclip.paste()

            # --- Second LLM Interaction: Verification ---
            try:
                copy_pdf_image_to_clipboard(i, pdf_path)
                print(f"\n📋 Image of Page {page_num} copied to clipboard AGAIN for verification.")
            except PDFImageCopyError as e:
                print(f"🚨 CRITICAL ERROR: Could not copy image to clipboard. {e}")
                sys.exit(1)

            input("   Paste it into a new chat and press Enter...")

            prompt_2 = "are there any significant wording changes from the original image that I wrote and the latex text? I don’t want my original wording to be lost, but it’s fine if something very small like a typo was replaced"
            pyperclip.copy(prompt_2)
            print("\n📋 Verification prompt copied to clipboard.")
            print("   Paste this prompt into the LLM and review its answer.")
            
            user_approval = input(
                "   --> If there were NO significant deviations, just hit Enter.\n"
                "   --> If something went wrong, enter ANY character and then hit Enter to retry this page: "
            )

            if user_approval == "":
                print(f"✅ Page {page_num} approved!")
                all_latex_outputs.append(latex_output)
                page_approved = True
            else:
                print(f"🔄 Retrying Page {page_num}...")

    print("\n\n🎉 All pages have been processed! Now for the final combination step.")

    # 3. Final combination and verification loop
    final_combination_approved = False
    while not final_combination_approved:
        separator = "\n```\nnext page\n```\n"
        individual_outputs_str = separator.join(all_latex_outputs)

        final_prompt = (
            "I got all of these latex outputs from an LLM, can you combine them into one cohesive document, "
            "but without changing any of the actual text, just lumping them together so it will render on overleaf\n\n"
            "first page:\n```\n"
            f"{individual_outputs_str}"
            "\n```"
        )
        
        pyperclip.copy(final_prompt)
        print("\n📋 Final combination prompt copied to clipboard.")
        input("   Paste it into the LLM, copy the full response, and then press Enter...")

        final_latex = pyperclip.paste()
        
        # Final Verification
        verification_prompt = (
            "Were there any changes between the 'INDIVIDUAL' blocks and the 'COMBINED' document below?\n\n"
            '--- INDIVIDUAL ---\n"""\n'
            f'{final_prompt}\n"""\n\n'
            "--- COMBINED ---\n```\n"
            f"{final_latex}\n```"
        )
        pyperclip.copy(verification_prompt)
        print("\n📋 Final verification prompt copied to clipboard.")
        print("   Paste this into the LLM to double-check for unwanted changes.")
        
        final_user_approval = input(
            "   --> If the combined document is correct, just hit Enter.\n"
            "   --> If the LLM changed things, enter ANY character and then hit Enter to retry the combination: "
        )

        if final_user_approval == "":
            pyperclip.copy(final_latex)
            print("\n\n✨ Success! The final combined LaTeX has been copied to your clipboard.")
            final_combination_approved = True
        else:
            print("🔄 Retrying final combination step...")
            

    # --- Restore clipboard logic before exiting ---
    if prior_clipboard is not None:
        print()
        choice = input(
            "Once you are done with the full latex document, hit enter to retrieve your clipboard from before the script execution.\n"
            "If you wish to override your old clipboard with the latex text, enter 'override': "
        ).strip().lower()
        if choice == "override":
            print("Clipboard override chosen. Exiting latex saved to clipboard instead of prior clipboard.")
        else:
            pyperclip.copy(prior_clipboard)
            print("Restored your clipboard from before the script execution.")

    print("✅ Program finished.")

if __name__ == "__main__":
    main()
