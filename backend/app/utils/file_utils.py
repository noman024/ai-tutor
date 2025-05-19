import os
import string
import random
from datetime import datetime

def generate_short_id(length: int = 6) -> str:
    """Generate a short unique identifier using alphanumeric characters."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_unique_filename(original_filename: str, length: int = 6) -> str:
    """
    Generate a unique filename that preserves the original name with a short unique identifier.
    Format: original_name_shortid.ext
    """
    name, ext = os.path.splitext(original_filename)
    # Remove any special characters from the original name
    safe_name = ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
    # Replace spaces with underscores and limit length
    safe_name = safe_name.replace(' ', '_')[:30]
    # Add timestamp to ensure uniqueness even with same original name
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    short_id = generate_short_id(length)
    return f"{safe_name}_{timestamp}_{short_id}{ext}" 