# 🤖 FAQ Chatbot

A smart FAQ chatbot built with **FastAPI**, **NLTK**, and **TF-IDF cosine similarity**. It preprocesses user questions using NLP techniques and matches them to the most relevant FAQ answer.

## ✨ Features

- ✅ NLP preprocessing with NLTK (tokenize, clean, lemmatize, stopword removal)
- ✅ TF-IDF vectorization + Cosine Similarity matching
- ✅ 25+ FAQs on tech product support
- ✅ Beautiful chat UI with sidebar FAQ browser
- ✅ Typing indicator and confidence score display
- ✅ FastAPI backend with Uvicorn server

## 📁 Project Structure

```
faq-chatbot/
│
├── main.py           # FastAPI app + routes
├── nlp.py            # NLP preprocessing + matching engine
├── faqs.py           # FAQ dataset
├── requirements.txt
├── .gitignore
├── README.md
│
└── static/
    ├── index.html    # Chat UI
    ├── style.css     # Styles
    └── app.js        # Frontend logic
```

## 🚀 Setup & Run

### 1. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the server
```bash
uvicorn main:app --reload
```

### 4. Open in browser
```
http://localhost:8000
```

## 🧠 How It Works

1. **User types a question**
2. **NLTK preprocesses it** — lowercase, remove special chars, tokenize, remove stopwords, lemmatize
3. **TF-IDF vectorizer** converts the question into a vector
4. **Cosine similarity** compares it against all FAQ vectors
5. **Best matching FAQ** answer is returned with a confidence score

## 🛠️ Built With

- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [NLTK](https://www.nltk.org/)
- [Scikit-learn](https://scikit-learn.org/)

## 📄 License

MIT
