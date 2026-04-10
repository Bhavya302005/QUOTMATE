import { useLocation, useNavigate } from 'react-router-dom';
import { LogOut, ChevronLeft } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

const TITLE_MAP = {
  '/dashboard': 'Dashboard',
  '/quotations': 'Quotations',
  '/moms': 'Meetings',
  '/work-orders': 'Work orders',
  '/profile': 'Profile',
};

function getTitle(pathname) {
  if (pathname === '/') return 'Dashboard';
  const base = `/${pathname.split('/')[1] || ''}`;
  return TITLE_MAP[base] || 'QuotMate';
}

export default function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const title = getTitle(location.pathname);
  const isNested = location.pathname.split('/').filter(Boolean).length > 1;
  const companyLabel = user?.company_name?.trim() || user?.full_name?.trim() || title;

  return (
    <header className="fixed inset-x-0 top-0 z-50 flex h-16 items-center justify-between border-b border-black bg-surface-white px-4 md:px-6">
      <div className="flex w-10 items-center md:w-12">
        {isNested && (
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="flex h-10 w-10 items-center justify-center border border-black bg-white text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
            aria-label="Go back"
          >
            <ChevronLeft className="h-6 w-6" strokeWidth={2} />
          </button>
        )}
      </div>

      <div className="pointer-events-none absolute left-1/2 top-1/2 flex -translate-x-1/2 -translate-y-1/2 items-center gap-2 md:gap-3">
        <span className="font-mono text-sm font-medium tracking-tighter uppercase text-black md:hidden">QM</span>
        <div className="hidden items-center gap-2 md:flex">
          <span className="font-mono text-sm font-medium tracking-tighter uppercase text-black">QUOTMATE</span>
          <span className="max-w-[160px] truncate font-mono text-[10px] uppercase tracking-widest text-outline-muted">
            × {companyLabel}
          </span>
        </div>
        <span className="max-w-[130px] truncate font-mono text-[10px] uppercase tracking-widest text-outline-muted md:hidden">
          × {companyLabel}
        </span>
      </div>

      <div className="flex w-10 justify-end md:w-12">
        <button
          type="button"
          onClick={() => {
            logout();
            navigate('/login');
          }}
          title="Logout"
          aria-label="Logout"
          className="flex h-9 w-9 items-center justify-center border border-black bg-white text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
        >
          <LogOut className="h-4 w-4" strokeWidth={2} />
        </button>
      </div>
    </header>
  );
}
