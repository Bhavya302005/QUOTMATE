export default function Input({
  label,
  error,
  helperText,
  className = '',
  inputClassName = '',
  icon: Icon,
  registration,
  ...props
}) {
  const hasIcon = Boolean(Icon);
  const inputStyle = {
    ...(props.style || {}),
    ...(hasIcon ? { paddingLeft: '2.75rem', paddingInlineStart: '2.75rem' } : {}),
  };

  return (
    <div className={className}>
      {label && <label className="mb-1.5 block stitch-label">{label}</label>}
      <div className="relative">
        {hasIcon && (
          <div className="pointer-events-none absolute left-3 top-1/2 z-10 -translate-y-1/2 text-on-surface">
            <Icon className="h-5 w-5" strokeWidth={2} />
          </div>
        )}
        <input
          {...registration}
          {...props}
          className={`stitch-input ${hasIcon ? 'stitch-input--with-icon pr-3' : ''} ${error ? 'border-error' : ''} ${inputClassName}`}
          style={inputStyle}
        />
      </div>
      {helperText && !error && (
        <p className="mt-1 text-sm text-outline-muted">{helperText}</p>
      )}
      {error && (
        <p className="mt-1 text-sm text-error">{error}</p>
      )}
    </div>
  );
}
