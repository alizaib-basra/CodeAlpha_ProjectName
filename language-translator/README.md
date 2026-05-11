# 🌐 LinguaTranslate

A clean, full-featured **Language Translation Web App** built with HTML, CSS, and JavaScript — powered by the Claude AI API.

## ✨ Features

- **25+ languages** supported including English, Urdu, Arabic, French, Spanish, Chinese, Japanese, and more
- **Auto language detection** — detects what language you typed automatically
- **Swap languages** — flip source and target with one click
- **Translation History** — all translations saved locally (persists across sessions)
- **Favorites** — star and save translations you want to keep
- **Copy to clipboard** — one-click copy of translation
- **Text to Speech** — listen to the translated text out loud
- **Keyboard shortcut** — `Ctrl + Enter` to translate fast
- **Word & character counter** on both panels
- **Responsive design** — works on mobile and desktop

## 📁 Project Structure

```
language-translator/
│
├── index.html          # Main HTML page
├── css/
│   └── style.css       # All styles
├── js/
│   └── app.js          # All JavaScript logic
└── README.md
```

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/language-translator.git
cd language-translator
```

### 2. Add your API Key
Open `js/app.js` and replace the placeholder:
```js
const API_KEY = "YOUR_ANTHROPIC_API_KEY_HERE";
```
Get your key at: https://console.anthropic.com

### 3. Run it
- **With XAMPP:** Copy the folder to `C:\xampp\htdocs\` and open `http://localhost/language-translator/`
- **Without a server:** Just open `index.html` directly in your browser

> ⚠️ **Note:** The API key is exposed in the browser for this project. For production, move the API call to a backend (PHP, Node.js, etc.)

## 🛠️ Built With

- HTML5 / CSS3 / Vanilla JavaScript
- [Claude AI API](https://www.anthropic.com) — for translations
- [Font Awesome 6](https://fontawesome.com) — for icons

## 📸 Screenshot

> Add a screenshot of the app here

## 📄 License

MIT — free to use and modify.
