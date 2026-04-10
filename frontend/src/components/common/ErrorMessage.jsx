export default function ErrorMessage({ message, className = '' }) {
  if (!message) return null;

  return (
    <p className={`mt-1 text-xs font-medium text-error ${className}`}>
      {message}
    </p>
  );
}

