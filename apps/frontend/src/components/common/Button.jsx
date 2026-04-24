export default function Button({
  type = 'button',
  variant = 'primary',
  size = 'md',
  isLoading = false,
  fullWidth = false,
  disabled,
  className = '',
  children,
  ...props
}) {
  const base =
    'inline-flex items-center justify-center font-normal transition-colors duration-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed border border-black';

  const variants = {
    primary: 'bg-black text-white hover:bg-white hover:text-black',
    outline: 'bg-white text-black hover:bg-black hover:text-white',
    ghost: 'border-transparent bg-transparent text-black shadow-none hover:bg-surface-container',
  };

  const sizes = {
    sm: 'px-3 py-2   ',
    md: 'px-6 py-2.5 text-xs   ',
    lg: 'px-8 py-3 text-sm   ',
  };

  return (
    <button
      type={type}
      disabled={isLoading || disabled}
      className={`${base} ${variants[variant]} ${sizes[size]} ${fullWidth ? 'w-full' : ''} ${className}`}
      {...props}
    >
      {isLoading && (
        <span className="mr-2 inline-block h-3 w-3 animate-spin border-2 border-current border-t-transparent" />
      )}
      {children}
    </button>
  );
}
