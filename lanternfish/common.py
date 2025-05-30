import os

def clear_folder(folder):
    """
    Delete all contents of the specified folder.

    This function removes all files, symbolic links, and subdirectories 
    within the given folder. If the folder does not exist, nothing is done.

    Args:
        folder (str): Path to the folder whose contents should be cleared.

    Raises:
        Prints an error message if any file or directory could not be deleted.
    """
    
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
