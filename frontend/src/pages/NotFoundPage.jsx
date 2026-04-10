import { Link } from 'react-router-dom';
import Card from '../components/common/Card.jsx';

export default function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4">
      <Card className="w-full max-w-sm text-center">
        <h1 className="mb-2 text-xl font-light  tracking-tight text-on-surface">Page not found</h1>
        <p className="mb-6 text-sm font-light text-outline-muted">
          The page you are looking for doesn&apos;t exist or has been moved.
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center justify-center border border-black bg-black px-4 py-2.5    text-white transition-colors duration-100 hover:bg-white hover:text-black"
        >
          Dashboard
        </Link>
      </Card>
    </div>
  );
}
