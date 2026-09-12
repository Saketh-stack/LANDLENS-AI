import re

LANGUAGE_CODES = {
    'en': 'English',
    'hi': 'Hindi',
    'te': 'Telugu',
    'ta': 'Tamil',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'bn': 'Bengali',
    'kn': 'Kannada',
    'ml': 'Malayalam'
}

def detect_text_script(text: str) -> str:
    # Unicode range checks for Indian scripts
    if re.search(r'[ऀ-ॿ]', text):
        return 'Hindi / Marathi (Devanagari)'
    elif re.search(r'[ఀ-౿]', text):
        return 'Telugu'
    elif re.search(r'[஀-௿]', text):
        return 'Tamil'
    elif re.search(r'[઀-૿]', text):
        return 'Gujarati'
    elif re.search(r'[ঀ-৿]', text):
        return 'Bengali'
    elif re.search(r'[ಀ-೿]', text):
        return 'Kannada'
    elif re.search(r'[ഀ-ൿ]', text):
        return 'Malayalam'
    return 'English'
