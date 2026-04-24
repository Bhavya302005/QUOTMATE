import { useLocation, useOutlet } from 'react-router-dom';

import Header from './Header.jsx';
import BottomTabBar from './BottomTabBar.jsx';
import Sidebar from './Sidebar.jsx';

export default function AppLayout() {
  const location = useLocation();
  const outlet = useOutlet();

  return (
    <div className="relative flex min-h-[100dvh] flex-col overflow-hidden bg-surface text-on-surface selection:bg-black selection:text-white">
      <Header />
      <Sidebar />

      <main className="relative z-0 flex-1 overflow-y-auto overflow-x-hidden pt-16 pb-20 no-scrollbar md:ml-64 md:pb-8">
          <div className="mx-auto w-full max-w-lg px-4 py-6 md:max-w-none md:px-10 md:py-10 lg:px-12">
            {outlet}
          </div>
      </main>

      <BottomTabBar />
    </div>
  );
}
