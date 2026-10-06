/**
 * SPEED MOI - Microphone & Web Speech API Handler
 * Handles SpeechRecognition lifecycle, interim feedback, full transcript joining,
 * and passes the completed text to parseVoiceInput().
 */

(function() {
  'use strict';

  // Check Web Speech API support
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  let recognition = null;
  let isListening = false;
  let finalTranscript = '';
  let fullTranscriptAccumulated = '';

  // DOM Elements
  const micBtn = document.getElementById('mic-btn');
  const micStatus = document.getElementById('voice-status');
  const langSelect = document.getElementById('voice-lang-select');
  const recognizedBox = document.getElementById('voice-transcript-box');
  const transcriptText = document.getElementById('voice-transcript-text');
  const voiceAlert = document.getElementById('voice-feedback-msg');
  const retryBtn = document.getElementById('voice-retry-btn');

  const inputName = document.getElementById('contributor_name');
  const inputPlace = document.getElementById('native_place');
  const inputAmount = document.getElementById('amount');

  if (!micBtn) return;

  // Initialize SpeechRecognition if available
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
  } else {
    showStatus('Microphone not supported in this browser. Please use Google Chrome or type manually.', 'error');
    if (micBtn) micBtn.disabled = true;
    return;
  }

  // Restore remembered language
  if (langSelect) {
    const savedLang = localStorage.getItem('speed_moi_voice_lang');
    if (savedLang) {
      langSelect.value = savedLang;
    }
  }

  // Helper: map selected language to speech recognition locale
  function getRecognitionLocale() {
    if (!langSelect) return 'en-IN';
    const val = langSelect.value;
    if (val === 'tanglish') return 'en-IN'; // Tanglish uses en-IN recognition
    return val || 'en-IN';
  }

  // Helper: Show status message
  function showStatus(msg, type = 'normal') {
    if (micStatus) {
      micStatus.textContent = msg;
      micStatus.className = `voice-status-badge status-${type}`;
    }
    if (voiceAlert) {
      voiceAlert.textContent = msg;
      voiceAlert.style.display = 'block';
      if (type === 'error') {
        voiceAlert.style.color = 'var(--color-danger)';
        voiceAlert.style.backgroundColor = '#FDF2F2';
      } else if (type === 'success') {
        voiceAlert.style.color = 'var(--color-success)';
        voiceAlert.style.backgroundColor = '#F0FDF4';
      } else {
        voiceAlert.style.color = 'var(--color-burgundy-900)';
        voiceAlert.style.backgroundColor = 'var(--color-ivory-50)';
      }
    }
  }

  function startListening() {
    if (!recognition) return;
    try {
      finalTranscript = '';
      fullTranscriptAccumulated = '';
      recognition.lang = getRecognitionLocale();
      recognition.start();
      isListening = true;
      micBtn.classList.add('mic-active');
      micBtn.innerHTML = '⏹ Stop Listening';
      showStatus('Listening... Speak clearly (e.g. Ramesh Kumar, Salem, 2000 rupees)', 'listening');
      if (recognizedBox) recognizedBox.style.display = 'block';
      if (transcriptText) transcriptText.textContent = 'Listening...';
      if (retryBtn) retryBtn.style.display = 'none';

      // Remove field highlight warnings
      clearHighlights();
    } catch (err) {
      console.warn('SpeechRecognition start error:', err);
      showStatus('Recognition failed. Please try again.', 'error');
      if (retryBtn) retryBtn.style.display = 'inline-block';
    }
  }

  function stopListening() {
    if (!recognition) return;
    try {
      recognition.stop();
    } catch (err) {
      console.warn('SpeechRecognition stop error:', err);
    }
    isListening = false;
    micBtn.classList.remove('mic-active');
    micBtn.innerHTML = '🎤 Voice Input';
  }

  // Speech Recognition Events
  recognition.onstart = function() {
    isListening = true;
    showStatus('Listening...', 'listening');
  };

  recognition.onresult = function(event) {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      const part = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += part + ' ';
      } else {
        interim += part;
      }
    }

    fullTranscriptAccumulated = (finalTranscript + ' ' + interim).trim();

    if (transcriptText) {
      transcriptText.innerHTML = `<strong>Recognized:</strong> ${escapeHtml(finalTranscript)} <span style="opacity: 0.6;">${escapeHtml(interim)}</span>`;
    }
  };

  recognition.onerror = function(event) {
    console.error('SpeechRecognition error:', event.error);
    isListening = false;
    micBtn.classList.remove('mic-active');
    micBtn.innerHTML = '🎤 Voice Input';

    if (event.error === 'not-allowed') {
      showStatus('Microphone permission required. Please allow microphone access in browser settings.', 'error');
    } else if (event.error === 'no-speech') {
      showStatus('Speech not detected. Please tap microphone to try again.', 'error');
      if (retryBtn) retryBtn.style.display = 'inline-block';
    } else {
      showStatus('Recognition failed. Please try again.', 'error');
      if (retryBtn) retryBtn.style.display = 'inline-block';
    }
  };

  recognition.onend = function() {
    isListening = false;
    micBtn.classList.remove('mic-active');
    micBtn.innerHTML = '🎤 Voice Input';

    const speechToProcess = (finalTranscript || fullTranscriptAccumulated).trim();

    if (!speechToProcess) {
      showStatus('Speech not detected.', 'error');
      if (retryBtn) retryBtn.style.display = 'inline-block';
      return;
    }

    showStatus('Processing...', 'normal');

    // Parse transcript using pure function in voice_parser.js
    if (typeof window.parseVoiceInput === 'function') {
      const parsed = window.parseVoiceInput(speechToProcess, langSelect ? langSelect.value : 'en-IN');
      populateFields(parsed);
    } else {
      showStatus('Voice parser module not found. Please review manually.', 'error');
    }
  };

  // Populate parsed details into the form
  function populateFields(parsed) {
    let missingFields = [];

    // Contributor Name
    if (parsed.name && inputName) {
      inputName.value = parsed.name;
      inputName.classList.remove('field-highlight');
    } else if (inputName) {
      inputName.value = '';
      inputName.classList.add('field-highlight');
      missingFields.push('Name');
    }

    // Native Place
    if (parsed.place && inputPlace) {
      inputPlace.value = parsed.place;
      inputPlace.classList.remove('field-highlight');
    } else if (inputPlace) {
      inputPlace.value = '';
      inputPlace.classList.add('field-highlight');
      missingFields.push('Native Place');
    }

    // Amount
    if (parsed.amount && inputAmount) {
      inputAmount.value = parsed.amount;
      inputAmount.classList.remove('field-highlight');
    } else if (inputAmount) {
      inputAmount.value = '';
      inputAmount.classList.add('field-highlight');
      missingFields.push('Amount');
    }

    if (transcriptText) {
      transcriptText.innerHTML = `<strong>Full Text:</strong> "${escapeHtml(parsed.rawTranscript)}"`;
    }

    if (missingFields.length > 0) {
      showStatus(`Voice recognized. Please enter missing ${missingFields.join(', ')} before saving.`, 'error');
    } else {
      showStatus('Voice recognized. Please review the details before saving.', 'success');
    }

    if (retryBtn) retryBtn.style.display = 'inline-block';
  }

  function clearHighlights() {
    if (inputName) inputName.classList.remove('field-highlight');
    if (inputPlace) inputPlace.classList.remove('field-highlight');
    if (inputAmount) inputAmount.classList.remove('field-highlight');
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Toggle microphone
  micBtn.addEventListener('click', function(e) {
    e.preventDefault();
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  });

  // Retry button
  if (retryBtn) {
    retryBtn.addEventListener('click', function(e) {
      e.preventDefault();
      startListening();
    });
  }

  // Save selected language in localStorage
  if (langSelect) {
    langSelect.addEventListener('change', function() {
      localStorage.setItem('speed_moi_voice_lang', langSelect.value);
      if (isListening) {
        stopListening();
      }
    });
  }

})();
