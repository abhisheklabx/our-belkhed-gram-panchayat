/**
 * Voice Typing Engine for Our Belkhed
 * Supports Marathi (mr-IN), Hindi (hi-IN), and English (en-IN).
 */

class BelkhedVoiceTyping {
  constructor() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.hasSupport = !!SpeechRecognition;
    this.recognition = this.hasSupport ? new SpeechRecognition() : null;
    this.isRecording = false;
    this.activeInput = null;
    this.activeButton = null;

    if (this.hasSupport) {
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.initEvents();
    }
  }

  getLocale() {
    const lang = document.documentElement.lang || 'mr';
    if (lang === 'mr') return 'mr-IN';
    if (lang === 'hi') return 'hi-IN';
    return 'en-IN';
  }

  initEvents() {
    this.recognition.onstart = () => {
      this.isRecording = true;
      if (this.activeButton) {
        this.activeButton.classList.add('recording');
        this.activeButton.innerHTML = '<i class="bi bi-mic-fill"></i> ऐकत आहे... (Listening)';
      }
    };

    this.recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      if (this.activeInput) {
        this.activeInput.value = transcript;
        this.activeInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
    };

    this.recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      this.stop();
      if (event.error === 'not-allowed') {
        alert("मायक्रोफोन परवानगी नाकारली गेली आहे. कृपया ब्राउझरमध्ये मायक्रोफोन परवानगी सुरू करा. (Microphone permission denied)");
      }
    };

    this.recognition.onend = () => {
      this.stop();
    };
  }

  toggle(targetInputId, triggerBtn) {
    if (!this.hasSupport) {
      alert("आपल्या ब्राउझरमध्ये आवाज टायपिंग (Speech Recognition) समर्थित नाही. कृपया क्रोम किंवा एज वापरा. (Browser speech typing not supported, please type manually)");
      return;
    }

    const inputEl = document.getElementById(targetInputId);
    if (!inputEl) return;

    if (this.isRecording) {
      this.recognition.stop();
      this.stop();
    } else {
      this.activeInput = inputEl;
      this.activeButton = triggerBtn;
      this.recognition.lang = this.getLocale();
      try {
        this.recognition.start();
      } catch (err) {
        console.error("Failed to start voice recognition:", err);
      }
    }
  }

  stop() {
    this.isRecording = false;
    if (this.activeButton) {
      this.activeButton.classList.remove('recording');
      this.activeButton.innerHTML = '<i class="bi bi-mic"></i> बोलून लिहा';
      this.activeButton = null;
    }
    this.activeInput = null;
  }
}

// Global instance
window.voiceTyping = new BelkhedVoiceTyping();
