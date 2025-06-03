import os
import json
import logging
import hashlib
import datetime # Import datetime for interpretation_date

logger = logging.getLogger(__name__)

class T4Translator:
    """
    Simulates the translation of raw text into a semantic T4 format.
    This version uses simple keyword matching and configured rules for 'compression'.
    """
    def __init__(self, semantic_compression_rules_path, t4_storage_directory):
        self.rules = self._load_semantic_compression_rules(semantic_compression_rules_path)
        self.t4_storage_directory = t4_storage_directory
        os.makedirs(self.t4_storage_directory, exist_ok=True)
        logger.info(f"T4Translator initialized. Rules loaded from {semantic_compression_rules_path}, T4 storage: {t4_storage_directory}")

    def _load_semantic_compression_rules(self, rules_file_path):
        """Loads semantic compression rules from a JSON file."""
        try:
            with open(rules_file_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
                logger.debug(f"Loaded semantic compression rules: {rules}")
                return rules
        except FileNotFoundError:
            logger.error(f"Semantic compression rules file not found: {rules_file_path}")
            return {"compression_rules": [], "default_semantic_id_prefix": "SEM_GENERIC"}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in semantic compression rules file '{rules_file_path}': {e}")
            return {"compression_rules": [], "default_semantic_id_prefix": "SEM_GENERIC"}

    def _apply_compression_rules(self, text):
        """Applies basic keyword-based compression rules to text."""
        for rule in self.rules.get("compression_rules", []):
            pattern = rule.get("pattern")
            semantic_id_prefix = rule.get("semantic_id_prefix")
            if pattern and semantic_id_prefix and pattern.lower() in text.lower():
                return {
                    "semantic_id_prefix": semantic_id_prefix,
                    "meaning": rule.get("meaning", "No specific meaning provided.")
                }
        return None

    def translate(self, raw_text: str, source_id: str, domain: str = "General") -> dict:
        """
        Translates raw text into a T4 semantic representation.
        Assigns a semantic ID and stores the representation.

        Args:
            raw_text (str): The raw text to translate.
            source_id (str): A unique ID for the source of this raw text (e.g., file path hash).
            domain (str): The academic domain (e.g., "Science", "Math", "History", "Financial").

        Returns:
            dict: A dictionary containing the T4 representation:
                  {
                      "t4_semantic_id": "SEMID_XYZ_123",
                      "raw_hash": "abc123def456",
                      "domain": "Science",
                      "compressed_meaning": "Meaning from rule (if applied)",
                      "compressed_id_prefix": "COMP_XYZ",
                      "t4_storage_path": "/path/to/t4_data_file.json"
                  }
        """
        logger.info(f"Translating raw text from source: {source_id}, domain: {domain}")

        raw_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
        
        # Apply semantic compression rules
        compression_result = self._apply_compression_rules(raw_text)
        
        semantic_id_core = compression_result["semantic_id_prefix"] if compression_result else self.rules.get("default_semantic_id_prefix", "SEM_GENERIC")
        
        # Combine prefix with a unique identifier based on raw_hash and a UUID
        t4_semantic_id = f"{semantic_id_core}_{raw_hash[:8]}"

        t4_data = {
            "t4_semantic_id": t4_semantic_id,
            "raw_text_hash": raw_hash,
            "domain": domain,
            "original_source_id": source_id,
            "interpretation_date": datetime.datetime.utcnow().isoformat() + 'Z',
            "compressed_meaning": compression_result["meaning"] if compression_result else "No specific compression rule applied.",
            "raw_snippet": raw_text[:200] + "..." if len(raw_text) > 200 else raw_text
        }

        # Store the T4 data in a separate file within tier4_storage
        t4_file_name = f"{t4_semantic_id}.json"
        t4_file_path = os.path.join(self.t4_storage_directory, t4_file_name)
        try:
            with open(t4_file_path, 'w', encoding='utf-8') as f:
                json.dump(t4_data, f, indent=4)
            logger.debug(f"T4 data stored to: {t4_file_path}")
            t4_data["t4_storage_path"] = os.path.relpath(t4_file_path, self.t4_storage_directory) # Store relative path for lookup
        except IOError as e:
            logger.error(f"Failed to store T4 data for {t4_semantic_id}: {e}")
            t4_data["t4_storage_path"] = "ERROR: Storage failed"
        
        return t4_data
