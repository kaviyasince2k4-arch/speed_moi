/**
 * SPEED MOI - Voice Input Parser
 * Pure function module for parsing voice recognition transcripts into:
 *   - Contributor Name
 *   - Native Place
 *   - Amount (integer)
 * 
 * Works in both browser and Node.js test environments.
 */

// Native digit mapping (Tamil and other Indian scripts)
const NATIVE_DIGITS = {
  // Tamil digits: ௦ ௧ ௨ ௩ ௪ ௫ ௬ ௭ ௮ ௯
  '௦': '0', '௧': '1', '௨': '2', '௩': '3', '௪': '4',
  '௫': '5', '௬': '6', '௭': '7', '௮': '8', '௯': '9',
  // Devanagari digits: ० १ २ ३ ४ ५ ६ ७ ८ ९
  '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
  '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
  // Kannada digits: ೦ ೧ ೨ ೩ ೪ ೫ ೬ ೭ ೮ ೯
  '೦': '0', '೧': '1', '೨': '2', '೩': '3', '೪': '4',
  '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9',
  // Malayalam digits: ൦ ൧ ൨ ൩ ൪ ൫ ൬ ൭ ൮ ൯
  '൦': '0', '൧': '1', '൨': '2', '൩': '3', '൪': '4',
  '൫': '5', '൬': '6', '൭': '7', '൮': '8', '൯': '9'
};

function normalizeNativeDigits(str) {
  if (!str) return '';
  return str.replace(/[௦-௯०-९೦-೯൦-൯]/g, (char) => NATIVE_DIGITS[char] || char);
}

// Word-to-number maps
const ENGLISH_NUMBERS = {
  'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
  'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
  'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
  'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
  'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
  'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
  'hundred': 100, 'thousand': 1000, 'lakh': 100000, 'lakhs': 100000,
  'lac': 100000, 'lacs': 100000, 'crore': 10000000, 'crores': 10000000
};

const TAMIL_NUMBERS = {
  'ஒன்று': 1, 'ஒன்னு': 1, 'ஒரு': 1,
  'இரண்டு': 2, 'ரெண்டு': 2, 'இரு': 2,
  'மூன்று': 3, 'மூணு': 3,
  'நான்கு': 4, 'நாலு': 4,
  'ஐந்து': 5, 'அஞ்சு': 5,
  'ஆறு': 6,
  'ஏழு': 7,
  'எட்டு': 8,
  'ஒன்பது': 9, 'ஒம்போது': 9,
  'பத்து': 10,
  'இருபது': 20, 'இருவது': 20,
  'முப்பது': 30,
  'நாற்பது': 40, 'நாப்பது': 40,
  'ஐம்பது': 50, 'அம்பது': 50,
  'அறுபது': 60,
  'எழுபது': 70,
  'எண்பது': 80, 'எம்பது': 80,
  'தொண்ணூறு': 90,
  'நூறு': 100, 'ஒரு நூறு': 100, 'நூற்றி': 100,
  'இருநூறு': 200,
  'முந்நூறு': 300,
  'நானூறு': 400,
  'ஐநூறு': 500, 'ஐந்நூறு': 500,
  'அறுநூறு': 600,
  'எழுநூறு': 700,
  'எண்ணூறு': 800,
  'தொள்ளாயிரம்': 900,
  'ஆயிரம்': 1000, 'ஓராயிரம்': 1000, 'ஒரு ஆயிரம்': 1000,
  'இரண்டாயிரம்': 2000, 'ரெண்டாயிரம்': 2000, 'இரண்டாயிரத்து': 2000, 'ரெண்டாயிரத்து': 2000,
  'மூவாயிரம்': 3000, 'மூவாயிரத்து': 3000,
  'நாலாயிரம்': 4000, 'நாலாயிரத்து': 4000,
  'ஐயாயிரம்': 5000, 'ஐந்தாயிரம்': 5000, 'ஐயாயிரத்து': 5000,
  'ஆறாயிரம்': 6000,
  'ஏழாயிரம்': 7000,
  'எட்டாயிரம்': 8000,
  'ஒன்பதாயிரம்': 9000,
  'பத்தாயிரம்': 10000,
  'இருபதாயிரம்': 20000,
  'ஐம்பதாயிரம்': 50000,
  'லட்சம்': 100000, 'இலட்சம்': 100000, 'ஒரு லட்சம்': 100000
};

// Currency markers across languages
const CURRENCY_WORDS_REGEX = /(?:rupees?|rupee|rs\.?|inr|₹|ரூபாய்|ரூபா|ரூ)/gi;

// Action/filler words to strip (giving/moi)
const FILLER_VERBS_REGEX = /\b(?:gave|gives|given|paid|has\s+given|contributed|contributes|put|கொடுத்தார்|தந்தார்|கொடுத்தது|குடுத்தாரு|குடுத்தார்|போட்டார்|செய்தார்|மொய்|ரூபாய்|ரூபா|rupees?|rupee)\b/gi;

/**
 * Extracts and calculates numeric amount from text.
 * Returns { amount: number | null, cleanedText: string }
 */
function extractAmount(text, lang) {
  let cleaned = normalizeNativeDigits(text);

  // Pattern 1: Digits already present (e.g. 2000, 2,500, ₹500, 500 rupees, 500 ரூபாய்)
  const digitRegex = /(?:₹|rs\.?|inr)?\s*(\d{1,3}(?:,\d{3})+|\d+)\s*(?:₹|rs\.?|inr|rupees?|rupee|ரூபாய்|ரூபா|ரூ)?/i;
  const digitMatch = cleaned.match(digitRegex);
  if (digitMatch) {
    const rawNum = digitMatch[1].replace(/,/g, '');
    const amountVal = parseInt(rawNum, 10);
    if (!isNaN(amountVal) && amountVal > 0) {
      // Remove the matched portion and currency markers
      cleaned = cleaned.replace(digitMatch[0], ' ');
      cleaned = cleaned.replace(CURRENCY_WORDS_REGEX, ' ');
      return {
        amount: amountVal,
        cleanedText: cleaned
      };
    }
  }

  // Pattern 2: Word numbers in Tamil
  // Check compound phrases first (e.g. "இரண்டாயிரத்து ஐநூறு", "இரண்டாயிரம்", "ஐநூறு")
  let tamilTotal = 0;
  let matchedTamilWords = [];

  // Sort keys by descending length to match longest compound phrases first
  const tamilKeys = Object.keys(TAMIL_NUMBERS).sort((a, b) => b.length - a.length);
  for (const word of tamilKeys) {
    if (cleaned.includes(word)) {
      tamilTotal += TAMIL_NUMBERS[word];
      matchedTamilWords.push(word);
      cleaned = cleaned.replace(word, ' ');
    }
  }

  if (tamilTotal > 0) {
    cleaned = cleaned.replace(CURRENCY_WORDS_REGEX, ' ');
    return {
      amount: tamilTotal,
      cleanedText: cleaned
    };
  }

  // Pattern 3: Word numbers in English (e.g. "two thousand five hundred", "two thousand")
  const tokens = cleaned.toLowerCase().split(/[\s,]+/);
  let engTotal = 0;
  let currentGroup = 0;
  let hasEngNumber = false;
  let matchedTokens = [];

  for (const token of tokens) {
    if (ENGLISH_NUMBERS.hasOwnProperty(token)) {
      hasEngNumber = true;
      matchedTokens.push(token);
      const val = ENGLISH_NUMBERS[token];
      if (val === 100) {
        currentGroup = (currentGroup === 0 ? 1 : currentGroup) * 100;
      } else if (val === 1000 || val === 100000 || val === 10000000) {
        currentGroup = (currentGroup === 0 ? 1 : currentGroup) * val;
        engTotal += currentGroup;
        currentGroup = 0;
      } else {
        currentGroup += val;
      }
    }
  }
  engTotal += currentGroup;

  if (hasEngNumber && engTotal > 0) {
    // Remove matched tokens
    for (const tok of matchedTokens) {
      const reg = new RegExp(`\\b${tok}\\b`, 'gi');
      cleaned = cleaned.replace(reg, ' ');
    }
    cleaned = cleaned.replace(CURRENCY_WORDS_REGEX, ' ');
    return {
      amount: engTotal,
      cleanedText: cleaned
    };
  }

  // No amount found
  return {
    amount: null,
    cleanedText: cleaned
  };
}

/**
 * Extracts contributor name and native place from the remaining text.
 * Strategy:
 *   1. Comma separation: "Name, Place"
 *   2. Preposition words: "from", "in", "at", "இருந்து"
 *   3. Fallback: Last remaining word is Place, all preceding words are Name.
 */
function extractNameAndPlace(text) {
  // Strip common verbs and extra currency remnants
  let cleaned = text.replace(FILLER_VERBS_REGEX, ' ');
  cleaned = cleaned.replace(CURRENCY_WORDS_REGEX, ' ');
  // Clean up sentence punctuation but PRESERVE dots (initials T.), hyphens (-), &, and commas
  cleaned = cleaned.replace(/["':;!?()]/g, ' ').trim();

  let name = '';
  let place = '';

  // Case 1: Comma separated (e.g. "Name, Place" or "T. விஜயபிரபாகரன் - சுஜிதா, KK பட்டி")
  if (cleaned.includes(',')) {
    const parts = cleaned.split(',').map(p => p.trim()).filter(Boolean);
    if (parts.length >= 2) {
      name = parts[0];
      place = parts.slice(1).join(', ');
      return {
        name: cleanString(name),
        place: cleanString(place)
      };
    }
  }

  // Case 2: Preposition separation (English "from", "in", "at")
  const prepRegex = /\s+(?:from|in|at)\s+/i;
  if (prepRegex.test(cleaned)) {
    const parts = cleaned.split(prepRegex);
    if (parts.length >= 2) {
      name = parts[0];
      place = parts.slice(1).join(' ');
      return {
        name: cleanString(name),
        place: cleanString(place)
      };
    }
  }

  // Case 3: Tamil suffixes: "இருந்து"
  const tamilFromRegex = /(.*?)\s+(?:இருந்து|லிருந்து|இருந்த)\s+(.*)/;
  const matchTamilFrom = cleaned.match(tamilFromRegex);
  if (matchTamilFrom) {
    name = matchTamilFrom[1];
    place = matchTamilFrom[2];
    return {
      name: cleanString(name),
      place: cleanString(place)
    };
  }

  // Case 4: Fallback - Last remaining word is Native Place, preceding words are Name
  const words = cleaned.split(/\s+/).filter(Boolean);
  if (words.length >= 2) {
    place = words[words.length - 1];
    name = words.slice(0, words.length - 1).join(' ');
  } else if (words.length === 1) {
    name = words[0];
    place = '';
  }

  return {
    name: cleanString(name),
    place: cleanString(place)
  };
}

function cleanString(str) {
  if (!str) return '';
  // Preserve initials (T.), hyphens (-), &, spaces, Indian scripts, English, numbers
  // Only remove leading/trailing commas or slashes and collapse whitespace
  return str
    .replace(/^[,/\s]+|[,/\s]+$/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Main Pure Function: parseVoiceInput
 * 
 * @param {string} transcript - The raw speech text from browser Web Speech API
 * @param {string} [lang='en-IN'] - Selected language code ('en-IN', 'ta-IN', etc.)
 * @returns {object} { name: string, place: string, amount: number | null, rawTranscript: string }
 */
function parseVoiceInput(transcript, lang = 'en-IN') {
  if (!transcript || typeof transcript !== 'string') {
    return {
      name: '',
      place: '',
      amount: null,
      rawTranscript: ''
    };
  }

  const rawTranscript = transcript.trim();

  // Step 1: Extract amount
  const { amount, cleanedText } = extractAmount(rawTranscript, lang);

  // Step 2: Extract name and native place from remaining text
  const { name, place } = extractNameAndPlace(cleanedText);

  return {
    name: name || '',
    place: place || '',
    amount: amount !== null ? amount : null,
    rawTranscript: rawTranscript
  };
}

// Export for Node.js test environment and ES module
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    parseVoiceInput,
    extractAmount,
    extractNameAndPlace,
    normalizeNativeDigits
  };
}

if (typeof window !== 'undefined') {
  window.parseVoiceInput = parseVoiceInput;
}

export {
  parseVoiceInput,
  extractAmount,
  extractNameAndPlace,
  normalizeNativeDigits
};

