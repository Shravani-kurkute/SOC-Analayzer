import { Outlet } from 'react-router-dom';
import { Sidebar } from '@components/layout/Sidebar';
import { Topbar } from '@components/layout/Topbar';
import { useSidebar } from '@contexts/SidebarContext';
import { cn } from '@utils/cn';

export default function AppLayout() {
  const { isCollapsed } = useSidebar();

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div
        className={cn(
          'flex flex-1 flex-col overflow-hidden transition-all duration-300',
          isCollapsed ? 'ml-16' : 'ml-64',
        )}
      >
        <Topbar />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
