// Formatting helpers will be added here (dates, currency, etc.).

export function formatCurrency(amount) {
  if (typeof amount !== 'number') return '';
  return amount.toLocaleString('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  });
}

