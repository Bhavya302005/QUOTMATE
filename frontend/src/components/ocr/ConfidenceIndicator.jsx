export default function ConfidenceIndicator({ confidence = 0 }) {
  const normalized = confidence <= 1 ? confidence * 100 : confidence;
  const percentage = Math.max(0, Math.min(100, Math.round(normalized)));

  let label = 'Low';
  if (percentage >= 80) label = 'High';
  else if (percentage >= 55) label = 'Medium';

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between    text-on-surface">
        <span className="text-outline-muted">Confidence</span>
        <span>
          {percentage}% · {label}
        </span>
      </div>
      <div className="h-1.5 w-full overflow-hidden border border-black bg-surface-container">
        <div className="h-full bg-black transition-[width] duration-300" style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}
