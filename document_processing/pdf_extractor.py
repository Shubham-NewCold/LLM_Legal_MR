# document_processing/pdf_extractor.py

import os
import re
import pymupdf
import pymupdf4llm
from langchain_core.documents import Document
import traceback

# --- Service Provider Names (Keep as is) ---
SERVICE_PROVIDER_NAMES_LOWER = [
    "newcold melbourne no.2 pty ltd", "newcold melbourne no 2 pty ltd",
    "newcold melbourne no.2 pty limited", "newcold melbourne no 2 pty limited",
    "newcold melbourne pty ltd", "newcold burley, llc",
    "newcold burley operations, llc", "newcold pty ltd", "newcold", "nc",
]

# --- Clean Function (Keep previous version - it seemed okay) ---
def clean_extracted_name(name):
    """Improved cleaning for extracted names."""
    print(f"    DEBUG [Clean]: Input to clean_extracted_name: '{name}'") # DEBUG
    if not name:
        print("    DEBUG [Clean]: Output (empty input): ''") # DEBUG
        return ""

    # Initial strip
    cleaned = name.strip(' .,;:"()[]{}')

    # Remove '(trading as ...)'
    original_name_step1 = cleaned
    cleaned = re.sub(r'\s*\(trading as.*?\)\s*$', '', cleaned, flags=re.IGNORECASE).strip(' .,;:"()[]{}')
    if cleaned != original_name_step1:
        print(f"    DEBUG [Clean]: After '(trading as...)' removal: '{cleaned}'") # DEBUG

    # Remove trailing '(2) NewCold...'
    original_name_step2 = cleaned
    cleaned = re.sub(r'\s*\(?2\)?\s*NewCold.*$', '', cleaned, flags=re.IGNORECASE | re.DOTALL).strip(' .,;:"()[]{}')
    if cleaned != original_name_step2:
        print(f"    DEBUG [Clean]: After trailing '(2) NewCold...' removal: '{cleaned}'") # DEBUG

    # Remove leading (1), (2) etc.
    original_name_step3 = cleaned
    cleaned = re.sub(r'^\s*\(?\d\)?\s*', '', cleaned).strip(' .,;:"()[]{}')
    if cleaned != original_name_step3:
        print(f"    DEBUG [Clean]: After leading '(1)' removal: '{cleaned}'") # DEBUG

    # Store original name *after* these initial cleanups for heuristic check
    original_name_for_heuristic = cleaned

    # Remove common legal suffixes (more robustly)
    suffixes = [
        r'Pty\s+Ltd\.?', r'Pty\s+Limited\.?', r'Ltd\.?', r'Limited\.?',
        r'Inc\.?', r'LLC\.?', r'plc\.?'
    ]
    cleaned_after_suffix = cleaned
    for suffix in suffixes:
        pattern = r'\s+' + suffix + r'$'
        if re.search(pattern, cleaned, flags=re.IGNORECASE):
             cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE).strip(' .,;:"()[]{}')
    if cleaned != cleaned_after_suffix:
        print(f"    DEBUG [Clean]: After suffix removal: '{cleaned}'") # DEBUG

    # Attempt to remove ACN/ABN/Company Registration
    cleaned_after_acn = cleaned
    cleaned = re.sub(r'\s*\(?(ACN|ABN|Company registration)[\s\d:./-]+\)?$', '', cleaned, flags=re.IGNORECASE).strip(' .,;:"()[]{}')
    cleaned = re.sub(r'\s+\d{9,11}$', '', cleaned).strip(' .,;:"()[]{}')
    if cleaned != cleaned_after_acn:
        print(f"    DEBUG [Clean]: After ACN/ABN/Reg removal: '{cleaned}'") # DEBUG

    # Remove definitions like ("McCain") or ('Customer') or (Mondelez)
    cleaned_after_def = cleaned
    cleaned = re.sub(r'\s*\((?:["\'].*?["\']|[A-Za-z]+)\)$', '', cleaned).strip(' .,;:"()[]{}') # Handles ("X"), ('X'), (X)
    if cleaned != cleaned_after_def:
        print(f"    DEBUG [Clean]: After ('Shortname') removal: '{cleaned}'") # DEBUG

    # Remove location info
    cleaned_after_loc = cleaned
    cleaned = re.sub(r'\s*,\s*a\s+.*?corporation$', '', cleaned, flags=re.IGNORECASE).strip(' .,;:"()[]{}')
    cleaned = re.sub(r'\s*,\s*registered\s+in.*$', '', cleaned, flags=re.IGNORECASE).strip(' .,;:"()[]{}')
    cleaned = re.sub(r'\s+whose\s+registered\s+office.*$', '', cleaned, flags=re.IGNORECASE).strip(' .,;:"()[]{}')
    cleaned = re.sub(r'\s+of\s+[\d/]+\s+[A-Z][a-z]+.*$', '', cleaned, flags=re.IGNORECASE).strip(' .,.')
    cleaned = re.sub(r'\s+of\s+[A-Z][a-z]+.*$', '', cleaned, flags=re.IGNORECASE).strip(' .,.')
    if cleaned != cleaned_after_loc:
        print(f"    DEBUG [Clean]: After location/office removal: '{cleaned}'") # DEBUG

    # Final whitespace cleanup
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Heuristic check
    if len(cleaned) < 3 or (len(original_name_for_heuristic) > 10 and len(cleaned) < len(original_name_for_heuristic) / 3):
        print(f"    DEBUG [Clean]: Heuristic triggered. Cleaning reduced '{original_name_for_heuristic}' to '{cleaned}'. Reverting.") # DEBUG
        cleaned = original_name_for_heuristic.strip(' .,;:"()[]{}')

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

    # --- Define Patterns with Priorities ---

    # Priority 1: Explicit definitions or very clear structures
    patterns_priority_1 = [
        # Explicitly "(the 'Customer')" - Allied Pinnacle Style
        re.compile(r'^\s*\(?1\)?\s*(.*?)(?:\s*,\s*a\s+company.*?)?(?:\s*\(?(?:ACN|ABN|Company registration)[\s\d:./-]+\)?)?(?:\s*whose\s+registered\s+office.*?)?\s*\(the\s+["\']Customer["\']\)', re.IGNORECASE | re.MULTILINE | re.DOTALL),
        # Between: (1) Customer Name ... ; (2) Service Provider - Peters Style (Revised Capture)
        # Use [\s\S] to explicitly match any char including newline, non-greedily
        re.compile(r'Between:?\s*\(?1\)?\s*([\s\S]*?)\s*;\s*\(?2\)?\s*(?:NewCold[\w\s.]*|NC)', re.IGNORECASE | re.MULTILINE | re.DOTALL),
        # Structure: (1) Customer Name [single line] \n (2) Service Provider - Lactalis/Pinnacle/Simplot Style
        re.compile(r'^\s*\(?1\)?\s*(.*?)(?:\s*\(?(?:ACN|ABN|Company registration)[\s\d:./-]+\)?)?\s*$(?=\n\s*\(?2\)\s*NewCold)', re.IGNORECASE | re.MULTILINE),
    ]

    # Priority 2: Common agreement structures
    patterns_priority_2 = [
        # by and among Customer, ServiceProvider, [ServiceProvider] - McCain Style
        re.compile(r'by and among\s+(.*?)(?:\s*,\s*a\s+.*?corporation)?(?:\s*\(".*?"\))?\s*,?\s+(?:NewCold[\w\s.]*|NC)', re.IGNORECASE | re.MULTILINE | re.DOTALL),
        # General (1) Party Name structure (Improved boundary check)
        re.compile(r'^\s*\(?1\)?\s+([A-Z][\w\s.,&()-]+(?:Pty Ltd|Ltd|Inc|Pty Limited|Limited|USA, Inc\.?|LLC|plc))(?:\s*\(?(?:ACN|ABN|Company registration)[\s\d:./-]+\)?)?\s*?(?=\n\s*\(?2\)?|\s*;|$)', re.IGNORECASE | re.MULTILINE),
        # Party 1: Customer Name
        re.compile(r'(?:Party\s+(?:1|one)|First\s+Party)\s*:\s*(.*?)(?:\s*,?\s*(?:ACN|ABN|of\s|whose\sregistered\soffice)|$|\n)', re.IGNORECASE | re.MULTILINE),
    ]

    # Priority 3: Letter format patterns
    patterns_priority_3 = [
        # Customer Name ... has requested that NewCold - Mondelez Style (Removed ^ anchor)
        re.compile(r'([A-Z][\w\s.,&()-]+(?:Pty Ltd|Ltd|Inc|Pty Limited|Limited|USA, Inc\.?|LLC|plc))\s*(?:\(ACN\s+[\d\s]+\))?\s*(?:\(.*?\))?\s+has requested that\s+(?:NewCold[\w\s.]*|NC)', re.IGNORECASE | re.MULTILINE),
        # Signature block fallback - Mondelez Style (Removed ^ anchor, less strict ending)
        re.compile(r'([A-Z][\w\s.,&()-]+(?:Pty Ltd|Ltd|Inc|Pty Limited|Limited|USA, Inc\.?|LLC|plc))\s*\n+(?:Yours sincerely|Signature|Director)', re.IGNORECASE | re.MULTILINE),
    ]

    # Priority 4: Less reliable patterns (Keep as is)
    patterns_priority_4 = [
        re.compile(r'^\s*\(?2\)?\s+([A-Z][\w\s.,&()-]+(?:Pty Ltd|Ltd|Inc|Pty Limited|Limited|USA, Inc\.?|LLC|plc))(?:\s*\(?(?:ACN|ABN|Company registration)[\s\d:./-]+\)?)?\s*?(?=\n\s*\(?3\)?|\s*;|$)', re.IGNORECASE | re.MULTILINE),
        re.compile(r'(?:Party\s+(?:2|two)|Second\s+Party)\s*:\s*(.*?)(?:\s*,?\s*(?:ACN|ABN|of\s|whose\sregistered\soffice)|$|\n)', re.IGNORECASE | re.MULTILINE),
    ]

    # (Rest of the function remains the same - matching, cleaning, exclusion, selection)
    all_patterns = {
        1: patterns_priority_1,
        2: patterns_priority_2,
        3: patterns_priority_3,
        4: patterns_priority_4,
    }

    for priority, patterns in all_patterns.items():
        print(f"  DEBUG [AutoDetect]: Checking Priority {priority} patterns...") # DEBUG
        for i, pattern in enumerate(patterns):
            print(f"    DEBUG [AutoDetect]: Trying Pattern {priority}.{i+1}: {pattern.pattern}") # DEBUG
            match_found_for_pattern = False
            for match in pattern.finditer(text):
                match_found_for_pattern = True
                potential_name_capture = match.group(1) if match.groups() else match.group(0)
                print(f"      DEBUG [AutoDetect]: RAW CAPTURE (Pattern {priority}.{i+1}): '{potential_name_capture}'") # DEBUG
                if not potential_name_capture:
                    print("      DEBUG [AutoDetect]: -> Skipping (Empty Capture)") # DEBUG
                    continue

                cleaned_potential = clean_extracted_name(potential_name_capture)
                print(f"      DEBUG [AutoDetect]: CLEANED (Pattern {priority}.{i+1}): '{cleaned_potential}'") # DEBUG

                if not cleaned_potential or len(cleaned_potential) < 4:
                    print(f"      DEBUG [AutoDetect]: -> Skipping (Cleaned name too short or empty: '{cleaned_potential}')") # DEBUG
                    continue

                is_service_provider = False
                cleaned_lower = cleaned_potential.lower()
                for sp_name in SERVICE_PROVIDER_NAMES_LOWER:
                    if cleaned_lower == sp_name or re.fullmatch(re.escape(sp_name) + r'[\s,.]*', cleaned_lower):
                        print(f"      DEBUG [AutoDetect]: -> Ignoring '{cleaned_potential}' (Matches service provider '{sp_name}')") # DEBUG
                        is_service_provider = True
                        break
                    if re.search(r'\bnewcold\b', cleaned_lower) or (cleaned_lower == 'nc'):
                         is_likely_sp_variation = False
                         for known_sp in SERVICE_PROVIDER_NAMES_LOWER:
                             if known_sp in cleaned_lower:
                                 is_likely_sp_variation = True
                                 break
                         if is_likely_sp_variation:
                             print(f"      DEBUG [AutoDetect]: -> Ignoring '{cleaned_potential}' (Contains service provider base name and resembles known SP variation)") # DEBUG
                             is_service_provider = True
                             break

                if is_service_provider:
                    continue

                if priority not in potential_matches:
                    potential_matches[priority] = set()
                potential_matches[priority].add(cleaned_potential)
                print(f"      DEBUG [AutoDetect]: -> Added Potential Match '{cleaned_potential}' (Priority {priority})") # DEBUG

    # --- Determine the best guess based on priority ---
    print(f"  DEBUG [AutoDetect]: Potential Matches Found (by priority): {potential_matches}") # DEBUG
    best_guess = "Unknown Customer"
    for priority in sorted(potential_matches.keys()):
        if potential_matches[priority]:
            valid_matches = list(potential_matches[priority])
            if len(valid_matches) > 1:
                 valid_matches.sort(key=len, reverse=True)
                 print(f"  WARN [AutoDetect]: Multiple potential customer names found at priority {priority}: {valid_matches}. Selecting the longest one: '{valid_matches[0]}'") # DEBUG
            best_guess = valid_matches[0]
            print(f"  DEBUG [AutoDetect]: Selected best guess '{best_guess}' from priority {priority}.") # DEBUG
            break

    if best_guess == "Unknown Customer":
         print("  DEBUG [AutoDetect]: Could not automatically determine a likely customer name from patterns.") # DEBUG

    print(f"  DEBUG [AutoDetect]: Returning final guess: '{best_guess}'") # DEBUG
    return best_guess


# --- extract_documents_from_pdf function (No changes needed here) ---
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
                print(first_page_text[:2000]) # Print first 2000 chars for brevity
                print("--- End First Page Text Snippet ---\n") # DEBUG
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
        md_text_data = pymupdf4llm.to_markdown(pdf_path, page_chunks=True, write_images=False)
        print(f"DEBUG [Extractor]: Markdown extraction complete for '{file_name}'. Type: {type(md_text_data)}") # DEBUG


        # --- Step 3: Create LangChain Documents ---
        print(f"DEBUG [Extractor]: Creating LangChain documents for '{file_name}'...") # DEBUG
        if isinstance(md_text_data, list):
            print(f"DEBUG [Extractor]: Handling list output ({len(md_text_data)} items) from pymupdf4llm.") # DEBUG
            for page_num_zero_based, page_item in enumerate(md_text_data):
                page_num_one_based = page_num_zero_based + 1
                page_content_str = ""

                if isinstance(page_item, dict):
                    if 'text' in page_item and isinstance(page_item['text'], str):
                        page_content_str = page_item['text']
                    elif 'content' in page_item and isinstance(page_item['content'], str):
                        page_content_str = page_item['content']
                    else:
                        print(f"  WARN [Extractor]: Page {page_num_one_based} item is dict, but no 'text' or 'content' key found. Using str(dict). Keys: {page_item.keys()}")
                        page_content_str = str(page_item)
                elif isinstance(page_item, str):
                    page_content_str = page_item
                else:
                    print(f"  ERROR [Extractor]: Page {page_num_one_based} item has unexpected type: {type(page_item)}. Skipping.")
                    continue

                metadata = {}
                metadata["source"] = file_name
                metadata["page_number"] = page_num_one_based
                metadata["customer"] = customer_name
                metadata["region"] = region
                pdf_meta_cleaned = {k: v for k, v in pdf_metadata_from_pymupdf.items() if v is not None and isinstance(v, (str, int, float, bool))}
                metadata.update(pdf_meta_cleaned)
                try:
                    documents.append(Document(page_content=page_content_str, metadata=metadata))
                except Exception as doc_error:
                     print(f"  ERROR [Extractor]: Failed to create Document for page {page_num_one_based}. Error: {doc_error}")
                     print(f"  DEBUG [Extractor]: page_content type: {type(page_content_str)}, metadata: {metadata}")


        elif isinstance(md_text_data, str):
            print(f"WARN [Extractor]: pymupdf4llm returned a single string even with page_chunks=True. Handling as single doc.") # DEBUG
            metadata = {}
            metadata["source"] = file_name
            metadata["page_number"] = 1
            metadata["customer"] = customer_name
            metadata["region"] = region
            pdf_meta_cleaned = {k: v for k, v in pdf_metadata_from_pymupdf.items() if v is not None and isinstance(v, (str, int, float, bool))}
            metadata.update(pdf_meta_cleaned)
            print(f"  DEBUG [Extractor]: Metadata for single doc fallback: {metadata}") # DEBUG
            documents.append(Document(page_content=md_text_data, metadata=metadata))
        else:
             print(f"ERROR [Extractor]: Unexpected output format from pymupdf4llm for {file_name}: {type(md_text_data)}")

    except Exception as e:
        print(f"ERROR processing PDF {pdf_path}: {e}")
        traceback.print_exc()
        if pdf_doc:
            pdf_doc.close()
        return []

    print(f"DEBUG [Extractor]: Extracted {len(documents)} LangChain documents for '{file_name}'.") # DEBUG
    if documents:
        print(f"DEBUG [Extractor]: Metadata assigned to first document of '{file_name}': {documents[0].metadata}") # DEBUG
    else:
        print(f"WARN [Extractor]: No documents were created for '{file_name}'.") # DEBUG
    return documents


# --- Example Usage (__main__ block remains the same) ---
if __name__ == '__main__':
    # --- Use your actual PDF directory ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '.')) # Assume script is in project root or adjust as needed
    pdf_directory = os.path.join(project_root, 'pdfs_to_test') # Create a 'pdfs_to_test' subdirectory
    print(f"Looking for PDFs in: {pdf_directory}")

    # Create dummy directory if it doesn't exist for testing
    if not os.path.exists(pdf_directory):
        os.makedirs(pdf_directory)
        print(f"Created directory: {pdf_directory}")
        # You would place your test PDFs here

    if not os.path.isdir(pdf_directory):
        print(f"ERROR: PDF directory not found or is not a directory: {pdf_directory}")
    else:
        pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith(".pdf")]
        if not pdf_files:
            print(f"No PDF files found in {pdf_directory}")
        else:
            print(f"Found PDFs: {pdf_files}")
            all_extracted_docs = []
            for pdf_file in pdf_files:
                pdf_path = os.path.join(pdf_directory, pdf_file)
                print(f"\n--- Processing {pdf_file} ---")
                extracted_docs = extract_documents_from_pdf(pdf_path)
                if extracted_docs:
                    print(f"Successfully extracted {len(extracted_docs)} documents for {pdf_file}.")
                    all_extracted_docs.extend(extracted_docs)
                else:
                    print(f"Extraction failed or returned no documents for {pdf_file}.")

            print(f"\n--- Extraction Summary ---")
            customer_counts = {}
            for doc in all_extracted_docs:
                cust = doc.metadata.get("customer", "Unknown Customer")
                customer_counts[cust] = customer_counts.get(cust, 0) + 1
            print("Customer names extracted and document counts:")
            for cust, count in customer_counts.items():
                print(f"- {cust}: {count} documents")
            print(f"Total documents extracted: {len(all_extracted_docs)}")