import os

def remove_apostrophe_from_names(base_dir):
    for root, dirs, files in os.walk(base_dir, topdown=False):
        # Rename files
        for filename in files:
            new_filename = filename.replace("''", "")
            if new_filename != filename:
                os.rename(os.path.join(root, filename), os.path.join(root, new_filename))
        
        # Rename directories
        for dirname in dirs:
            new_dirname = dirname.replace("''", "")
            if new_dirname != dirname:
                os.rename(os.path.join(root, dirname), os.path.join(root, new_dirname))

# Example usage
base_directory = r"J:\otzaria-library\Ben-YehudaToOtzaria\ספרים"
remove_apostrophe_from_names(base_directory)
