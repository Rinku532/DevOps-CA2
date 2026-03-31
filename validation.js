/**
 * validation.js — Student Feedback Registration Form
 * Sub Task 3: JavaScript client-side validation
 *
 * Rules:
 *  - Student Name  : not empty
 *  - Email         : proper format (regex)
 *  - Mobile Number : exactly 10 digits
 *  - Gender        : at least one radio selected
 *  - Department    : must choose a non-placeholder value
 *  - Comments      : not blank, minimum 10 words
 */

'use strict';

/* ── Utility helpers ─────────────────────────────────────── */

/**
 * Count words in a string (split by whitespace, ignore empty tokens).
 * @param {string} text
 * @returns {number}
 */
function countWords(text) {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

/**
 * Mark a form-group as valid or invalid and set/clear an error message.
 * @param {string} groupId  - id of the .form-group element
 * @param {string} errorId  - id of the .error-msg <span>
 * @param {boolean} isValid
 * @param {string} message  - error message (empty string clears it)
 */
function setValidity(groupId, errorId, isValid, message = '') {
  const group = document.getElementById(groupId);
  const span  = document.getElementById(errorId);

  if (!group || !span) return;

  if (isValid) {
    group.classList.remove('invalid');
    span.textContent = '';
  } else {
    group.classList.add('invalid');
    span.textContent = message;
  }
}

/* ── Individual field validators ─────────────────────────── */

function validateName() {
  const val = document.getElementById('studentName').value.trim();
  const ok  = val.length > 0;
  setValidity('group-name', 'err-name', ok, 'Student name is required.');
  return ok;
}

function validateEmail() {
  const val   = document.getElementById('emailId').value.trim();
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  let msg = '';

  if (!val) {
    msg = 'Email address is required.';
  } else if (!regex.test(val)) {
    msg = 'Enter a valid email address (e.g. name@example.com).';
  }

  const ok = msg === '';
  setValidity('group-email', 'err-email', ok, msg);
  return ok;
}

function validateMobile() {
  const val   = document.getElementById('mobileNumber').value.trim();
  const regex = /^\d{10}$/;
  let msg = '';

  if (!val) {
    msg = 'Mobile number is required.';
  } else if (!regex.test(val)) {
    msg = 'Enter a valid 10-digit mobile number (digits only).';
  }

  const ok = msg === '';
  setValidity('group-mobile', 'err-mobile', ok, msg);
  return ok;
}

function validateDepartment() {
  const val = document.getElementById('department').value;
  const ok  = val !== '' && val !== null;
  setValidity('group-dept', 'err-dept', ok, 'Please select your department.');
  return ok;
}

function validateGender() {
  const selected = document.querySelector('input[name="gender"]:checked');
  const ok = selected !== null;
  setValidity('group-gender', 'err-gender', ok, 'Please select your gender.');
  return ok;
}

function validateComments() {
  const val   = document.getElementById('feedbackComments').value.trim();
  const words = countWords(val);
  let msg = '';

  if (!val) {
    msg = 'Feedback comments are required.';
  } else if (words < 10) {
    msg = `Please write at least 10 words (currently ${words} word${words === 1 ? '' : 's'}).`;
  }

  const ok = msg === '';
  setValidity('group-comments', 'err-comments', ok, msg);
  return ok;
}

/* ── Live word-count for textarea ────────────────────────── */

(function initWordCount() {
  const textarea  = document.getElementById('feedbackComments');
  const wordCount = document.getElementById('word-count');

  if (!textarea || !wordCount) return;

  textarea.addEventListener('input', () => {
    const n = countWords(textarea.value);
    wordCount.textContent = `${n} word${n === 1 ? '' : 's'}`;
    wordCount.classList.toggle('enough', n >= 10);
  });
})();

/* ── Real-time validation (on blur) ─────────────────────── */

(function attachBlurListeners() {
  const map = [
    ['studentName',     validateName],
    ['emailId',         validateEmail],
    ['mobileNumber',    validateMobile],
    ['department',      validateDepartment],
    ['feedbackComments',validateComments],
  ];

  map.forEach(([id, fn]) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('blur', fn);
  });

  // Gender radios
  document.querySelectorAll('input[name="gender"]').forEach(radio => {
    radio.addEventListener('change', validateGender);
  });
})();

/* ── Form submission ─────────────────────────────────────── */

document.getElementById('feedbackForm').addEventListener('submit', function (e) {
  e.preventDefault();

  // Run all validators; collect results
  const results = [
    validateName(),
    validateEmail(),
    validateMobile(),
    validateDepartment(),
    validateGender(),
    validateComments(),
  ];

  const allValid = results.every(Boolean);

  if (!allValid) {
    // Scroll to first error
    const firstError = document.querySelector('.form-group.invalid');
    if (firstError) {
      firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    return;
  }

  // ── All validations passed → show success modal
  document.getElementById('successModal').removeAttribute('hidden');
  this.reset();

  // Reset word count display
  const wc = document.getElementById('word-count');
  if (wc) { wc.textContent = '0 words'; wc.classList.remove('enough'); }

  // Clear any leftover invalid states
  document.querySelectorAll('.form-group.invalid').forEach(g => g.classList.remove('invalid'));
});

/* ── Reset button: clear validation states ───────────────── */

document.getElementById('resetBtn').addEventListener('click', function () {
  // Give the browser time to clear field values first
  setTimeout(() => {
    document.querySelectorAll('.form-group').forEach(g => g.classList.remove('invalid'));
    document.querySelectorAll('.error-msg').forEach(s => { s.textContent = ''; });
    const wc = document.getElementById('word-count');
    if (wc) { wc.textContent = '0 words'; wc.classList.remove('enough'); }
  }, 0);
});

/* ── Modal close ─────────────────────────────────────────── */

function closeModal() {
  document.getElementById('successModal').setAttribute('hidden', '');
}

// Close modal on overlay click
document.getElementById('successModal').addEventListener('click', function (e) {
  if (e.target === this) closeModal();
});

// Close modal on Escape key
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') closeModal();
});
