import { NavLink } from 'react-router-dom';
import { LayoutGrid, FileText, Users, ClipboardList, User } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

const items = [
  { to: '/dashboard', icon: LayoutGrid, label: 'Dashboard' },
  { to: '/quotations', icon: FileText, label: 'Quotations' },
  { to: '/moms', icon: Users, label: 'MOMs' },
  { to: '/work-orders', icon: ClipboardList, label: 'Work orders' },
  { to: '/profile', icon: User, label: 'Profile' },
];

export default function Sidebar() {
  const { user } = useAuth();
  const display = user?.full_name?.trim() || user?.email?.split('@')[0] || 'Operator';

  return (
    <aside className="fixed left-0 top-16 z-40 hidden h-[calc(100dvh-4rem)] w-64 flex-col border-r border-black bg-surface-container md:flex">
      <div className="border-b border-black px-6 py-6">
        <h2 className="font-headline text-lg font-normal leading-none tracking-tight uppercase text-on-surface">{display}</h2>
        <p className="mt-1 font-mono text-[10px] uppercase tracking-widest text-outline-muted">v.2.4.0_stable</p>
      </div>
      <nav className="flex flex-1 flex-col py-2">
        {items.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/dashboard'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 font-mono text-[10px] uppercase tracking-widest transition-colors duration-100 ${isActive ? 'bg-black text-white' : 'text-on-surface opacity-70 hover:bg-white hover:opacity-100'}`
            }
          >
            <Icon className="h-4 w-4 shrink-0" strokeWidth={1.75} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
