// ─────────────────────────────────────────
//  LinguaTranslate · app.js
//  Translation powered by MyMemory API
//  No API key needed — works out of the box!
// ─────────────────────────────────────────

// ── MyMemory language codes ──────────────
const LANG_CODES = {
  "English":              "en",
  "Urdu":                 "ur",
  "Arabic":               "ar",
  "French":               "fr",
  "Spanish":              "es",
  "German":               "de",
  "Chinese (Simplified)": "zh",
  "Chinese (Traditional)":"zh",
  "Japanese":             "ja",
  "Korean":               "ko",
  "Hindi":                "hi",
  "Portuguese":           "pt",
  "Russian":              "ru",
  "Italian":              "it",
  "Dutch":                "nl",
  "Turkish":              "tr",
  "Polish":               "pl",
  "Swedish":              "sv",
  "Greek":                "el",
  "Hebrew":               "he",
  "Persian":              "fa",
  "Indonesian":           "id",
  "Thai":                 "th",
  "Vietnamese":           "vi",
  "Bengali":              "bn",
  "Punjabi":              "pa"
};

// ── DOM REFS ────────────────────────────
const sourceText     = document.getElementById("sourceText");
const outputText     = document.getElementById("outputText");
const sourceLang     = document.getElementById("sourceLang");
const targetLang     = document.getElementById("targetLang");
const translateBtn   = document.getElementById("translateBtn");
const copyBtn        = document.getElementById("copyBtn");
const speakBtn       = document.getElementById("speakBtn");
const clearBtn       = document.getElementById("clearBtn");
const swapBtn        = document.getElementById("swapBtn");
const favBtn         = document.getElementById("favBtn");
const detectBadge    = document.getElementById("detectBadge");
const charCount      = document.getElementById("charCount");
const wordCount      = document.getElementById("wordCount");
const transWordCount = document.getElementById("transWordCount");
const errorMsg       = document.getElementById("errorMsg");
const historyList    = document.getElementById("historyList");
const favList        = document.getElementById("favList");

// ── STATE ───────────────────────────────
let translatedText = "";
let isSpeaking     = false;
let history        = JSON.parse(localStorage.getItem("lt_history")   || "[]");
let favorites      = JSON.parse(localStorage.getItem("lt_favorites") || "[]");

// ── HELPERS ─────────────────────────────
function countWords(text) {
  return text.trim() ? text.trim().split(/\s+/).length : 0;
}

function timeAgo(timestamp) {
  const s = Math.floor((Date.now() - timestamp) / 1000);
  if (s < 60)    return "just now";
  if (s < 3600)  return Math.floor(s / 60) + "m ago";
  if (s < 86400) return Math.floor(s / 3600) + "h ago";
  return Math.floor(s / 86400) + "d ago";
}

function saveHistory()   { localStorage.setItem("lt_history",   JSON.stringify(history));   }
function saveFavorites() { localStorage.setItem("lt_favorites", JSON.stringify(favorites)); }

function setOutput(text) {
  outputText.textContent = text;
  translatedText = text;
  transWordCount.textContent = countWords(text) + " words";
}

function resetOutput() {
  outputText.innerHTML = '<span class="placeholder-text">Translation appears here...</span>';
  translatedText = "";
  transWordCount.textContent = "";
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.add("visible");
}

function hideError() {
  errorMsg.classList.remove("visible");
}

function escapeHTML(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ── TABS ────────────────────────────────
document.querySelectorAll(".tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".panel-wrap").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    if (btn.dataset.tab === "history")   renderHistory();
    if (btn.dataset.tab === "favorites") renderFavs();
  });
});

// ── SOURCE TEXT EVENTS ──────────────────
sourceText.addEventListener("input", () => {
  const val = sourceText.value;
  charCount.textContent = val.length + " / 2000";
  wordCount.textContent = countWords(val) + " words";
});

sourceText.addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    translateBtn.click();
  }
});

// ── CLEAR ───────────────────────────────
clearBtn.addEventListener("click", () => {
  sourceText.value = "";
  charCount.textContent = "0 / 2000";
  wordCount.textContent = "0 words";
  resetOutput();
  hideError();
  detectBadge.classList.remove("visible");
  detectBadge.textContent = "";
  favBtn.classList.remove("starred");
  favBtn.innerHTML = '<i class="fa-regular fa-star"></i>';
  if (isSpeaking) { window.speechSynthesis.cancel(); isSpeaking = false; }
});

// ── SWAP LANGUAGES ──────────────────────
swapBtn.addEventListener("click", () => {
  swapBtn.classList.add("spin");
  setTimeout(() => swapBtn.classList.remove("spin"), 400);

  const sv = sourceLang.value;
  const tv = targetLang.value;

  if (sv !== "auto") {
    const inTarget = [...targetLang.options].some(o => o.value === sv);
    const inSource = [...sourceLang.options].some(o => o.value === tv);
    if (inTarget && inSource) {
      sourceLang.value = tv;
      targetLang.value = sv;
    }
  }

  if (translatedText) {
    const tmp = sourceText.value;
    sourceText.value = translatedText;
    charCount.textContent = sourceText.value.length + " / 2000";
    wordCount.textContent = countWords(sourceText.value) + " words";
    setOutput(tmp);
  }
});

// ── TRANSLATE — MyMemory API ─────────────
translateBtn.addEventListener("click", async () => {
  const text = sourceText.value.trim();
  if (!text) return;

  const srcName = sourceLang.value;
  const tgtName = targetLang.value;
  const srcCode = srcName === "auto" ? "autodetect" : LANG_CODES[srcName];
  const tgtCode = LANG_CODES[tgtName];

  if (!tgtCode) { showError("Target language not supported."); return; }

  // Build MyMemory URL
  // Format: https://api.mymemory.translated.net/get?q=TEXT&langpair=en|fr
  const langPair = `${srcCode}|${tgtCode}`;
  const apiUrl   = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${langPair}`;

  // Loading state
  translateBtn.disabled = true;
  translateBtn.innerHTML = '<div class="spinner"></div> Translating...';
  hideError();
  resetOutput();
  detectBadge.classList.remove("visible");
  favBtn.classList.remove("starred");
  favBtn.innerHTML = '<i class="fa-regular fa-star"></i>';

  try {
    const response = await fetch(apiUrl);
    const data     = await response.json();

    // MyMemory returns responseStatus 200 on success
    if (data.responseStatus !== 200) {
      throw new Error(data.responseMessage || "Translation failed.");
    }

    const result   = data.responseData.translatedText;
    const detected = data.responseData.detectedLanguage || null;

    if (!result) throw new Error("No translation returned.");

    setOutput(result);

    // Show detected language if auto mode
    if (srcName === "auto" && detected) {
      detectBadge.textContent = "Detected: " + detected;
      detectBadge.classList.add("visible");
    }

    // Save to history
    const entry = {
      src:     text,
      tgt:     result,
      srcLang: srcName === "auto" ? (detected || "Auto") : srcName,
      tgtLang: tgtName,
      ts:      Date.now()
    };
    history.unshift(entry);
    if (history.length > 50) history.pop();
    saveHistory();

  } catch (err) {
    showError("Translation failed: " + err.message);
    resetOutput();
  } finally {
    translateBtn.disabled = false;
    translateBtn.innerHTML = '<i class="fa-solid fa-language"></i> <span>Translate</span>';
  }
});

// ── COPY ────────────────────────────────
copyBtn.addEventListener("click", () => {
  if (!translatedText) return;
  navigator.clipboard.writeText(translatedText).then(() => {
    copyBtn.classList.add("success");
    copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
    setTimeout(() => {
      copyBtn.classList.remove("success");
      copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy';
    }, 2000);
  });
});

// ── TEXT TO SPEECH ───────────────────────
speakBtn.addEventListener("click", () => {
  if (!translatedText) return;

  if (isSpeaking) {
    window.speechSynthesis.cancel();
    isSpeaking = false;
    speakBtn.classList.remove("speaking");
    speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Listen';
    return;
  }

  const utterance = new SpeechSynthesisUtterance(translatedText);
  isSpeaking = true;
  speakBtn.classList.add("speaking");
  speakBtn.innerHTML = '<i class="fa-solid fa-stop"></i> Stop';

  utterance.onend = () => {
    isSpeaking = false;
    speakBtn.classList.remove("speaking");
    speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Listen';
  };

  window.speechSynthesis.speak(utterance);
});

// ── FAVORITES ───────────────────────────
favBtn.addEventListener("click", () => {
  if (!translatedText) return;

  const entry = {
    src:     sourceText.value.trim(),
    tgt:     translatedText,
    srcLang: sourceLang.value === "auto" ? "Auto" : sourceLang.value,
    tgtLang: targetLang.value,
    ts:      Date.now()
  };

  const idx = favorites.findIndex(f => f.src === entry.src && f.tgt === entry.tgt);

  if (idx > -1) {
    favorites.splice(idx, 1);
    favBtn.classList.remove("starred");
    favBtn.innerHTML = '<i class="fa-regular fa-star"></i>';
  } else {
    favorites.unshift(entry);
    favBtn.classList.add("starred");
    favBtn.innerHTML = '<i class="fa-solid fa-star"></i>';
  }

  saveFavorites();
});

// ── RENDER HISTORY ───────────────────────
function renderHistory() {
  historyList.innerHTML = "";
  if (!history.length) {
    historyList.innerHTML = `
      <div class="empty-state">
        <i class="fa-solid fa-clock-rotate-left"></i>
        <p>No translations yet</p>
      </div>`;
    return;
  }
  history.forEach((item, idx) => historyList.appendChild(makeCard(item, false, idx)));
}

// ── RENDER FAVORITES ─────────────────────
function renderFavs() {
  favList.innerHTML = "";
  if (!favorites.length) {
    favList.innerHTML = `
      <div class="empty-state">
        <i class="fa-regular fa-star"></i>
        <p>No saved translations yet</p>
      </div>`;
    return;
  }
  favorites.forEach((item, idx) => favList.appendChild(makeCard(item, true, idx)));
}

// ── MAKE CARD ───────────────────────────
function makeCard(item, isFav, idx) {
  const card = document.createElement("div");
  card.className = "trans-card";

  card.innerHTML = `
    <div class="card-meta">
      <div class="card-langs">
        <span>${item.srcLang}</span>
        <i class="fa-solid fa-arrow-right" style="font-size:.65rem"></i>
        <span>${item.tgtLang}</span>
      </div>
      <span class="card-time">${timeAgo(item.ts)}</span>
    </div>
    <div class="card-src">${escapeHTML(item.src)}</div>
    <div class="card-tgt">${escapeHTML(item.tgt)}</div>
    <div class="card-actions">
      <button class="icon-btn btn-use">
        <i class="fa-solid fa-pencil"></i> Use again
      </button>
      <button class="icon-btn btn-copy">
        <i class="fa-regular fa-copy"></i> Copy
      </button>
      ${isFav
        ? `<button class="icon-btn btn-unfav starred"><i class="fa-solid fa-star"></i> Saved</button>`
        : `<button class="icon-btn btn-savefav"><i class="fa-regular fa-star"></i> Save</button>`
      }
      <button class="icon-btn btn-delete" style="margin-left:auto;color:#ef4444">
        <i class="fa-solid fa-trash"></i>
      </button>
    </div>`;

  card.querySelector(".btn-use").addEventListener("click", () => {
    sourceText.value = item.src;
    charCount.textContent = item.src.length + " / 2000";
    wordCount.textContent = countWords(item.src) + " words";
    if ([...sourceLang.options].some(o => o.value === item.srcLang)) sourceLang.value = item.srcLang;
    if ([...targetLang.options].some(o => o.value === item.tgtLang)) targetLang.value = item.tgtLang;
    document.querySelector('[data-tab="translate"]').click();
  });

  card.querySelector(".btn-copy").addEventListener("click", () => {
    navigator.clipboard.writeText(item.tgt).then(() => {
      const btn = card.querySelector(".btn-copy");
      btn.classList.add("success");
      btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
      setTimeout(() => {
        btn.classList.remove("success");
        btn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy';
      }, 2000);
    });
  });

  const sfBtn = card.querySelector(".btn-savefav");
  if (sfBtn) {
    sfBtn.addEventListener("click", () => {
      if (!favorites.some(f => f.src === item.src && f.tgt === item.tgt)) {
        favorites.unshift({ ...item, ts: Date.now() });
        saveFavorites();
        sfBtn.classList.add("starred");
        sfBtn.innerHTML = '<i class="fa-solid fa-star"></i> Saved';
      }
    });
  }

  const ufBtn = card.querySelector(".btn-unfav");
  if (ufBtn) {
    ufBtn.addEventListener("click", () => {
      favorites.splice(idx, 1);
      saveFavorites();
      renderFavs();
    });
  }

  card.querySelector(".btn-delete").addEventListener("click", () => {
    if (isFav) { favorites.splice(idx, 1); saveFavorites(); renderFavs(); }
    else        { history.splice(idx, 1);   saveHistory();   renderHistory(); }
  });

  return card;
}

// ── CLEAR ALL ───────────────────────────
document.getElementById("clearHistory").addEventListener("click", () => {
  history = []; saveHistory(); renderHistory();
});

document.getElementById("clearFavs").addEventListener("click", () => {
  favorites = []; saveFavorites(); renderFavs();
});
