import os
import re
import json
import logging

logger = logging.getLogger(__name__)

def load_rules(rules_file_path):
    """Loads validation rules from a JSON file."""
    try:
        with open(rules_file_path, 'r') as f:
            rules = json.load(f)
            logger.info(f"Successfully loaded rules from: {rules_file_path}")
            return rules
    except FileNotFoundError:
        logger.error(f"Rules file not found: {rules_file_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in rules file '{rules_file_path}': {e}")
        return None

def check_placement(root_dir, rules):
    """
    Checks if folders and documents are in their 'right place' based on loaded rules.
    Returns a list of dictionaries, each describing a misplaced item.
    """
    misplaced_items = []

    if not rules:
        logger.warning("No rules loaded for placement validation. Skipping checks.")
        return misplaced_items

    folder_rules = rules.get("folder_rules", [])
    file_rules = rules.get("file_rules", [])

    logger.info(f"Starting placement validation for: {root_dir}")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Determine the effective parent directory name for rule comparison
        # This is the name of the current directory (dirpath)
        parent_dir_name = os.path.basename(dirpath) 
        
        # For the root directory itself, parent_dir_name is often the name of the root.
        # If rules need to apply to items directly under the root, adjust this logic.
        # For typical placement rules, we check children relative to 'parent_dir_name'.
        
        # Check folders
        for dirname in dirnames:
            full_folder_path = os.path.join(dirpath, dirname)
            relative_folder_path = os.path.relpath(full_folder_path, root_dir)
            
            for rule in folder_rules:
                name_pattern = rule.get("name_pattern")
                expected_parent_pattern = rule.get("expected_parent_pattern")

                if name_pattern and re.search(name_pattern, dirname, re.IGNORECASE): # Case-insensitive search
                    if expected_parent_pattern and not re.search(expected_parent_pattern, parent_dir_name, re.IGNORECASE):
                        misplaced_items.append({
                            "type": "folder",
                            "item_path": relative_folder_path,
                            "item_name": dirname,
                            "current_parent": parent_dir_name,
                            "expected_parent_pattern": expected_parent_pattern,
                            "reason": rule.get("description", "No specific description provided.")
                        })
                        logger.warning(f"Misplaced folder: {relative_folder_path}. Reason: {rule.get('description', 'Rule mismatch.')}")
                        break # Only report once per folder for the first matching rule

        # Check files
        for filename in filenames:
            full_file_path = os.path.join(dirpath, filename)
            relative_file_path = os.path.relpath(full_file_path, root_dir)
            file_extension = os.path.splitext(filename)[1].lower()

            for rule in file_rules:
                rule_matched = False
                
                # Check by extension
                if rule.get("extension") and file_extension == rule["extension"]:
                    rule_matched = True
                # Check by name pattern
                elif rule.get("name_pattern") and re.search(rule["name_pattern"], filename, re.IGNORECASE):
                    rule_matched = True
                
                if rule_matched:
                    expected_parent_pattern = rule.get("expected_parent_pattern")
                    if expected_parent_pattern and not re.search(expected_parent_pattern, parent_dir_name, re.IGNORECASE):
                        misplaced_items.append({
                            "type": "file",
                            "item_path": relative_file_path,
                            "item_name": filename,
                            "current_parent": parent_dir_name,
                            "expected_parent_pattern": expected_parent_pattern,
                            "reason": rule.get("description", "No specific description provided.")
                        })
                        logger.warning(f"Misplaced file: {relative_file_path}. Reason: {rule.get('description', 'Rule mismatch.')}")
                        break # Only report once per file for the first matching rule

    return misplaced_items
