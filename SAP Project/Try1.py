import pandas as pd
import os
import pickle
from sentence_transformers import SentenceTransformer, util
import time
import logging # For more advanced logging

# --- Configure Logging ---
# This will output INFO level messages and above to the console.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ItemMatcher:
    def __init__(self, excel_path, model_name='all-MiniLM-L6-v2', cache_path='embeddings_cache.pkl', log_path='learning_log.pkl', device='cpu'):
        """
        Initializes the ItemMatcher with an Excel file containing item descriptions.

        Args:
            excel_path (str): Path to the Excel file with 'ItemCode' and 'ItemDescription' columns.
            model_name (str): Name of the SentenceTransformer model to use.
            cache_path (str): Path to store/load sentence embeddings cache.
            log_path (str): Path to store/load search query logs.
            device (str): Device to run the model on. Explicitly set to 'cpu' for CPU-only environments.
        """
        self.excel_path = excel_path
        self.cache_path = cache_path
        self.log_path = log_path

        # Initialize the model on the specified device (CPU)
        try:
            self.model = SentenceTransformer(model_name, device=device)
            logging.info(f"SentenceTransformer model '{model_name}' loaded successfully on {device.upper()}.")
        except Exception as e:
            logging.critical(f"Failed to load SentenceTransformer model '{model_name}': {e}")
            logging.critical("Please ensure the model name is correct and you have an internet connection for the first download.")
            exit(1) # Exit if the model cannot be loaded

        self.data = self._load_data()
        self.embeddings = None
        self._load_or_create_cache()

    def _load_data(self):
        """Loads data from the Excel file and performs initial validation."""
        try:
            logging.info(f"Attempting to load data from Excel file: '{self.excel_path}'")
            data = pd.read_excel(self.excel_path)
            
            # Check for essential columns
            required_columns = ['ItemCode', 'ItemDescription']
            for col in required_columns:
                if col not in data.columns:
                    raise ValueError(f"Excel file must contain a '{col}' column.")
            
            data.fillna('', inplace=True) # Fill NaN values with empty strings
            
            if data.empty:
                logging.warning("Excel file loaded but contains no data rows. The matcher will not have items to search.")
            else:
                logging.info(f"Successfully loaded {len(data)} items from Excel.")
            
            return data
        except FileNotFoundError:
            logging.critical(f"Error: Excel file not found at '{self.excel_path}'. Please check the path.")
            exit(1) # Exit if the file is not found
        except pd.errors.EmptyDataError:
            logging.critical(f"Error: Excel file '{self.excel_path}' is empty or has no parseable data.")
            exit(1)
        except Exception as e:
            logging.critical(f"An unexpected error occurred while loading Excel data from '{self.excel_path}': {e}")
            exit(1)

    def _load_or_create_cache(self):
        """
        Loads embeddings from cache if available and up-to-date,
        otherwise generates new embeddings and saves them.
        """
        # Get modification time of the Excel file to check cache freshness
        try:
            excel_last_modified_time = os.path.getmtime(self.excel_path)
        except OSError as e:
            logging.error(f"Could not get modification time for '{self.excel_path}': {e}. Forcing embedding regeneration.")
            excel_last_modified_time = -1 # Sentinel value to force regeneration

        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'rb') as f:
                try:
                    cache = pickle.load(f)
                    # Check if file modification time matches
                    if cache.get('file') == excel_last_modified_time:
                        self.embeddings = cache['embeddings']
                        logging.info("Loaded embeddings from cache.")
                        return
                    else:
                        logging.info("Excel file has been modified or cache is outdated. Re-generating embeddings.")
                except (pickle.UnpicklingError, EOFError) as e:
                    logging.warning(f"Error loading cache '{self.cache_path}': {e}. Cache might be corrupt. Re-generating embeddings.")
                except Exception as e:
                    logging.warning(f"Unexpected error with cache '{self.cache_path}': {e}. Re-generating embeddings.")

        logging.info("Generating embeddings. This may take a while for large datasets...")
        start_time = time.time()
        descriptions = self.data['ItemDescription'].tolist()

        if not descriptions:
            logging.warning("No item descriptions found in the Excel data to generate embeddings for. Search functionality will be limited.")
            self.embeddings = []
            return

        # Batch encoding for efficiency and a built-in progress bar
        # 'show_progress_bar=True' will display a tqdm progress bar in the console
        # 'batch_size' can be tuned based on your system's memory
        try:
            self.embeddings = self.model.encode(
                descriptions,
                convert_to_tensor=True,
                show_progress_bar=True,
                batch_size=32 # A common default, adjust if memory is an issue
            )
            elapsed = time.time() - start_time
            logging.info(f"Finished generating {len(self.embeddings)} embeddings in {elapsed:.1f} seconds.")
        except Exception as e:
            logging.critical(f"Error during embedding generation: {e}. Cannot perform searches.")
            self.embeddings = None # Ensure embeddings are None if generation fails
            return

        # Save the newly generated embeddings to cache
        try:
            with open(self.cache_path, 'wb') as f:
                pickle.dump({'file': excel_last_modified_time, 'embeddings': self.embeddings}, f)
            logging.info(f"Embeddings saved to cache: '{self.cache_path}'")
        except Exception as e:
            logging.error(f"Failed to save embeddings to cache '{self.cache_path}': {e}. This might slow down future runs.")

    def search(self, query, top_k=5, min_score_threshold=0.0):
        """
        Performs a semantic search for the given query against item descriptions.

        Args:
            query (str): The search query.
            top_k (int): The number of top matches to return.
            min_score_threshold (float): Minimum similarity score for a result to be included.
                                         Results with scores below this will be filtered out.

        Returns:
            list: A list of dictionaries, each containing 'ItemCode', 'ItemDescription', and 'Score'.
                  Returns an empty list if no relevant matches are found or if embeddings are not ready.
        """
        if not query or not query.strip():
            logging.warning("Search query is empty or whitespace only. Returning no matches.")
            return []

        if self.embeddings is None or len(self.embeddings) == 0:
            logging.warning("No embeddings available for search. Please check your data and cache generation. Cannot perform search.")
            return []

        try:
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            # util.semantic_search expects corpus_embeddings to be a single tensor
            hits = util.semantic_search(query_embedding, self.embeddings, top_k=top_k)[0]
        except Exception as e:
            logging.error(f"Error during semantic search for query '{query}': {e}")
            return []

        results = []
        for hit in hits:
            score = hit['score']
            if score < min_score_threshold:
                # If score is below threshold, skip this result and any subsequent lower-scoring results
                break 

            idx = hit['corpus_id']
            # Using .iloc for integer-location based indexing
            row = self.data.iloc[idx] 
            results.append({
                'ItemCode': row['ItemCode'],
                'ItemDescription': row['ItemDescription'],
                'Score': round(score, 4) # Round score for cleaner display
            })
        
        return results

    def log_search_feedback(self, query, search_results, user_selected_item_code=None):
        """
        Logs detailed search query information and user feedback for analysis and potential learning.

        Args:
            query (str): The original search query.
            search_results (list): The list of dictionaries returned by the search method.
            user_selected_item_code (str, optional): The ItemCode the user confirmed or provided.
                                                     Defaults to None if no specific feedback was given.
        """
        suggested_top_code = search_results[0]['ItemCode'] if search_results else None
        
        feedback_status = "No matches suggested"
        if suggested_top_code:
            feedback_status = "No feedback given" # Default if user doesn't provide specific feedback

        if user_selected_item_code:
            if user_selected_item_code.lower() == 'skip': # User explicitly skipped
                feedback_status = "Feedback skipped by user"
            elif user_selected_item_code == suggested_top_code:
                feedback_status = "Top match confirmed by user"
            else:
                # Check if the user's selection was among the suggested results
                suggested_codes = {res['ItemCode'] for res in search_results}
                if user_selected_item_code in suggested_codes:
                    feedback_status = "Other suggested match selected by user"
                else:
                    feedback_status = "New code provided by user"
        elif suggested_top_code and not user_selected_item_code:
             feedback_status = "No specific feedback given (top match exists)"
        
        log_entry = {
            'query': query,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'suggested_top_match_code': suggested_top_code,
            'all_suggested_results': search_results, # Log all suggested results
            'user_selected_item_code': user_selected_item_code,
            'feedback_status': feedback_status
        }

        logs = []
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, 'rb') as f:
                    logs = pickle.load(f)
                    if not isinstance(logs, list): # Handle corrupted log files
                        logging.warning(f"Log file '{self.log_path}' content is not a list. Starting a new log.")
                        logs = []
            except (pickle.UnpicklingError, EOFError):
                logging.warning(f"Corrupt or empty log file at {self.log_path}. Starting a new log.")
            except Exception as e:
                logging.warning(f"Error loading log file '{self.log_path}': {e}. Starting a new log.")

        logs.append(log_entry)

        try:
            with open(self.log_path, 'wb') as f:
                pickle.dump(logs, f)
            logging.debug(f"Logged feedback for query: '{query}' with status: '{feedback_status}'")
        except Exception as e:
            logging.error(f"Failed to save log entry to '{self.log_path}': {e}")


# --- Configuration Constants for File Paths ---
# IMPORTANT: Adjust these paths according to your actual file locations
# Example: If your script is in 'D:/documents/desktop/item-matcher/matcher/FinalItemDescription1/'
# And your Excel is in 'D:/documents/desktop/item-matcher/'
# Then relative paths might be:
# EXCEL_PATH = "../../SAPITEMCODEPYTHON.xlsx"
# EMBEDDINGS_CACHE_PATH = "../../embeddings_cache.pkl"
# LEARNING_LOG_PATH = "../../learning_log.pkl"
# For absolute paths, ensure they are correct for your system.
EXCEL_PATH = "D:/documents/desktop/item-matcher/SAPITEMCODEPYTHON.xlsx"
EMBEDDINGS_CACHE_PATH = "D:/documents/desktop/item-matcher/embeddings_cache.pkl"
LEARNING_LOG_PATH = "D:/documents/desktop/item-matcher/learning_log.pkl"

if __name__ == '__main__':
    print("--- Initializing Item Matcher ---")
    try:
        # Initialize ItemMatcher. 'device='cpu'' forces CPU usage.
        matcher = ItemMatcher(
            excel_path=EXCEL_PATH,
            cache_path=EMBEDDINGS_CACHE_PATH,
            log_path=LEARNING_LOG_PATH,
            device='cpu' 
        )
    except Exception as e:
        print(f"\nCRITICAL ERROR: Failed to initialize ItemMatcher. Please check logs above. Exiting.")
        exit(1)

    print("\nItem Matcher Ready!")
    print("Type 'exit' to quit at any time.")
    print("---------------------------------")

    while True:
        user_input_query = input("\nEnter item description to search: ")
        
        if user_input_query.lower() == 'exit':
            print("\nExiting Item Matcher. Goodbye!")
            break
        
        if not user_input_query.strip(): # Check if the input is empty or just whitespace
            print("Please enter a description to search for.")
            continue

        # Perform the search
        # Adjust top_k and min_score_threshold here as needed for your application
        # min_score_threshold=0.3 is an example; you might need to tune this.
        search_results = matcher.search(user_input_query, top_k=5, min_score_threshold=0.3) 
        
        print("\n--- Top Matches ---")
        if search_results:
            for i, res in enumerate(search_results):
                print(f"Match {i+1}:")
                print(f"  Code: {res['ItemCode']} | Score: {res['Score']:.4f}")
                print(f"  Description: {res['ItemDescription']}\n")
        else:
            print("No relevant matches found for your query. Try a different description or lower the threshold.")
        print("-------------------")

        # --- User Feedback Section ---
        feedback_prompt = (
            "Was any of this correct?\n"
            "Enter the correct Item Code (e.g., 'CODE123').\n"
            "Type 'N/A' if none of the suggestions were right.\n"
            "Type 'skip' to skip providing feedback.\n"
            "Your feedback: "
        )
        user_feedback_code = input(feedback_prompt).strip()

        # Normalize feedback for logging
        if user_feedback_code.lower() == 'n/a':
            user_feedback_code = None # No specific code provided as correct
        elif user_feedback_code.lower() == 'skip':
            # This case will be handled by the log_search_feedback function's 'skip' check
            pass 
        elif user_feedback_code == '':
            user_feedback_code = None # User just pressed enter without typing
        
        matcher.log_search_feedback(user_input_query, search_results, user_feedback_code)
        print("Feedback logged. Thank you!")