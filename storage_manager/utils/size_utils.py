"""Utilities for handling file sizes and calculations."""

import os
from tqdm import tqdm

def get_directory_size(path):
    """Calculate the total size of a directory."""
    total_size = 0
    files = []
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            files.append(fp)
    
    with tqdm(total=len(files), desc=f"Calculating size of {os.path.basename(path)}", unit="files") as pbar:
        for fp in files:
            try:
                total_size += os.path.getsize(fp)
                pbar.update(1)
            except (OSError, FileNotFoundError):
                continue
    return total_size

def format_size(size):
    """Format size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"
