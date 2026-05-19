import os
import tempfile

def get_temp_file(suffix=".tmp"):
    """
    Returns a path for a temporary file with the given suffix.
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path
