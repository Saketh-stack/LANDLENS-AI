import os
import uuid
import re
from typing import Tuple

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tif', 'tiff'}
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB limit

def sanitize_filename(filename: str) -> str:
    # Remove paths and unsafe characters
    base = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', base)
    return clean

def generate_secure_filename(original_filename: str) -> Tuple[str, str]:
    clean_name = sanitize_filename(original_filename)
    ext = clean_name.split('.')[-1].lower() if '.' in clean_name else 'bin'
    unique_id = uuid.uuid4().hex[:12]
    secure_name = f'{unique_id}_{clean_name}'
    return secure_name, ext

def validate_file_metadata(filename: str, file_size: int) -> Tuple[bool, str]:
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f'File exceeds maximum allowed size of 25MB (got {file_size / (1024*1024):.2f}MB)'
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return False, f'Unsupported file format .{ext}. Allowed: {list(ALLOWED_EXTENSIONS)}'
    return True, 'Valid'
