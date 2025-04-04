# langchain_utils/qa_chain.py

import os
import sys
import uuid
from typing import Any, Dict, List, Optional, Sequence, Union
import traceback

# --- LangChain Imports ---
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.mapreduce import MapReduceDocumentsChain
from langchain_openai import AzureChatOpenAI
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain.globals import set_debug

# --- Local Imports ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION,
                    AZURE_OPENAI_DEPLOYMENT_NAME, AZURE_OPENAI_API_KEY,
                    TEMPERATURE, MAX_TOKENS, PDF_DIR, MAX_TOKENS_THRESHOLD,
                    PROJECT_NAME, PERSIST_DIRECTORY)
from langchain_utils.vectorstore import initialize_faiss_vectorstore, embeddings
from document_processing.pdf_extractor import extract_documents_from_pdf
from document_processing.parser import pyparse_hierarchical_chunk_text

try:
    # Use the detailed system prompt suitable for MapReduce's Reduce step
    from system_prompt import system_prompt
    print("--- Successfully imported system_prompt from system_prompt.py ---")
except ImportError:
    print("--- WARNING: Could not import system_prompt. Using a basic default for Reduce step. ---")
    system_prompt = "You are a helpful AI assistant. Synthesize the provided summaries to answer the question."


# --- Global Variables ---
map_reduce_chain: Optional[MapReduceDocumentsChain] = None
vectorstore = None
retriever = None
llm_instance = None
detected_customer_names: List[str] = []
CUSTOMER_LIST_FILE = "detected_customers.txt"

# --- MapReduce Chain Setup ---
def setup_map_reduce_chain() -> MapReduceDocumentsChain:
    global llm_instance
    llm_instance = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
        openai_api_key=AZURE_OPENAI_API_KEY,
        temperature=TEMPERATURE,
        model_name=AZURE_OPENAI_DEPLOYMENT_NAME,
        max_tokens=MAX_TOKENS,
    )


    llm = llm_instance

    # --- Map Prompt ---
    # Acknowledges prepended metadata and focuses on topic extraction
    map_template = """
You will be provided with a document excerpt preceded by its source metadata (Source, Page, Customer, Clause).
Your task is to analyze ONLY the text of the document excerpt BELOW the '---' line.
Based *only* on this excerpt text, identify and extract the exact sentences or key points that are relevant to answering the user's question.

User Question: {question}

Document Excerpt with Metadata:
{page_content}

**Instructions:**
1.  Focus *only* on the text provided in the excerpt *below* the '---' line.
2.  Extract verbatim sentences or concise key points from the excerpt text that help answer the User Question.
3.  **Pay special attention to extracting specific details mentioned in the question (like temperatures, dates, durations, monetary amounts, specific obligations) if they appear in the excerpt, even if the surrounding sentence doesn't explicitly name the entity from the question (use the overall context of the chunk).**
4.  **Your entire output MUST start with the *exact* metadata line provided above (everything before the '---'), followed by ' --- ', and then either your extracted text OR the specific phrase "No relevant information found in this excerpt."**
5.  If the excerpt text contains NO information relevant to the User Question, your output MUST be the metadata line followed by ' --- No relevant information found in this excerpt.'.
6.  Do NOT add explanations, introductions, summaries, or any text other than the required metadata prefix and the extracted relevant text (or the "No relevant information" message).
7.  Do NOT attempt to answer the overall User Question.

**Output:**
"""
    map_prompt = PromptTemplate(
        input_variables=["page_content", "question"],
        template=map_template
    )
    map_chain = LLMChain(llm=llm, prompt=map_prompt, verbose=True)

    # --- Reduce Prompt ---
    # Uses the detailed system_prompt for synthesis from summaries
    reduce_template = f"""
{system_prompt} # <-- Embed the detailed system prompt for synthesis

Original User Question: {{question}}

Extracted Information Summaries (Metadata --- Content):
{{doc_summaries}}

Based *only* on the summaries above and following all instructions in the initial system prompt, provide the final answer to the Original User Question.

Final Answer:"""
    reduce_prompt = PromptTemplate(
        input_variables=["doc_summaries", "question"],
        template=reduce_template
        )
    reduce_llm_chain = LLMChain(llm=llm, prompt=reduce_prompt, verbose=True)

    # Use StuffDocumentsChain for the final combination of summaries
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_llm_chain,
        document_variable_name="doc_summaries",
        document_separator="\n\n---\n\n",
        verbose=True
    )

    # --- Create the MapReduceDocumentsChain ---
    chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=combine_documents_chain,
        document_variable_name="page_content",
        input_key="input_documents",
        output_key="output_text",
        verbose=True
    )
    return chain


# --- Document Loading and Parsing (Includes metadata handling) ---
# (Keep print_chunk_details and load_all_documents exactly as they were)
def print_chunk_details(chunk, index):
    """Prints key details of a document chunk for debugging."""
    metadata = chunk.metadata
    print(f"\n--- Debug Chunk Details (Overall Index: {index}) ---")
    print(f"  Source: {metadata.get('source', 'N/A')}")
    print(f"  Page:   {metadata.get('page_number', 'N/A')}")
    print(f"  Customer: {metadata.get('customer', 'N/A')}")
    print(f"  Region: {metadata.get('region', 'N/A')}")
    print(f"  Hierarchy: {metadata.get('hierarchy', [])}")
    print(f"  Clause: {metadata.get('clause', 'N/A')}")
    print(f"  Title:  {metadata.get('clause_title', 'N/A')}")
    content_snippet = chunk.page_content[:150].replace("\n", " ").replace("\r", "")
    print(f"  Content Snippet: {content_snippet}...")
    print("-" * 50)

def load_all_documents(pdf_directory):
    """Loads PDFs, extracts using automatic detection, parses, maintains state."""
    all_final_documents = []
    overall_chunk_index = 0

    if not os.path.isdir(pdf_directory):
        print(f"ERROR: PDF directory not found: {pdf_directory}")
        return []

    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith(".pdf")]
    print(f"Found {len(pdf_files)} PDF files in {pdf_directory}")

    for file in pdf_files:
        file_path = os.path.join(pdf_directory, file)
        print(f"Processing {file_path}...")
        try:
            page_documents = extract_documents_from_pdf(file_path)
            if not page_documents:
                 print(f"WARN: No documents extracted from {file_path}. Skipping.")
                 continue
        except Exception as e:
            print(f"ERROR: Failed to extract pages from {file_path}: {e}")
            traceback.print_exc()
            continue

        current_hierarchy_stack = []

        for doc_obj in page_documents:
            page_content = doc_obj.page_content
            page_metadata = doc_obj.metadata
            source_file = page_metadata.get('source', file)
            page_number = page_metadata.get('page_number', 'N/A')
            customer_name = page_metadata.get('customer', 'Unknown Customer')
            region_name = page_metadata.get('region', 'Unknown Region')
            word_count = len(page_content.split())

            parser_metadata = {
                'source': source_file, 'page_number': page_number,
                'customer': customer_name, 'region': region_name,
                'clause': 'N/A', 'hierarchy': []
            }
            parser_metadata.update({k: v for k, v in page_metadata.items() if k not in parser_metadata})

            if word_count > MAX_TOKENS_THRESHOLD:
                try:
                    parsed_page_docs, current_hierarchy_stack = pyparse_hierarchical_chunk_text(
                        full_text=page_content, source_name=source_file,
                        page_number=page_number, extra_metadata=parser_metadata,
                        initial_stack=current_hierarchy_stack
                    )
                    for parsed_doc in parsed_page_docs:
                        all_final_documents.append(parsed_doc)
                        overall_chunk_index += 1
                except Exception as e:
                    print(f"ERROR: Failed to parse page {page_number} of {file}: {e}")
                    traceback.print_exc()
                    print(f"  WARNING: Adding page {page_number} as whole chunk due to parsing error.")
                    doc_obj.metadata.update(parser_metadata)
                    doc_obj.metadata['hierarchy'] = [item[0] for item in current_hierarchy_stack] if current_hierarchy_stack else []
                    doc_obj.metadata['clause'] = current_hierarchy_stack[-1][0] if current_hierarchy_stack else 'N/A'
                    all_final_documents.append(doc_obj)
                    overall_chunk_index += 1
            else:
                doc_obj.metadata.update(parser_metadata)
                doc_obj.metadata['hierarchy'] = [item[0] for item in current_hierarchy_stack] if current_hierarchy_stack else []
                doc_obj.metadata['clause'] = current_hierarchy_stack[-1][0] if current_hierarchy_stack else 'N/A'
                all_final_documents.append(doc_obj)
                overall_chunk_index += 1

    print(f"Total documents processed into chunks: {len(all_final_documents)}")
    return all_final_documents


# --- Application Initialization ---
def initialize_app(top_k_vectors=15):
    """Initializes vectorstore, retriever, chain, and detected customer names."""
    global vectorstore, retriever, map_reduce_chain, detected_customer_names
    set_debug(True) # Keep debug mode on

    # --- Vectorstore Loading/Building (remains the same) ---
    documents_for_analysis = []
    if os.path.exists(PERSIST_DIRECTORY):
        print("Loading precomputed FAISS vectorstore...")
        try:
            vectorstore = initialize_faiss_vectorstore([], persist_directory=PERSIST_DIRECTORY)
            print("FAISS vectorstore loaded successfully.")
            try:
                with open(CUSTOMER_LIST_FILE, "r") as f:
                    detected_customer_names = sorted([line.strip() for line in f if line.strip() and line.strip() != "Unknown Customer"])
                print(f"Loaded detected customer names from file: {detected_customer_names}")
            except FileNotFoundError:
                print(f"WARN: {CUSTOMER_LIST_FILE} not found. Customer name list will be empty until index rebuild.")
                detected_customer_names = []
            except Exception as e:
                print(f"Error loading {CUSTOMER_LIST_FILE}: {e}")
                detected_customer_names = []
        except Exception as e:
            print(f"ERROR loading FAISS index: {e}. Will attempt to rebuild.")
            vectorstore = None

    if vectorstore is None:
        print("Precomputed vectorstore not found or failed to load; building from scratch...")
        documents_for_analysis = load_all_documents(PDF_DIR)
        if not documents_for_analysis:
             print("ERROR: No documents were loaded or processed. Check PDF_DIR and PDF files.")
             sys.exit(1)
        print(f"Building FAISS index from {len(documents_for_analysis)} processed chunks...")
        try:
            vectorstore = initialize_faiss_vectorstore(documents_for_analysis, persist_directory=PERSIST_DIRECTORY)
            print("FAISS index built and saved successfully.")
            all_names = set(doc.metadata.get('customer', 'Unknown Customer') for doc in documents_for_analysis)
            detected_customer_names = sorted([name for name in all_names if name != "Unknown Customer"])
            print(f"Dynamically detected customer names: {detected_customer_names}")
            try:
                with open(CUSTOMER_LIST_FILE, "w") as f:
                    for name in detected_customer_names: f.write(name + "\n")
                print(f"Saved detected customer names to {CUSTOMER_LIST_FILE}")
            except Exception as e:
                print(f"ERROR saving detected customer names to {CUSTOMER_LIST_FILE}: {e}")
        except Exception as e:
            print(f"ERROR building FAISS index: {e}")
            traceback.print_exc()
            sys.exit(1)

    # --- Retriever Setup (remains the same) ---
    if vectorstore:
        try:
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": top_k_vectors}
            )
            print(f"Retriever initialized with k={top_k_vectors}")
        except Exception as e:
             print(f"ERROR creating retriever: {e}")
             traceback.print_exc()
             sys.exit(1)
    else:
        print("ERROR: Vectorstore initialization failed. Cannot create retriever.")
        sys.exit(1)

    # --- Chain Setup ---
    try:
        # *** CHANGE: Setup MapReduce Chain ***
        map_reduce_chain = setup_map_reduce_chain()
        print("MapReduce chain initialized")
    except Exception as e:
        # *** CHANGE: Error message ***
        print(f"ERROR setting up MapReduce chain: {e}")
        traceback.print_exc()
        sys.exit(1)

# --- Function to get detected names (remains the same) ---
def get_detected_customer_names() -> List[str]:
    """Returns the list of customer names detected during initialization."""
    global detected_customer_names
    if not detected_customer_names:
         try:
             with open(CUSTOMER_LIST_FILE, "r") as f:
                 detected_customer_names = sorted([line.strip() for line in f if line.strip() and line.strip() != "Unknown Customer"])
             print(f"Reloaded detected customer names in get() function: {detected_customer_names}")
         except FileNotFoundError:
             print(f"WARN: {CUSTOMER_LIST_FILE} not found in get() function.")
             return []
         except Exception as e:
             print(f"Error loading {CUSTOMER_LIST_FILE} in get() function: {e}")
             return []
    return detected_customer_names


# --- Direct Execution Test Block ---
if __name__ == '__main__':
    print("Initializing MapReduce Chain directly for testing...")
    initialize_app(top_k_vectors=15) # Using k=15 for testing
    print("Initialization complete.")

    print("\nTesting get_detected_customer_names():", get_detected_customer_names())

    if map_reduce_chain and retriever:
        # Example Query 1
        query1 = "which clause deals with termination in lactalis?"
        print(f"\n--- Testing Query 1: '{query1}' ---")
        try:
            customer_name_for_query = "Lactalis Australia"
            retrieved_docs1 = retriever.get_relevant_documents(query1)
            print(f"Retrieved {len(retrieved_docs1)} documents initially for Query 1.")

            filtered_docs1 = [d for d in retrieved_docs1 if d.metadata.get('customer') == customer_name_for_query]
            print(f"Simulating filter: {len(filtered_docs1)} documents remain for customer '{customer_name_for_query}'.")
            print("Filtered Docs (Source - Customer - Page):")
            for i, d in enumerate(filtered_docs1): print(f"  {i+1}: {d.metadata.get('source')} - {d.metadata.get('customer')} - Pg {d.metadata.get('page_number')}")

            # --- PREPROCESSING STEP for MapReduce ---
            processed_docs_for_map = []
            for doc in filtered_docs1:
                header = f"Source: {doc.metadata.get('source', 'Unknown')} | Page: {doc.metadata.get('page_number', 'N/A')} | Customer: {doc.metadata.get('customer', 'Unknown')} | Clause: {doc.metadata.get('clause', 'N/A')}\n---\n"
                processed_docs_for_map.append(
                    Document(page_content=header + doc.page_content, metadata=doc.metadata)
                )
            # -----------------------------------------

            chain_input1 = {"input_documents": processed_docs_for_map, "question": query1} # Use processed docs
            if processed_docs_for_map:
                result1 = map_reduce_chain.invoke(chain_input1)
                print("\nResult 1:")
                print(result1.get("output_text", "No result found."))
            else:
                print("\nResult 1: No documents found for the specified customer.")
        except Exception as e:
            print(f"ERROR invoking chain for Query 1: {e}")
            traceback.print_exc()

        # Example Query 2
        query2 = "compare termination clauses in simplot and patties contracts"
        print(f"\n--- Testing Query 2: '{query2}' ---")
        try:
            retrieved_docs2 = retriever.get_relevant_documents(query2)
            print(f"Retrieved {len(retrieved_docs2)} documents for Query 2.")
            print("Retrieved Docs (Source - Customer - Page):")
            for i, d in enumerate(retrieved_docs2): print(f"  {i+1}: {d.metadata.get('source')} - {d.metadata.get('customer')} - Pg {d.metadata.get('page_number')}")

            # --- PREPROCESSING STEP for MapReduce ---
            processed_docs_for_map_2 = []
            for doc in retrieved_docs2: # Use unfiltered docs for comparison
                header = f"Source: {doc.metadata.get('source', 'Unknown')} | Page: {doc.metadata.get('page_number', 'N/A')} | Customer: {doc.metadata.get('customer', 'Unknown')} | Clause: {doc.metadata.get('clause', 'N/A')}\n---\n"
                processed_docs_for_map_2.append(
                    Document(page_content=header + doc.page_content, metadata=doc.metadata)
                )
            # -----------------------------------------

            chain_input2 = {"input_documents": processed_docs_for_map_2, "question": query2} # Use processed docs
            result2 = map_reduce_chain.invoke(chain_input2)
            print("\nResult 2:")
            print(result2.get("output_text", "No result found."))
        except Exception as e:
            print(f"ERROR invoking chain for Query 2: {e}")
            traceback.print_exc()
    else:
        print("MapReduce chain or retriever not initialized, cannot run tests.")