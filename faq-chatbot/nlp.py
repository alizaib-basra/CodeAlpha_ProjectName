"""
NLP Engine
===========
- Preprocesses text using NLTK (tokenize, clean, lemmatize)
- Matches user questions to FAQs using TF-IDF + Cosine Similarity
"""

import re
import nltk
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from faqs import FAQS

# ── Download NLTK data ───────────────────────────────────────────────────────
nltk.download("punkt",        quiet=True)
nltk.download("punkt_tab",    quiet=True)
nltk.download("stopwords",    quiet=True)
nltk.download("wordnet",      quiet=True)
nltk.download("omw-1.4",      quiet=True)

# ── Setup ────────────────────────────────────────────────────────────────────
lemmatizer  = WordNetLemmatizer()
stop_words  = set(stopwords.words("english"))

# ── Preprocess text ──────────────────────────────────────────────────────────
def preprocess(text: str) -> str:
    """
    Clean and normalize text:
    1. Lowercase
    2. Remove special characters
    3. Tokenize
    4. Remove stopwords
    5. Lemmatize
    """
    text   = text.lower()
    text   = re.sub(r"[^a-z0-9\s]", "", text)
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words]
    return " ".join(tokens)

# ── Build TF-IDF Matrix from FAQs ────────────────────────────────────────────
faq_questions    = [faq["question"] for faq in FAQS]
faq_answers      = [faq["answer"]   for faq in FAQS]
processed_faqs   = [preprocess(q)   for q in faq_questions]

vectorizer       = TfidfVectorizer()
tfidf_matrix     = vectorizer.fit_transform(processed_faqs)

# ── Match user question ───────────────────────────────────────────────────────
def get_best_match(user_question: str, threshold: float = 0.15):
    """
    Find the most similar FAQ to the user's question.
    Returns the answer and confidence score.
    """
    processed_q   = preprocess(user_question)
    user_vector   = vectorizer.transform([processed_q])
    similarities  = cosine_similarity(user_vector, tfidf_matrix).flatten()
    best_idx      = np.argmax(similarities)
    best_score    = similarities[best_idx]

    if best_score < threshold:
        return {
            "question":   None,
            "answer":     "I'm sorry, I couldn't find a matching answer to your question. Please try rephrasing or contact our support team at support@example.com.",
            "confidence": round(float(best_score) * 100, 1),
            "matched":    False
        }

    return {
        "question":   faq_questions[best_idx],
        "answer":     faq_answers[best_idx],
        "confidence": round(float(best_score) * 100, 1),
        "matched":    True
    }


def get_all_faqs():
    """Return all FAQs for display."""
    return [{"question": q, "answer": a} for q, a in zip(faq_questions, faq_answers)]
