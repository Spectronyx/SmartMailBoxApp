import re
import bleach
import logging

logger = logging.getLogger(__name__)

def preprocess_for_ai(text: str) -> str:
    """
    Cleans text content before sending it to an LLM (Gemini).
    
    1. Removes all HTML tags if text is HTML.
    2. Simplifies whitespace (multiple spaces/newlines).
    3. Handles long sequences of dashes/special characters.
    4. Truncates content if excessively long.
    """
    if not text:
        return ""

    # 0. Unescape HTML entities first (e.g., &lt;div&gt; -> <div>)
    # This ensures bleach sees them as tags and can strip them.
    import html
    text = html.unescape(text)
    
    # 0.1 Remove <style> and <script> tags AND their content entirely
    text = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # 1. Strip all other HTML tags using bleach (no tags allowed)
    cleaned_text = bleach.clean(
        text, 
        tags=[], 
        attributes={}, 
        strip=True
    )
    
    # Remove &nbsp; and other HTML entities if lingering
    cleaned_text = re.sub(r'&[a-z0-9#]+;', ' ', cleaned_text, flags=re.IGNORECASE)

    # 2. Normalize whitespace
    # Replace multiple spaces with single space
    cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
    # Replace more than 2 newlines with exactly 2
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # 3. Clean common email separator noise (e.g., -----------)
    cleaned_text = re.sub(r'[-=]{5,}', '-', cleaned_text)
    
    # 4. Strip leading/trailing whitespace
    cleaned_text = cleaned_text.strip()
    
    # 5. Final safety truncation (10k chars is plenty for most email context)
    return cleaned_text[:10000]

def decode_headers(header_value: str) -> str:
    """
    Decodes RFC 2047 encoded email headers (e.g., =?utf-8?B?...) 
    into plain unicode strings.
    """
    if not header_value:
        return ""
    
    from email.header import decode_header, make_header
    try:
        # make_header handles multiple fragments and various encodings automatically
        return str(make_header(decode_header(header_value)))
    except Exception:
        # Fallback to original string if decoding fails
        return str(header_value)
