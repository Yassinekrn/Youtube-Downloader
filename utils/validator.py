import re
import os

def sanitize_filename(filename: str) -> str:
    """
    Removes invalid characters from a filename and trims unnecessary spaces.
    :param filename: Original filename.
    :return: Sanitized filename.
    """
    # Replace invalid characters with an underscore
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return sanitized.strip()


def get_available_filename(directory: str, filename: str) -> str:
    """
    Ensures the filename is unique by appending a number if needed.
    :param directory: Directory where the file will be saved.
    :param filename: Desired filename.
    :return: A unique filename.
    """
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_filename = filename

    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base}({counter}){ext}"
        counter += 1

    return unique_filename
