import { NavLink, useLocation } from 'react-router-dom';
import { Home, FileText, Users, ClipboardList, User } from 'lucide-react';

const tabs = [
  { to: '/dashboard', icon: Home, label: 'Home' },
  { to: '/quotations', icon: FileText, label: 'Quotes' },
  { to: '/moms', icon: Users, label: 'MOM' },
  { to: '/work-orders', icon: ClipboardList, label: 'Work' },
  { to: '/profile', icon: User, label: 'Profile' },
];

export default function BottomTabBar() {
  const location = useLocation();

  return (
    <div id="bottom-tab-bar" className="fixed bottom-0 left-0 right-0 z-50 w-full border-t border-black bg-surface-white pb-[env(safe-area-inset-bottom,0)] md:hidden">
      <nav className="mx-auto flex h-14 w-full max-w-lg items-stretch justify-between">
        {tabs.map((tab) => {
          const IconComponent = tab.icon;
          const isActive =
            location.pathname.startsWith(tab.to) &&
            (tab.to !== '/dashboard' || location.pathname === '/dashboard');

          return (
            <NavLink
              key={tab.to}
              to={tab.to}
              end={tab.to === '/dashboard'}
              className={`relative flex flex-1 flex-col items-center justify-center outline-none transition-colors duration-100 ${isActive ? 'bg-black text-white' : 'text-on-surface opacity-60 hover:opacity-100'}`}
            >
              <IconComponent className="mb-0.5 h-4 w-4" strokeWidth={isActive ? 2.25 : 2} />
              <span className="text-[9px]   ">{tab.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
}
