import re

# Simple NLP-like keyword extraction and synonym mapping
# This avoids large spaCy downloads for easy local setup, relying on regex and a dictionary.

SYNONYMS = {
    'coding': 'programming',
    'developer': 'programming',
    'python': 'python',
    'js': 'javascript',
    'web design': 'html css',
    'ui/ux': 'graphic design',
    'teaching': 'public speaking',
    'mentoring': 'public speaking',
    'analytics': 'data analysis',
    'statistics': 'data analysis',
    'machine learning': 'machine learning',
    'ai': 'machine learning',
    'writing': 'content writing',
    'blogging': 'content writing',
    'pr': 'marketing',
    'advertising': 'marketing'
}

def extract_keywords(text):
    """
    Extracts potential skill keywords from a block of text.
    Replaces known synonyms with standard skill names.
    """
    if not text:
        return []
        
    text = text.lower()
    
    # Remove basic punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    
    extracted = []
    
    # Check for multi-word synonyms first
    for syn, standard in SYNONYMS.items():
        if f" {syn} " in f" {text} ":
            extracted.extend(standard.split())
            
    # Also just tokenize and look for exact matches in our known skills
    # Since recommender.py merges this with explicit skills, TF-IDF will handle the weighting
    words = text.split()
    for word in words:
        if word in SYNONYMS:
            extracted.extend(SYNONYMS[word].split())
        elif len(word) > 3: # Keep longer words as potential context for TF-IDF
            extracted.append(word)
            
    return list(set(extracted))
