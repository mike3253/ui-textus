import os
import hashlib
import logging

logger = logging.getLogger(__name__)

def find_duplicate_folders_by_name(root_dir):
    """Finds folders with duplicate names within the same parent directory."""
    duplicate_folders = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        seen_dirnames = set()
        for dirname in dirnames:
            if dirname in seen_dirnames:
                parent_path = os.path.relpath(dirpath, root_dir)
                if parent_path not in duplicate_folders:
                    duplicate_folders[parent_path] = []
                duplicate_folders[parent_path].append(dirname)
                logger.debug(f"Found name duplicate: {dirname} in {parent_path}")
            seen_dirnames.add(dirname)
    return duplicate_folders

def get_folder_content_hash(folder_path):
    """Generates a hash based on the names and hashes of all files within a folder."""
    hasher = hashlib.sha256()
    file_info = []
    
    # Check if folder_path exists and is a directory
    if not os.path.isdir(folder_path):
        logger.warning(f"Path is not a directory or does not exist: {folder_path}. Cannot generate content hash.")
        return None # Or raise an error, depending on desired behavior

    for root, dirs, files in os.walk(folder_path):
        files.sort()
        dirs.sort()
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'rb') as f:
                    file_hasher = hashlib.sha256()
                    while chunk := f.read(4096):
                        file_hasher.update(chunk)
                relative_path = os.path.relpath(filepath, folder_path)
                file_info.append(f"{relative_path}:{file_hasher.hexdigest()}")
            except (IOError, OSError) as e:
                logger.error(f"Error reading file {filepath} for hashing: {e}")
                file_info.append(f"{os.path.relpath(filepath, folder_path)}:ERROR")
    file_info.sort()
    for info in file_info:
        hasher.update(info.encode('utf-8'))
    return hasher.hexdigest()

def find_duplicate_folders_by_content(root_dir):
    """Finds folders with identical content (based on file names and hashes)."""
    folder_hashes = {}
    duplicate_content_folders = {}
    
    # Check if root_dir exists and is a directory
    if not os.path.isdir(root_dir):
        logger.error(f"Root directory for content duplicate check does not exist or is not a directory: {root_dir}")
        return {}

    for dirpath, dirnames, _ in os.walk(root_dir):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            try:
                content_hash = get_folder_content_hash(full_path)
                if content_hash is None: # Handle cases where hashing failed for a folder
                    logger.warning(f"Skipping folder {full_path} for content duplicate check due to hashing error.")
                    continue
                
                if content_hash in folder_hashes:
                    # Ensure the list exists for this hash
                    if content_hash not in duplicate_content_folders:
                        duplicate_content_folders[content_hash] = [folder_hashes[content_hash]]
                    duplicate_content_folders[content_hash].append(full_path)
                    logger.debug(f"Found content duplicate: {full_path} with hash {content_hash}")
                else:
                    folder_hashes[content_hash] = full_path
            except Exception as e:
                logger.error(f"Error processing folder {full_path} for content duplicate check: {e}")
    return duplicate_content_folders
