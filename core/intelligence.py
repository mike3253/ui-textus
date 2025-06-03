import logging
import os
import re
import datetime
from brain.memory.memory_manager import MemoryManager
from brain.tier4.tier4_translator import T4Translator
from brain.tier4.tier4_interpreter_decoder import T4InterpreterDecoder

logger = logging.getLogger(__name__)

class IntelligenceCore:
    """
    Represents the core intelligence and knowledge interpretation logic of the AI.
    Now integrates with T4 translation and memory management.
    """
    def __init__(self, memory_manager: MemoryManager, t4_translator: T4Translator, t4_interpreter_decoder: T4InterpreterDecoder):
        self.memory_manager = memory_manager
        self.t4_translator = t4_translator
        self.t4_interpreter_decoder = t4_interpreter_decoder
        logger.info("IntelligenceCore initialized with MemoryManager, T4Translator, and T4InterpreterDecoder.")

    def _determine_academic_domain(self, text: str, source_path: str) -> str:
        """
        Simple heuristic to determine academic domain based on keywords or file path.
        This can be expanded with more sophisticated NLP models.
        """
        text_lower = text.lower()
        source_path_lower = source_path.lower()

        if "scientific" in text_lower or "experiment" in text_lower or "research paper" in text_lower or "journal" in text_lower or "biology" in text_lower or "physics" in text_lower or "chemistry" in text_lower:
            return "Science"
        if "theorem" in text_lower or "formula" in text_lower or "equation" in text_lower or "calculus" in text_lower or "algebra" in text_lower:
            return "Math"
        if "history" in text_lower or "ancient" in text_lower or "war" in text_lower or "empire" in text_lower or "historical" in text_lower:
            return "History"
        if "invoice" in text_lower or "financial" in text_lower or "statement" in text_lower or "balance" in text_lower:
            return "Financial"
        if "contract" in text_lower or "legal" in text_lower or "agreement" in text_lower:
            return "Legal"
        if "project" in text_lower or "deliverable" in text_lower or "meeting notes" in text_lower:
            return "Project"
        
        # Fallback to path analysis if no keywords
        if "science" in source_path_lower:
            return "Science"
        if "math" in source_path_lower:
            return "Math"
        if "history" in source_path_lower:
            return "History"
        if "financial" in source_path_lower or "invoices" in source_path_lower:
            return "Financial"
        if "legal" in source_path_lower or "contracts" in source_path_lower:
            return "Legal"
        if "project" in source_path_lower or "deliverables" in source_path_lower:
            return "Project"

        return "General"

    def interpret_new_information(self, raw_data: str, source: str) -> dict:
        """
        Interprets raw information, translates it into T4 format,
        stores it, and updates the memory log.

        Args:
            raw_data (str): The raw input data (e.g., text from a document).
            source (str): The source of the raw data (e.g., "file_path", "web_crawl_url").

        Returns:
            dict: A structured representation of the interpreted knowledge, including T4 ID.
                  Returns an empty dict if no new knowledge is extracted.
        """
        logger.info(f"Interpreting new information from source: {source}")

        # 1. Determine Academic Domain
        domain = self._determine_academic_domain(raw_data, source)
        logger.debug(f"Determined domain for '{source}': {domain}")

        # 2. Translate to T4 format
        # This will also store the T4 data in tier4_storage
        t4_data_output = self.t4_translator.translate(raw_data, source, domain)
        t4_semantic_id = t4_data_output.get("t4_semantic_id")

        if not t4_semantic_id:
            logger.error(f"T4 translation failed for source: {source}. No semantic ID generated.")
            return {}
        
        # 3. Prepare knowledge for memory update
        # This interpreted knowledge will be stored in memory_log.jsonl
        interpreted_knowledge = {
            "type": "T4_Interpretation",
            "semantic_id": t4_semantic_id,
            "domain": domain,
            "source": source,
            "t4_storage_path": t4_data_output.get("t4_storage_path"),
            "compressed_meaning": t4_data_output.get("compressed_meaning"),
            "raw_snippet": raw_data[:100] + "..." if len(raw_data) > 100 else raw_data
        }

        # 4. Update Knowledge (persist in memory log)
        self.update_knowledge(interpreted_knowledge, semantic_id=t4_semantic_id)
        
        return interpreted_knowledge

    def update_knowledge(self, new_knowledge_data: dict, semantic_id: str = None):
        """
        Handles the logic for updating the AI's knowledge base.
        This method will call the MemoryManager to persist the update.

        Args:
            new_knowledge_data (dict): The structured new knowledge to be added.
            semantic_id (str, optional): The semantic ID if already known.
        """
        if new_knowledge_data:
            logger.info(f"Updating knowledge with semantic ID: {semantic_id or 'N/A'}")
            self.memory_manager.save_knowledge_update(new_knowledge_data, semantic_id=semantic_id)
        else:
            logger.info("No new knowledge data provided for update.")

    def retrieve_and_decode_t4_knowledge(self, semantic_id: str) -> dict:
        """
        Retrieves and decodes T4 knowledge by its semantic ID.
        """
        logger.info(f"Attempting to retrieve and decode T4 knowledge for ID: {semantic_id}")
        decoded_data = self.t4_interpreter_decoder.decode_semantic_id(semantic_id)
        return decoded_data
