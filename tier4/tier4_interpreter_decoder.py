import os
import json
import logging

logger = logging.getLogger(__name__)

class T4InterpreterDecoder:
    """
    Interprets/decodes T4 semantic IDs and their associated data.
    """
    def __init__(self, t4_storage_directory):
        self.t4_storage_directory = t4_storage_directory
        if not os.path.isdir(self.t4_storage_directory):
            logger.warning(f"T4 storage directory not found: {t4_storage_directory}")
        logger.info(f"T4InterpreterDecoder initialized. T4 storage: {t4_storage_directory}")

    def decode_semantic_id(self, t4_semantic_id: str) -> dict:
        """
        Decodes a T4 semantic ID by looking up its associated data.

        Args:
            t4_semantic_id (str): The T4 semantic ID to decode.

        Returns:
            dict: The original T4 data associated with the ID, or an error dict if not found.
        """
        logger.info(f"Decoding T4 semantic ID: {t4_semantic_id}")
        t4_file_name = f"{t4_semantic_id}.json"
        t4_file_path = os.path.join(self.t4_storage_directory, t4_file_name)

        if not os.path.exists(t4_file_path):
            logger.warning(f"T4 semantic data file not found for ID: {t4_semantic_id} at {t4_file_path}")
            return {"error": "T4 data not found", "semantic_id": t4_semantic_id}
        
        try:
            with open(t4_file_path, 'r', encoding='utf-8') as f:
                t4_data = json.load(f)
            logger.debug(f"Successfully decoded T4 data for ID {t4_semantic_id}")
            return t4_data
        except IOError as e:
            logger.error(f"Error reading T4 data file {t4_file_path}: {e}")
            return {"error": f"Failed to read data: {e}", "semantic_id": t4_semantic_id}
        except json.JSONDecodeError as e:
            logger.error(f"Malformed JSON in T4 data file {t4_file_path}: {e}")
            return {"error": f"Malformed T4 data: {e}", "semantic_id": t4_semantic_id}
    
    def get_all_semantic_ids(self):
        """
        Retrieves all semantic IDs currently stored in the T4 storage.
        """
        ids = []
        if not os.path.isdir(self.t4_storage_directory):
            logger.warning(f"T4 storage directory '{self.t4_storage_directory}' not found.")
            return ids
            
        for filename in os.listdir(self.t4_storage_directory):
            if filename.endswith(".json"):
                ids.append(filename.replace(".json", ""))
        logger.info(f"Found {len(ids)} semantic IDs in T4 storage.")
        return ids
