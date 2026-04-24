export default function Modal({ title, children, footer, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-md border border-black bg-surface-white p-4">
        {title && (
          <h2 className="mb-3 text-base font-normal  tracking-tight text-on-surface">{title}</h2>
        )}
        <div className="text-sm font-light text-on-surface">{children}</div>
        {footer && <div className="mt-4">{footer}</div>}
        <button
          type="button"
          onClick={onClose}
          className="mt-3 w-full border border-black bg-white py-2.5    text-black transition-colors duration-100 hover:bg-black hover:text-white"
        >
          Close
        </button>
      </div>
    </div>
  );
}
