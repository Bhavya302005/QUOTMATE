export default function Card({ className = '', children, onClick }) {
  return (
    <div
      className={`stitch-card p-5 ${onClick ? 'cursor-pointer transition-colors duration-100 hover:bg-black hover:text-white' : ''} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
}
