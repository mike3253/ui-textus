import os
import logging

logger = logging.getLogger(__name__)

def find_empty_folders(root_dir):
    """
    Finds empty folders (no files, no subfolders) within a root directory.
    Returns a list of relative paths to empty folders.
    """
    empty_folders = []
    # Walk from the bottom up (topdown=False) ensures we detect truly empty folders
    # after their children have been processed.
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Skip the root directory itself if it's the only thing left
        if dirpath == root_dir and not dirnames and not filenames:
            continue
        
        # Check if both dirnames (subfolders) and filenames are empty
        if not dirnames and not filenames:
            empty_folders.append(os.path.relpath(dirpath, root_dir))
    return empty_folders

def clean_empty_folders(root_dir, auto_delete=False):
    """
    Identifies empty folders and optionally deletes them.
    Returns a tuple: (list of empty folders found, list of folders attempted to delete)
    """
    logger.info(f"Scanning for empty folders in: {root_dir}")
    empty_folders_found = []
    deleted_folders = []

    # Walk from the bottom up to ensure a parent folder is truly empty after its children are checked/deleted
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Skip the root directory itself to prevent deleting the whole tree if empty
        if dirpath == root_dir:
            continue

        if not dirnames and not filenames: # If current folder has no subdirs and no files
            relative_path = os.path.relpath(dirpath, root_dir)
            empty_folders_found.append(relative_path)
            
            if auto_delete:
                try:
                    os.rmdir(dirpath)
                    deleted_folders.append(relative_path)
                    logger.info(f"Successfully deleted empty folder: {relative_path}")
                except OSError as e:
                    logger.error(f"Error deleting empty folder {relative_path}: {e}")
            else:
                logger.info(f"Identified empty folder (not deleted): {relative_path}")
    
    return empty_folders_found, deleted_folders
