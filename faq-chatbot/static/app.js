// ── DOM Refs ─────────────────────────────────────────────────────────────────
const messages  = document.getElementById("messages");
const userInput = document.getElementById("userInput");
const sendBtn   = document.getElementById("sendBtn");
const clearBtn  = document.getElementById("clearBtn");
const faqList   = document.getElementById("faqList");

// ── Load FAQs into sidebar ────────────────────────────────────────────────────
async function loadFAQs() {
  try {
    const res  = await fetch("/faqs");
    const faqs = await res.json();
    faqList.innerHTML = "";
    faqs.forEach(faq => {
      const item = document.createElement("div");
      item.className   = "faq-item";
      item.textContent = faq.question;
      item.addEventListener("click", () => {
        userInput.value = faq.question;
        userInput.focus();
      });
      faqList.appendChild(item);
    });
  } catch {
    faqList.innerHTML = '<p class="loading-text">Could not load FAQs.</p>';
  }
}

loadFAQs();

// ── Add message to chat ────────────────────────────────────────────────────────
function addMessage(role, content, extra = {}) {
  const wrap = document.createElement("div");
  wrap.className = `message ${role}`;

  const avatarIcon = role === "bot"
    ? '<i class="fa-solid fa-robot"></i>'
    : '<i class="fa-solid fa-user"></i>';

  let bubbleContent = content;

  if (role === "bot" && extra.confidence !== undefined && extra.matched) {
    bubbleContent += `
      <div class="matched-q">Matched: "${extra.question}"</div>
      <span class="confidence-tag">
        <i class="fa-solid fa-check-circle"></i> ${extra.confidence}% match
      </span>`;
  }

  wrap.innerHTML = `
    <div class="avatar-sm">${avatarIcon}</div>
    <div class="bubble">${bubbleContent}</div>`;

  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
  return wrap;
}

// ── Typing indicator ───────────────────────────────────────────────────────────
function showTyping() {
  const wrap = document.createElement("div");
  wrap.className = "message bot typing";
  wrap.id        = "typing";
  wrap.innerHTML = `
    <div class="avatar-sm"><i class="fa-solid fa-robot"></i></div>
    <div class="bubble">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>`;
  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
}

function hideTyping() {
  const t = document.getElementById("typing");
  if (t) t.remove();
}

// ── Send message ───────────────────────────────────────────────────────────────
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  // Show user message
  addMessage("user", text);
  userInput.value = "";
  sendBtn.disabled = true;

  // Show typing
  showTyping();

  try {
    const res  = await fetch("/chat", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ message: text })
    });

    const data = await res.json();
    hideTyping();

    addMessage("bot", data.answer, {
      question:   data.question,
      confidence: data.confidence,
      matched:    data.matched
    });

  } catch (err) {
    hideTyping();
    addMessage("bot", "Sorry, something went wrong. Please try again.");
  } finally {
    sendBtn.disabled = false;
    userInput.focus();
  }
}

// ── Event listeners ────────────────────────────────────────────────────────────
sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

clearBtn.addEventListener("click", () => {
  messages.innerHTML = `
    <div class="message bot">
      <div class="avatar-sm"><i class="fa-solid fa-robot"></i></div>
      <div class="bubble">
        👋 Hi! I'm your FAQ Assistant. Ask me any question and I'll find the best answer for you!
        <br/><br/>
        Try asking: <em>"How do I reset my password?"</em>
      </div>
    </div>`;
});
