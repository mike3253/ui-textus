import logging
import argparse
import os
import sys

# Set up basic logging configuration
# DEBUG level will show all debug messages from all loggers
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(name)s: %(message)s')
logger = logging.getLogger("BrainCore")
logger.info("BrainCore module loading...")

# Add the project root to the Python path for module imports
# This ensures components can be imported correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
logger.debug(f"Added '{project_root}' to sys.path")


# Import components
try:
    from components.nlu.t2_parser import T2Parser
    logger.debug("T2Parser module loaded from: %s", T2Parser.__module__)
except ImportError as e:
    logger.error(f"Failed to import T2Parser: {e}")
    sys.exit(1) # Use sys.exit(1) to stop execution on critical import failure

try:
    from components.dispatchers.dispatcher import Dispatcher
    logger.debug("Dispatcher module loaded from: %s", Dispatcher.__module__)
except ImportError as e:
    logger.error(f"Failed to import Dispatcher: {e}")
    sys.exit(1)

try:
    from components.interpreters.math_ai import MathAI
    logger.debug("math_ai module loaded from: %s", MathAI.__module__)
except ImportError as e:
    logger.error(f"Failed to import MathAI: {e}")
    sys.exit(1)

try:
    from components.memory.short_term_memory import ShortTermMemory
    logger.debug("ShortTermMemory module loaded from: %s", ShortTermMemory.__module__)
except ImportError as e:
    logger.error(f"Failed to import ShortTermMemory: {e}")
    sys.exit(1)

try:
    from components.memory.long_term_memory import LongTermMemory
    logger.debug("LongTermMemory module loaded from: %s", LongTermMemory.__module__)
except ImportError as e:
    logger.error(f"Failed to import LongTermMemory: {e}")
    sys.exit(1)

try:
    from components.memory.semantic_memory import SemanticMemory
    logger.debug("SemanticMemory module loaded from: %s", SemanticMemory.__module__)
except ImportError as e:
    logger.error(f"Failed to import SemanticMemory: {e}")
    sys.exit(1)

# Define data directory for memory files
DATA_DIR = os.path.join(project_root, 'data') # Use project_root to ensure correct path
MEMORY_FILE = os.path.join(DATA_DIR, 'memory.json')

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
logger.info(f"Data directory ensured at: {DATA_DIR}")


class BrainCore:
    def __init__(self):
        self.nlu = T2Parser()
        self.math_ai = MathAI() # Instantiate MathAI
        self.dispatcher = Dispatcher() # Initialize Dispatcher
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory(file_path=MEMORY_FILE)
        self.semantic_memory = SemanticMemory(ltm_instance=self.ltm)

        # Register interpreters with the dispatcher
        # The dispatcher's register_interpreter method now expects a domain and a callable function
        # math_ai.interpret_math_snippet is that callable function for the 'math' domain.
        self.dispatcher.register_interpreter("math", self.math_ai.interpret_math_snippet)
        logger.info("BrainCore initialized with NLU, Dispatcher, MathAI, STM, LTM, SemanticMemory.")

    def process_input(self, text: str):
        logger.info(f"Processing input: '{text}'")
        # Step 1: NLU Interpretation
        interpretation_result = self.nlu.parse_input(text)
        logger.debug(f"NLU Interpretation: {interpretation_result}")

        if interpretation_result.get("status") == "fail":
            logger.warning(f"NLU failed to parse input: {text}. Error: {interpretation_result.get('error_message')}")
            return {"status": "error", "response": interpretation_result.get("error_message", "I didn't understand that."), "source": "NLU"}

        # Add interpretation to STM
        self.stm.add_entry(interpretation_result)
        logger.debug(f"Added to STM. Current STM size: {len(self.stm)}")

        # Generate semantic ID for potential LTM storage/retrieval
        semantic_id = self.semantic_memory.generate_semantic_id(interpretation_result)
        logger.debug(f"Generated Semantic ID: {semantic_id}")

        # Check LTM for existing memory
        if self.ltm.get_entry(semantic_id):
            logger.info(f"Found existing LTM entry for semantic ID: {semantic_id}")
            # In a real AI, you'd retrieve and use this memory, potentially returning its cached result
            existing_entry = self.ltm.get_entry(semantic_id)
            response = f"I recall something similar. Result from LTM: {existing_entry.get('result', 'N/A')}"
            return {"status": "success", "response": response, "source": "LTM"}
        else:
            logger.info(f"No existing LTM entry for semantic ID: {semantic_id}. Attempting to dispatch.")
            # Step 2: Dispatch and Execute
            domain = interpretation_result.get("domain")
            concept = interpretation_result.get("concept")
            payload = interpretation_result.get("payload_received")

            # CRITICAL CHECK: Ensure domain and concept are valid before dispatch
            if domain and concept and domain != "unknown" and concept != "unknown":
                dispatch_result = self.dispatcher.dispatch(domain, concept, payload)
                logger.debug(f"Dispatcher Result: {dispatch_result}")

                if dispatch_result.get("status") == "success":
                    # Store new knowledge in LTM
                    ltm_entry = {
                        "semantic_id": semantic_id,
                        "timestamp": os.path.getmtime(__file__), # Example timestamp (of brain_core.py)
                        "original_input": text,
                        "interpretation": interpretation_result,
                        "result": dispatch_result.get("result"),
                        "source_module": dispatch_result.get("source_module")
                    }
                    self.ltm.add_entry(semantic_id, ltm_entry)
                    self.ltm.save_memory() # Save LTM after adding new entry
                    logger.info(f"New entry added to LTM with semantic ID: {semantic_id}")
                    return {"status": "success", "response": dispatch_result.get("result"), "source": dispatch_result.get("source_module")}
                else:
                    return {"status": "error", "response": dispatch_result.get("error", "Unknown dispatch error."), "source": dispatch_result.get("source_module", "Dispatcher")}
            else:
                # This path should be taken if NLU returns unknown domain/concept
                return {"status": "error", "response": f"NLU could not fully determine intent. Domain: {domain}, Concept: {concept}", "source": "NLU"}

    def run_cli(self):
        logger.info("Starting BrainCore CLI. Type 'exit' to quit.")
        while True:
            user_input = input("WordForge> ").strip()
            if user_input.lower() == 'exit':
                logger.info("Exiting CLI.")
                break
            if not user_input:
                continue

            result = self.process_input(user_input)
            response = result.get("response", "I don't understand that.")
            source = result.get("source", "Unknown")
            status = result.get("status", "error")

            print(f"[{status.upper()}] ({source}): {response}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the BrainCore AI.")
    parser.add_argument("--cli_mode", action="store_true", help="Run in command-line interface mode.")
    args = parser.parse_args()

    brain_core = BrainCore()

    if args.cli_mode:
        brain_core.run_cli()
    else:
        logger.info("No specific mode selected. Exiting. Use --cli_mode to run the CLI.")

