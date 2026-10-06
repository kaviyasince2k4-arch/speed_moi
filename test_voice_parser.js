/**
 * Node.js Test Suite for SPEED MOI Voice Parser
 * Tests English and Tamil inputs against exact requirements.
 */

import { parseVoiceInput } from './static/js/voice_parser.js';

const testCases = [
  {
    input: "Ramesh Kumar, Salem, 2000 rupees",
    lang: "en-IN",
    expected: { name: "Ramesh Kumar", place: "Salem", amount: 2000 }
  },
  {
    input: "Monica, Salem, 2,500 rupees",
    lang: "en-IN",
    expected: { name: "Monica", place: "Salem", amount: 2500 }
  },
  {
    input: "Suresh from Madurai 500 rupees",
    lang: "en-IN",
    expected: { name: "Suresh", place: "Madurai", amount: 500 }
  },
  {
    input: "Ramesh Kumar from Salem gave two thousand rupees",
    lang: "en-IN",
    expected: { name: "Ramesh Kumar", place: "Salem", amount: 2000 }
  },
  {
    input: "ரமேஷ் குமார், சேலம், இரண்டாயிரம் ரூபாய்",
    lang: "ta-IN",
    expected: { name: "ரமேஷ் குமார்", place: "சேலம்", amount: 2000 }
  },
  {
    input: "முருகன் மதுரை 500 ரூபாய்",
    lang: "ta-IN",
    expected: { name: "முருகன்", place: "மதுரை", amount: 500 }
  },
  {
    input: "T. விஜயபிரபாகரன் - சுஜிதா, KK பட்டி, 10000 ரூபாய்",
    lang: "ta-IN",
    expected: { name: "T. விஜயபிரபாகரன் - சுஜிதா", place: "KK பட்டி", amount: 10000 }
  },
  {
    input: "T. Vijayaprabhakaran - Sujitha from KK பட்டி 10000 rupees",
    lang: "en-IN",
    expected: { name: "T. Vijayaprabhakaran - Sujitha", place: "KK பட்டி", amount: 10000 }
  }
];

console.log("=========================================================================================================================");
console.log("                                       SPEED MOI - STAGE 3 VOICE PARSER VERIFICATION                                      ");
console.log("=========================================================================================================================");

let allPassed = true;
const results = [];

testCases.forEach((tc, idx) => {
  const got = parseVoiceInput(tc.input, tc.lang);
  const pass = (
    got.name === tc.expected.name &&
    got.place === tc.expected.place &&
    got.amount === tc.expected.amount
  );

  if (!pass) allPassed = false;

  results.push({
    No: idx + 1,
    Input: tc.input,
    Expected: `${tc.expected.name} | ${tc.expected.place} | ${tc.expected.amount}`,
    Got: `${got.name} | ${got.place} | ${got.amount}`,
    Result: pass ? "PASS" : "FAIL"
  });
});

console.table(results);

if (allPassed) {
  console.log("\n>>> ALL STAGE 3 VOICE PARSER TESTS PASSED (6/6) <<<\n");
  process.exit(0);
} else {
  console.error("\n>>> SOME TESTS FAILED. PLEASE FIX AND RE-RUN <<<\n");
  process.exit(1);
}
