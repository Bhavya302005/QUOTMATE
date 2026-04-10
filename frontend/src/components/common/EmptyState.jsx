import { Link } from 'react-router-dom';

export default function EmptyState({ icon: Icon, title, description, actionLabel, actionTo }) {
  return (
    <div className="flex flex-col items-center justify-center border border-black bg-surface-white px-4 py-10 text-center">
      {Icon && (
        <div className="mb-4 flex h-12 w-12 items-center justify-center border border-black bg-black text-white">
          <Icon className="h-6 w-6" strokeWidth={2} />
        </div>
      )}
      <h3 className="mb-1 text-base font-normal  tracking-tight text-on-surface">{title}</h3>
      {description && (
        <p className="mb-4    text-outline-muted">{description}</p>
      )}
      {actionLabel && actionTo && (
        <Link
          to={actionTo}
          className="border border-black bg-black px-4 py-2.5    text-white transition-colors duration-100 hover:bg-white hover:text-black"
        >
          {actionLabel}
        </Link>
      )}
    </div>
  );
}
