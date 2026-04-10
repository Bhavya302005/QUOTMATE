export function isRequired(value) {
  return value != null && String(value).trim().length > 0;
}

export function isValidEmail(value) {
  return /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(String(value || ''));
}

export function hasLetterAndNumber(value) {
  const input = String(value || '');
  return /[A-Za-z]/.test(input) && /\d/.test(input);
}
