import os
import json
import datetime
import logging
import uuid # For generating unique semantic IDs

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manages the saving and logging of new knowledge interpreted by the AI.
    Currently uses a JSON Lines file (jsonl) for persistent logging.
    Can be extended to interact with a database.
    """
    def __init__(self, log_directory, log_filename):
        """
        Initializes the MemoryManager.

        Args:
            log_directory (str): The absolute path to the directory where memory logs are stored.
            log_filename (str): The name of the memory log file.
        """
        self.log_directory = log_directory
        self.log_filepath = os.path.join(self.log_directory, log_filename)
        self._ensure_log_directory_exists()
        logger.info(f"MemoryManager initialized. Log file: {self.log_filepath}")

    def _ensure_log_directory_exists(self):
        """Ensures the log directory exists."""
        os.makedirs(self.log_directory, exist_ok=True)

    def generate_semantic_id(self, data_hash: str = None) -> str:
        """
        Generates a unique semantic ID. Could be based on content hash,
        or simply a UUID for unique identification.
        """
        if data_hash:
            return f"SEMID_{data_hash[:12]}_{uuid.uuid4().hex[:8]}"
        return f"SEMID_{uuid.uuid4().hex}"

    def save_knowledge_update(self, update_data: dict, semantic_id: str = None, timestamp=None):
        """
        Saves a new knowledge update to the memory log.

        Args:
            update_data (dict): A dictionary containing the new knowledge.
                                This should be JSON serializable.
                                Example: {"source": "document_analysis", "entity": "Gemini AI", "fact": "is a language model"}
            semantic_id (str, optional): A unique ID for the semantic entry. If None, one will be generated.
            timestamp (str, optional): An optional timestamp for the update. If None, current UTC time is used.
        """
        if not isinstance(update_data, dict):
            logger.error(f"Invalid update_data type. Expected dict, got {type(update_data)}")
            return

        if timestamp is None:
            timestamp = datetime.datetime.utcnow().isoformat() + 'Z' # ISO 8601 format, UTC
        
        if semantic_id is None:
            # Generate a semantic ID if not provided, perhaps based on a hash of the content
            # For simplicity, we'll generate a UUID-based one for now.
            semantic_id = self.generate_semantic_id()

        log_entry = {
            "timestamp": timestamp,
            "semantic_id": semantic_id,
            "update": update_data
        }

        try:
            with open(self.log_filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            logger.debug(f"Knowledge update saved: {log_entry}")
        except IOError as e:
            logger.error(f"Failed to write knowledge update to {self.log_filepath}: {e}")
        except TypeError as e:
            logger.error(f"Data not JSON serializable for {self.log_filepath}: {update_data}. Error: {e}")

    def load_all_knowledge_updates(self):
        """
        Loads all knowledge updates from the log file.
        Returns a list of dictionaries, each representing a logged update.
        """
        updates = []
        if not os.path.exists(self.log_filepath):
            logger.info(f"Memory log file not found: {self.log_filepath}. Returning empty list.")
            return updates

        try:
            with open(self.log_filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        updates.append(json.loads(line.strip()))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipping malformed JSON line in {self.log_filepath}: {line.strip()} - Error: {e}")
            logger.info(f"Loaded {len(updates)} knowledge updates from {self.log_filepath}")
        except IOError as e:
            logger.error(f"Failed to read knowledge updates from {self.log_filepath}: {e}")
        return updates
