/**
 * Belkhed Assistant (बेलखेड सहाय्यक) Frontend Widget
 */

document.addEventListener('DOMContentLoaded', () => {
  const triggerBtn = document.getElementById('assistantTriggerBtn');
  const modal = document.getElementById('assistantModal');
  const closeBtn = document.getElementById('assistantCloseBtn');
  const sendBtn = document.getElementById('assistantSendBtn');
  const input = document.getElementById('assistantInput');
  const messagesBox = document.getElementById('assistantMessages');
  const ttsBtn = document.getElementById('assistantTtsBtn');

  if (!triggerBtn || !modal) return;

  triggerBtn.addEventListener('click', () => {
    const isVisible = modal.style.display === 'flex';
    modal.style.display = isVisible ? 'none' : 'flex';
    if (!isVisible) {
      input.focus();
    }
  });

  closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
  });

  const appendMessage = (text, sender, meta) => {
    const div = document.createElement('div');
    div.className = `chat-bubble ${sender}`;
    div.innerHTML = `<div>${text}</div>`;
    if (meta) {
      const metaSpan = document.createElement('div');
      metaSpan.className = 'chat-meta';
      metaSpan.textContent = meta;
      div.appendChild(metaSpan);
    }
    messagesBox.appendChild(div);
    messagesBox.scrollTop = messagesBox.scrollHeight;
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      const curLang = document.documentElement.lang || 'mr';
      utterance.lang = curLang === 'mr' ? 'mr-IN' : (curLang === 'hi' ? 'hi-IN' : 'en-IN');
      window.speechSynthesis.speak(utterance);
    }
  };

  const sendMessage = async () => {
    const text = input.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    input.value = '';

    // Typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-bubble bot';
    typingDiv.id = 'assistantTyping';
    typingDiv.innerHTML = '<em>बेलखेड सहाय्यक उत्तर लिहीत आहे... (Typing...)</em>';
    messagesBox.appendChild(typingDiv);
    messagesBox.scrollTop = messagesBox.scrollHeight;

    try {
      const lang = document.documentElement.lang || 'mr';
      const res = await fetch('/api/assistant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, lang: lang })
      });
      const data = await res.json();

      const typingEl = document.getElementById('assistantTyping');
      if (typingEl) typingEl.remove();

      if (data.success) {
        appendMessage(data.response, 'bot', data.source);
        // Optional voice readout button on response
        speakText(data.response);
      } else {
        appendMessage("क्षमस्व, सध्या सहाय्यक सेवा उपलब्ध नाही. कृपया थोड्या वेळाने प्रयत्न करा.", 'bot');
      }
    } catch (err) {
      console.error("Assistant chat error:", err);
      const typingEl = document.getElementById('assistantTyping');
      if (typingEl) typingEl.remove();
      appendMessage("नेटवर्क त्रुटी! कृपया इंटरनेट कनेक्शन तपासा.", 'bot');
    }
  };

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
});
