# routes.py

from flask import Blueprint, render_template, request, jsonify
import langchain_utils.qa_chain as qa_module
from langchain_utils.qa_chain import get_detected_customer_names
import markdown
from langchain_core.callbacks.manager import CallbackManager
from email_tracer import EmailLangChainTracer
import re
import sys
import traceback
from langchain.chains.mapreduce import MapReduceDocumentsChain # For type hint
from langchain_core.documents import Document
from typing import List # Import List for type hinting

main_blueprint = Blueprint("main", __name__)

# --- Helpers (generate_keyword, get_customer_filter_keyword) remain the same ---
def generate_keyword(customer_name):
    if not customer_name: return None
    name_cleaned = customer_name
    suffixes = [' Pty Ltd', ' Pty Limited', ' Ltd', ' Limited', ' Inc']
    for suffix in suffixes:
        if name_cleaned.endswith(suffix):
            name_cleaned = name_cleaned[:-len(suffix)]
            break
    parts = name_cleaned.split()
    return parts[0].lower() if parts else None

def get_customer_filter_keyword(query):
    detected_names = get_detected_customer_names()
    customer_keywords_map = {}
    for name in detected_names:
        keyword = generate_keyword(name)
        if keyword:
            customer_keywords_map[keyword] = name
            full_name_keyword = name.lower().replace(" ", "")
            if full_name_keyword != keyword:
                 customer_keywords_map[full_name_keyword] = name

    query_lower = query.lower()
    found_original_names = []
    sorted_keywords = sorted(customer_keywords_map.keys(), key=len, reverse=True)
    temp_query = query_lower
    for query_keyword in sorted_keywords:
        regex_pattern = rf'\b{re.escape(query_keyword)}\b'
        match = re.search(regex_pattern, temp_query)
        if match:
            original_name = customer_keywords_map[query_keyword]
            if original_name not in found_original_names:
                 found_original_names.append(original_name)
                 temp_query = temp_query[:match.start()] + "_"*len(query_keyword) + temp_query[match.end():]

    if len(found_original_names) == 1:
        name_to_filter = found_original_names[0]
        print(f"DEBUG [Filter]: SUCCESS - Will filter for customer metadata exactly matching: '{name_to_filter}'")
        return name_to_filter
    elif len(found_original_names) > 1:
        print(f"DEBUG [Filter]: Multiple customers found ({found_original_names}). No filter applied (comparative query).")
        return None
    else:
        print("DEBUG [Filter]: No specific customer detected. No filter applied.")
        return None
# --- End Helper ---


@main_blueprint.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            user_query = data.get("query", "")
            user_email = data.get("email", "")
        else: # Handle form data
            user_query = request.form.get("query", "")
            user_email = request.form.get("email", "")

        answer = "An error occurred."
        sources = []
        retrieved_docs_for_display = []

        print(f"\n--- NEW REQUEST ---")
        print(f"User Query: {user_query}")
        print(f"User Email: {user_email}")

        if not user_query.strip():
            answer = "Please enter a valid query."
            sources = None
        else:
            # Check for MapReduce chain
            if qa_module.retriever is None or qa_module.map_reduce_chain is None:
                 print("ERROR: Retriever or MapReduce chain not initialized!")
                 if request.is_json: return jsonify({"error": "System not ready"}), 500
                 else: return render_template("index.html", query=user_query, answer="Error: System not ready.", sources=None), 500

            # Setup callbacks
            try:
                tracer = EmailLangChainTracer(project_name="pr-new-molecule-89")
                callback_manager = CallbackManager([tracer])
            except Exception as e:
                print(f"Error initializing tracer: {e}")
                callback_manager = CallbackManager([])

            # Determine filtering
            filter_customer_name = get_customer_filter_keyword(user_query)
            print(f"DEBUG: Customer filter identified: {filter_customer_name}")

            try:
                # --- Retrieval ---
                print(f"DEBUG: Retrieving documents for query: '{user_query}'")
                initial_docs: List[Document] = qa_module.retriever.get_relevant_documents(
                    user_query, callbacks=callback_manager
                )
                print(f"DEBUG: Initial retrieval found {len(initial_docs)} documents.")
                print("--- Initial Retrieved Docs Metadata ---")
                for i, doc in enumerate(initial_docs):
                    print(f"  Doc {i+1}: Src={doc.metadata.get('source')}, Pg={doc.metadata.get('page_number')}, Cust={doc.metadata.get('customer')}, Clause={doc.metadata.get('clause')}")
                print("--- End Initial Retrieved Docs Metadata ---")

                # --- Filtering ---
                docs_to_process: List[Document] = initial_docs
                if filter_customer_name:
                    print(f"DEBUG: Applying filter for customer: '{filter_customer_name}'")
                    filtered_docs = [
                        doc for doc in initial_docs
                        if doc.metadata.get('customer', '') == filter_customer_name
                    ]
                    if not filtered_docs:
                         print(f"WARN: Post-filtering removed all documents for customer '{filter_customer_name}'.")
                         answer = f"I found general information related to your query, but could not find documents specifically for '{filter_customer_name}'. Please check the customer name or broaden your search."
                         sources = []
                         docs_to_process = []
                    else:
                        docs_to_process = filtered_docs
                    print(f"DEBUG: {len(docs_to_process)} docs remaining after filtering.")
                    print("--- Filtered Docs Metadata (if filter applied) ---")
                    for i, doc in enumerate(docs_to_process):
                        print(f"  Doc {i+1}: Src={doc.metadata.get('source')}, Pg={doc.metadata.get('page_number')}, Cust={doc.metadata.get('customer')}, Clause={doc.metadata.get('clause')}")
                    print("--- End Filtered Docs Metadata ---")
                else:
                    print("DEBUG: No customer filter applied (comparative or no specific customer detected).")

                # Docs for final source display should reflect what *could* have been used
                retrieved_docs_for_display = docs_to_process

                # --- Chain Execution ---
                if not docs_to_process:
                     if answer == "An error occurred.":
                        answer = "Could not find relevant documents for your query after retrieval/filtering."
                        sources = []
                else:
                    # *** WORKAROUND A: Prepend metadata to page_content for Map step ***
                    print(f"DEBUG: Prepending metadata to content for {len(docs_to_process)} documents...")
                    processed_docs_for_map = []
                    for doc in docs_to_process:
                        # Create a clear header string
                        header = (
                            f"Source: {doc.metadata.get('source', 'Unknown')} | "
                            f"Page: {doc.metadata.get('page_number', 'N/A')} | "
                            f"Customer: {doc.metadata.get('customer', 'Unknown')} | "
                            f"Clause: {doc.metadata.get('clause', 'N/A')}\n"
                            f"---\n"
                        )
                        # Create a *new* Document object with the modified content
                        processed_docs_for_map.append(
                            Document(page_content=header + doc.page_content, metadata=doc.metadata)
                        )
                    print(f"DEBUG: Example of first processed doc content for Map:\n{processed_docs_for_map[0].page_content[:500]}...")
                    # *****************************************************************

                    # *** Use the processed docs in the chain input ***
                    chain_input = {
                        "input_documents": processed_docs_for_map, # Use modified docs
                        "question": user_query
                    }
                    print(f"DEBUG: Invoking MapReduce chain...")
                    try:
                        result = qa_module.map_reduce_chain.invoke(
                            chain_input,
                            config={"callbacks": callback_manager, "metadata": {"user_email": user_email}}
                        )
                        answer_raw = result.get("output_text", "Error: Could not generate answer from MapReduce chain.")
                        print("--- Raw LLM Response (Reduce Step) ---")
                        print(answer_raw)
                        print("--- End Raw LLM Response ---")
                        answer = answer_raw
                    except Exception as e:
                         print(f"Error invoking MapReduce chain: {e}")
                         traceback.print_exc()
                         answer = "Error processing query via MapReduce chain."

                # --- Source Generation (Use metadata from original docs before preprocessing) ---
                sources = []
                seen_sources = set()
                # Use retrieved_docs_for_display which has the original metadata
                for doc in retrieved_docs_for_display:
                    source_file = doc.metadata.get('source', 'Unknown Source')
                    page_num = doc.metadata.get('page_number', 'N/A')
                    customer_display = doc.metadata.get('customer', 'Unknown Customer')
                    source_key = f"{source_file}|Page {page_num}"

                    if source_key not in seen_sources:
                        source_str = f"{source_file} (Customer: {customer_display}) - Page {page_num}"
                        clause_display = doc.metadata.get('clause', None)
                        hierarchy_display = doc.metadata.get('hierarchy', [])
                        if clause_display and clause_display != 'N/A': source_str += f" (Clause: {clause_display})"
                        elif hierarchy_display:
                            try: source_str += f" (Section: {hierarchy_display[-1]})"
                            except IndexError: pass
                        sources.append(source_str)
                        seen_sources.add(source_key)

                # --- Final Formatting (remains the same) ---
                if "Error:" not in answer and "Could not find" not in answer:
                    if not isinstance(answer, str): answer = str(answer)
                    answer = markdown.markdown(answer, extensions=['fenced_code', 'tables'])
                elif not isinstance(answer, str):
                     answer = str(answer)

            except Exception as e:
                 print(f"Error during document processing or chain execution: {e}")
                 traceback.print_exc()
                 answer = "An unexpected error occurred while processing your query."
                 sources = []

        # --- Return Response ---
        print(f"DEBUG: Final Answer Prepared:\n{answer[:500]}...")
        print(f"DEBUG: Final Sources Prepared: {sources}")
        if request.is_json:
            return jsonify({"answer": answer, "sources": sources})
        else:
            return render_template("index.html", query=user_query, answer=answer, sources=sources)

    # GET request
    return render_template("index.html", query="", answer="", sources=None)