# document_processing/pdf_extractor.py

import os
import re
import pymupdf
import pymupdf4llm
from langchain_core.documents import Document
import traceback

# --- Define Service Provider Name Variations (to exclude) ---
SERVICE_PROVIDER_NAMES_LOWER = [
    "newcold melbourne no.2 pty ltd",
    "newcold melbourne no 2 pty ltd",
    "newcold melbourne no.2 pty limited",
    "newcold melbourne no 2 pty limited",
    "newcold",
]

# --- Region mapping is no longer feasible without a known customer list ---

def clean_extracted_name(name):
    """Basic cleaning for extracted names."""
    print(f"    DEBUG [Clean]: Input to clean_extracted_name: '{name}'") # DEBUG
    if not name:
        print("    DEBUG [Clean]: Output (empty input): ''") # DEBUG
        return ""
    # Remove leading/trailing whitespace, commas, periods, and parentheses
    cleaned = name.strip(' ,.()')
    # Remove common legal suffixes if they are clearly separated by space or comma
    suffixes = [
        r',?\s+Pty\s+Ltd\.?$', r',?\s+Pty\s+Limited\.?$',
        r',?\s+Ltd\.?$', r',?\s+Limited\.?$', r',?\s+Inc\.?$'
    ]
    original_name = cleaned # Keep original for comparison
    cleaned_after_suffix = cleaned # Track change
    for suffix_pattern in suffixes:
        # Only remove if it looks like a distinct suffix
        if re.search(r'\b' + suffix_pattern.replace('$', ''), cleaned, flags=re.IGNORECASE):
             cleaned = re.sub(suffix_pattern, '', cleaned, flags=re.IGNORECASE).strip(' ,.')
    if cleaned != cleaned_after_suffix:
        print(f"    DEBUG [Clean]: After suffix removal: '{cleaned}'") # DEBUG

    # Attempt to remove ACN/ABN if preceded by common patterns or just trailing numbers
    cleaned_after_acn = cleaned # Track change
    cleaned = re.sub(r'(\s*,?\s*(ACN|ABN)\s*[:\s]?\s*[\d\s]+)$', '', cleaned, flags=re.IGNORECASE).strip(' ,.')
    cleaned = re.sub(r'(\s+\d{2}\s+\d{3}\s+\d{3}\s+\d{3})$', '', cleaned) # Basic ABN/ACN number pattern
    cleaned = re.sub(r'(\s+\d{9,11})$', '', cleaned) # Trailing 9-11 digits
    if cleaned != cleaned_after_acn:
        print(f"    DEBUG [Clean]: After ACN/ABN removal: '{cleaned}'") # DEBUG


    # Remove 'of [Address]' if it looks like an address start (basic)
    cleaned_after_of = cleaned # Track change
    cleaned = re.sub(r'\s+of\s+[\d/]+\s+[A-Z][a-z]+.*$', '', cleaned, flags=re.IGNORECASE).strip(' ,.')
    cleaned = re.sub(r'\s+of\s+[A-Z][a-z]+.*$', '', cleaned, flags=re.IGNORECASE).strip(' ,.') # Simpler 'of City'
    cleaned = re.sub(r'\s+whose\s+registered\s+office.*$', '', cleaned, flags=re.IGNORECASE).strip(' ,.')
    if cleaned != cleaned_after_of:
        print(f"    DEBUG [Clean]: After 'of Address/City' removal: '{cleaned}'") # DEBUG

    # Final whitespace cleanup
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # If cleaning removed too much, revert (simple heuristic)
    if len(cleaned) < 3 or (len(original_name) > 10 and len(cleaned) < len(original_name) / 2):
        print(f"    DEBUG [Clean]: Heuristic triggered. Cleaning reduced '{original_name}' to '{cleaned}'. Reverting.") # DEBUG
        cleaned = original_name.strip(' ,.') # Revert to original cleaned of initial whitespace/punctuation

    print(f"    DEBUG [Clean]: Output from clean_extracted_name: '{cleaned}'") # DEBUG
    return cleaned


def find_customer_automatically(text):
    """
    Attempts to automatically identify the customer name based on common
    agreement patterns, excluding known service provider names.
    Returns the best guess or 'Unknown Customer'.
    """
    print("  DEBUG [AutoDetect]: Starting automatic customer detection...") # DEBUG
    potential_matches = {}

    # --- Define Patterns with Priorities (Lower number = higher priority) ---
    patterns_priority_1 = [
        re.compile(r'^(.*?)(?:\s*,?\s*(?:ACN|ABN)[\s\d]*)?\s*\(the\s+["\']Customer["\']\)', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^Customer\s*:\s*(.*?)(?:\s*,?\s*(?:ACN|ABN|of\s|whose\sregistered\soffice)|$|\n)', re.IGNORECASE | re.MULTILINE),
    ]
    patterns_priority_2 = [
         re.compile(r'(?:Between.*?\(?(?:1|one)\)?|\(?(?:1|one)\)?)\s+(.+?)(?:\s*,?\s*(?:ACN|ABN|of\s|whose\sregistered\soffice)|\s*\(2\)|$|\n)', re.IGNORECASE | re.MULTILINE),
         re.compile(r'(?:Party\s+(?:1|one)|First\s+Party)\s*:\s*(.*?)(?:\s*,?\s*(?:ACN|ABN|of\s|whose\sregistered\soffice)|$|\n)', re.IGNORECASE | re.MULTILINE),
    ]
    patterns_priority_3 = [
        re.compile(r'(?:and\s*\(?(?:2|two)\)?|\(?(?:2|two)\))\s*(.*?)(?:\s*,?\s*(?:ACN|ABN|of\s|whose\sregistered\soffice)|$|\n)', re.IGNORECASE | re.MULTILINE),
        re.compile(r'(?:Party\s+(?:2|two)|Second\s+Party)\s*:\s*(.*?)(?:\s*,?\s*(?:ACN|ABN|of\s|whose\sregistered\soffice)|$|\n)', re.IGNORECASE | re.MULTILINE),
    ]

    all_patterns = {
        1: patterns_priority_1,
        2: patterns_priority_2,
        3: patterns_priority_3,
    }

    # --- Find all potential matches and store by priority ---
    for priority, patterns in all_patterns.items():
        print(f"  DEBUG [AutoDetect]: Checking Priority {priority} patterns...") # DEBUG
        for i, pattern in enumerate(patterns):
            print(f"    DEBUG [AutoDetect]: Trying Pattern {priority}.{i+1}: {pattern.pattern}") # DEBUG
            match_found_for_pattern = False
            for match in pattern.finditer(text):
                match_found_for_pattern = True
                potential_name_capture = match.group(1)
                print(f"      DEBUG [AutoDetect]: RAW CAPTURE (Pattern {priority}.{i+1}): '{potential_name_capture}'") # DEBUG
                if not potential_name_capture:
                    print("      DEBUG [AutoDetect]: -> Skipping (Empty Capture)") # DEBUG
                    continue

                cleaned_potential = clean_extracted_name(potential_name_capture)
                print(f"      DEBUG [AutoDetect]: CLEANED (Pattern {priority}.{i+1}): '{cleaned_potential}'") # DEBUG

                if not cleaned_potential or len(cleaned_potential) < 3:
                    print(f"      DEBUG [AutoDetect]: -> Skipping (Cleaned name too short or empty: '{cleaned_potential}')") # DEBUG
                    continue

                is_service_provider = False
                for sp_name in SERVICE_PROVIDER_NAMES_LOWER:
                    if sp_name in cleaned_potential.lower():
                        print(f"      DEBUG [AutoDetect]: -> Ignoring '{cleaned_potential}' (Resembles service provider '{sp_name}')") # DEBUG
                        is_service_provider = True
                        break
                if is_service_provider:
                    continue

                if priority not in potential_matches:
                    potential_matches[priority] = []
                if cleaned_potential not in potential_matches[priority]:
                     potential_matches[priority].append(cleaned_potential)
                     print(f"      DEBUG [AutoDetect]: -> Added Potential Match '{cleaned_potential}' (Priority {priority})") # DEBUG
                else:
                     print(f"      DEBUG [AutoDetect]: -> Skipping (Duplicate Potential Match '{cleaned_potential}')") # DEBUG
            # if not match_found_for_pattern:
            #     print(f"    DEBUG [AutoDetect]: No matches found for Pattern {priority}.{i+1}") # Optional: Can be noisy

    # --- Determine the best guess based on priority ---
    print(f"  DEBUG [AutoDetect]: Potential Matches Found (by priority): {potential_matches}") # DEBUG
    best_guess = "Unknown Customer"
    for priority in sorted(potential_matches.keys()):
        if potential_matches[priority]:
            if len(potential_matches[priority]) > 1:
                 print(f"  WARN [AutoDetect]: Multiple potential customer names found at priority {priority}: {potential_matches[priority]}. Selecting the first one: '{potential_matches[priority][0]}'") # DEBUG
            best_guess = potential_matches[priority][0]
            print(f"  DEBUG [AutoDetect]: Selected best guess '{best_guess}' from priority {priority}.") # DEBUG
            break

    if best_guess == "Unknown Customer":
         print("  DEBUG [AutoDetect]: Could not automatically determine a likely customer name from patterns.") # DEBUG

    print(f"  DEBUG [AutoDetect]: Returning final guess: '{best_guess}'") # DEBUG
    return best_guess


# --- extract_documents_from_pdf function ---
def extract_documents_from_pdf(pdf_path):
    """
    Extract documents using PyMuPDF4LLM for clean markdown text,
    and automatically attempts to detect the customer name from the first page.
    Region information is no longer automatically assigned.
    """
    file_name = os.path.basename(pdf_path)
    print(f"\n--- Processing PDF: {file_name} ---") # DEBUG
    customer_name = "Unknown Customer"
    region = "Unknown Region"
    documents = []
    pdf_doc = None
    pdf_metadata_from_pymupdf = {}

    try:
        # --- Step 1: Open with PyMuPDF ONLY for first page analysis ---
        try:
            print(f"DEBUG [Extractor]: Opening '{file_name}' with pymupdf for first page analysis...") # DEBUG
            pdf_doc = pymupdf.open(pdf_path)
            if len(pdf_doc) > 0:
                print(f"DEBUG [Extractor]: Reading text from first page (page 0) of '{file_name}'...") # DEBUG
                first_page_text = pdf_doc[0].get_text("text")
                # *** ADDED Debugging: Print the raw text being analyzed ***
                print(f"\n--- Analyzing First Page Text for: {file_name} ---") # DEBUG
                print(first_page_text) # DEBUG
                print("--- End First Page Text ---\n") # DEBUG
                customer_name = find_customer_automatically(first_page_text)
                region = "Unknown Region" # Region assignment removed
            else:
                print(f"WARN [Extractor]: PDF '{file_name}' has no pages.")
            pdf_metadata_from_pymupdf = pdf_doc.metadata if pdf_doc else {}
            print(f"DEBUG [Extractor]: PyMuPDF metadata extracted: {pdf_metadata_from_pymupdf}") # DEBUG
        except Exception as e:
            print(f"ERROR [Extractor]: Failed to open/read first page of {pdf_path} with pymupdf: {e}")
            customer_name = "Unknown Customer"
            region = "Unknown Region"
        finally:
            if pdf_doc:
                pdf_doc.close()
                pdf_doc = None

        print(f"DEBUG [Extractor]: Detected Customer after analysis: '{customer_name}', Region: '{region}' for '{file_name}'") # DEBUG

        # --- Step 2: Extract clean markdown ---
        print(f"DEBUG [Extractor]: Extracting markdown text using pymupdf4llm for '{file_name}' (forcing page chunks)...") # DEBUG
        # ***** CHANGE HERE: Force page chunks *****
        md_text_data = pymupdf4llm.to_markdown(pdf_path, page_chunks=True, write_images=False)
        # ******************************************
        print(f"DEBUG [Extractor]: Markdown extraction complete for '{file_name}'. Type: {type(md_text_data)}") # DEBUG


        # --- Step 3: Create LangChain Documents ---
        print(f"DEBUG [Extractor]: Creating LangChain documents for '{file_name}'...") # DEBUG
        # ***** ADJUSTED LOGIC: Handle list of dicts or list of strings *****
        if isinstance(md_text_data, list):
            print(f"DEBUG [Extractor]: Handling list output ({len(md_text_data)} items) from pymupdf4llm.") # DEBUG
            for page_num_zero_based, page_item in enumerate(md_text_data):
                page_num_one_based = page_num_zero_based + 1
                page_content_str = ""

                # --- Check if item is dict or string ---
                if isinstance(page_item, dict):
                    # Try common keys for text content
                    if 'text' in page_item and isinstance(page_item['text'], str):
                        page_content_str = page_item['text']
                    elif 'content' in page_item and isinstance(page_item['content'], str):
                        page_content_str = page_item['content']
                    else:
                        # Fallback: try converting the whole dict (might be messy)
                        print(f"  WARN [Extractor]: Page {page_num_one_based} item is dict, but no 'text' or 'content' key found. Using str(dict). Keys: {page_item.keys()}")
                        page_content_str = str(page_item)
                elif isinstance(page_item, str):
                    page_content_str = page_item
                else:
                    print(f"  ERROR [Extractor]: Page {page_num_one_based} item has unexpected type: {type(page_item)}. Skipping.")
                    continue
                # --- End Check ---

                metadata = {}
                metadata["source"] = file_name
                metadata["page_number"] = page_num_one_based # Correct page number
                metadata["customer"] = customer_name # Use detected name
                metadata["region"] = region # Use detected region
                pdf_meta_cleaned = {k: v for k, v in pdf_metadata_from_pymupdf.items() if v is not None and isinstance(v, (str, int, float, bool))}
                metadata.update(pdf_meta_cleaned)
                # print(f"  DEBUG [Extractor]: Metadata for page {page_num_one_based}: {metadata}") # Optional: Can be noisy
                try:
                    documents.append(Document(page_content=page_content_str, metadata=metadata))
                except Exception as doc_error:
                     print(f"  ERROR [Extractor]: Failed to create Document for page {page_num_one_based}. Error: {doc_error}")
                     print(f"  DEBUG [Extractor]: page_content type: {type(page_content_str)}, metadata: {metadata}")


        elif isinstance(md_text_data, str): # Fallback if page_chunks=True somehow failed
            print(f"WARN [Extractor]: pymupdf4llm returned a single string even with page_chunks=True. Handling as single doc.") # DEBUG
            metadata = {}
            metadata["source"] = file_name
            metadata["page_number"] = 1 # Assume page 1 if single string
            metadata["customer"] = customer_name # Use detected name
            metadata["region"] = region # Use detected region
            pdf_meta_cleaned = {k: v for k, v in pdf_metadata_from_pymupdf.items() if v is not None and isinstance(v, (str, int, float, bool))}
            metadata.update(pdf_meta_cleaned)
            print(f"  DEBUG [Extractor]: Metadata for single doc fallback: {metadata}") # DEBUG
            documents.append(Document(page_content=md_text_data, metadata=metadata))
        else:
             print(f"ERROR [Extractor]: Unexpected output format from pymupdf4llm for {file_name}: {type(md_text_data)}")
        # ******************************************************************

    except Exception as e:
        print(f"ERROR processing PDF {pdf_path}: {e}")
        traceback.print_exc()
        if pdf_doc:
            pdf_doc.close()
        return []

    print(f"DEBUG [Extractor]: Extracted {len(documents)} LangChain documents for '{file_name}'.") # DEBUG
    # Print metadata of the first document created for this PDF
    if documents:
        print(f"DEBUG [Extractor]: Metadata assigned to first document of '{file_name}': {documents[0].metadata}") # DEBUG
    else:
        print(f"WARN [Extractor]: No documents were created for '{file_name}'.") # DEBUG
    return documents

# --- Example Usage (__main__ block) ---
if __name__ == '__main__':
    # --- Use your actual PDF directory ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..')) # Go up one level
    pdf_directory = os.path.join(project_root, 'pdfs')
    print(f"Looking for PDFs in: {pdf_directory}")

    if not os.path.isdir(pdf_directory):
        print(f"ERROR: PDF directory not found: {pdf_directory}")
    else:
        pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith(".pdf")]
        if not pdf_files:
            print(f"No PDF files found in {pdf_directory}")
        else:
            print(f"Found PDFs: {pdf_files}")
            for pdf_file in pdf_files:
                pdf_path = os.path.join(pdf_directory, pdf_file)
                print(f"\n--- Processing {pdf_file} ---")
                extracted_docs = extract_documents_from_pdf(pdf_path)
                if extracted_docs:
                    print(f"Successfully extracted {len(extracted_docs)} documents for {pdf_file}.")
                    # print("First document metadata:", extracted_docs[0].metadata) # Already printed inside
                else:
                    print(f"Extraction failed or returned no documents for {pdf_file}.")