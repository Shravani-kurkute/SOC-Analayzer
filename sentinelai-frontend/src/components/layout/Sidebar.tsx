import { useLocation, useNavigate } from 'react-router-dom';
import { useSidebar } from '@contexts/SidebarContext';
import { cn } from '@utils/cn';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  AlertTriangle,
  Siren,
  Shield,
  Server,
  FileText,
  Brain,
  PlayCircle,
  Puzzle,
  Settings,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  Activity,
} from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@components/ui/tooltip';
import { ScrollArea } from '@components/ui/scroll-area';

interface NavItem {
  label: string;
  path: string;
  icon: React.ElementType;
  badge?: string;
  badgeColor?: string;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const navGroups: NavGroup[] = [
  {
    label: 'Overview',
    items: [{ label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard }],
  },
  {
    label: 'Security',
    items: [
      { label: 'Alerts', path: '/alerts', icon: AlertTriangle, badge: '24', badgeColor: 'bg-red-500' },
      { label: 'Incidents', path: '/incidents', icon: Siren, badge: '7', badgeColor: 'bg-orange-500' },
      { label: 'Threats', path: '/threats', icon: Shield },
      { label: 'Assets', path: '/assets', icon: Server },
    ],
  },
  {
    label: 'Operations',
    items: [
      { label: 'AI Center', path: '/ai', icon: Brain },
      { label: 'Playbooks', path: '/playbooks', icon: PlayCircle },
      { label: 'Reports', path: '/reports', icon: FileText },
      { label: 'Integrations', path: '/integrations', icon: Puzzle },
    ],
  },
  {
    label: 'Administration',
    items: [
      { label: 'Admin', path: '/admin', icon: ShieldCheck },
      { label: 'Settings', path: '/settings', icon: Settings },
    ],
  },
];

export function Sidebar() {
  const { isCollapsed, toggle } = useSidebar();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <AnimatePresence>
      <motion.aside
        className={cn(
          'fixed left-0 top-0 z-40 flex h-screen flex-col border-r border-border/50 bg-gradient-to-b from-[#050816] via-[#0a0a2e] to-[#050816] shadow-2xl',
          isCollapsed ? 'w-16' : 'w-64',
        )}
        animate={{ width: isCollapsed ? 64 : 256 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
      >
        <div className="relative flex h-16 items-center border-b border-border/50 px-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#00F5FF]/10">
              <Activity className="h-5 w-5 text-[#00F5FF]" />
            </div>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col"
              >
                <span className="text-sm font-bold tracking-wide text-white">SentinelAI</span>
                <span className="text-[10px] text-[#00F5FF]/60 font-mono">SOC PLATFORM</span>
              </motion.div>
            )}
          </div>
          <button
            onClick={toggle}
            className={cn(
              'absolute -right-3 top-1/2 -translate-y-1/2 flex h-6 w-6 items-center justify-center rounded-full border border-border bg-[#050816] text-muted-foreground hover:text-foreground transition-colors',
              isCollapsed && 'right-3',
            )}
          >
            {isCollapsed ? (
              <ChevronRight className="h-3 w-3" />
            ) : (
              <ChevronLeft className="h-3 w-3" />
            )}
          </button>
        </div>

        <ScrollArea className="flex-1 px-2 py-4">
          <nav className="space-y-6">
            {navGroups.map((group) => (
              <div key={group.label}>
                {!isCollapsed && (
                  <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/50">
                    {group.label}
                  </p>
                )}
                <div className="space-y-1">
                  {group.items.map((item) => {
                    const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
                    const Icon = item.icon;

                    const navButton = (
                      <button
                        onClick={() => navigate(item.path)}
                        className={cn(
                          'group relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                          isActive
                            ? 'bg-[#00F5FF]/10 text-[#00F5FF] shadow-[inset_0_0_20px_rgba(0,245,255,0.05)]'
                            : 'text-muted-foreground hover:bg-accent/50 hover:text-accent-foreground',
                        )}
                      >
                        {isActive && (
                          <motion.div
                            layoutId="sidebar-active"
                            className="absolute inset-0 rounded-lg bg-[#00F5FF]/5"
                            transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                          />
                        )}
                        <div className="relative z-10 flex items-center gap-3">
                          <Icon className={cn('h-4.5 w-4.5 shrink-0', isActive && 'text-[#00F5FF]')} />
                          {!isCollapsed && (
                            <span className="truncate">{item.label}</span>
                          )}
                        </div>
                        {!isCollapsed && item.badge && (
                          <span
                            className={cn(
                              'ml-auto rounded-full px-2 py-0.5 text-[10px] font-bold text-white',
                              item.badgeColor || 'bg-primary',
                            )}
                          >
                            {item.badge}
                          </span>
                        )}
                      </button>
                    );

                    if (isCollapsed) {
                      return (
                        <TooltipProvider key={item.path} delayDuration={0}>
                          <Tooltip>
                            <TooltipTrigger asChild>{navButton}</TooltipTrigger>
                            <TooltipContent side="right" className="flex items-center gap-2">
                              <span>{item.label}</span>
                              {item.badge && (
                                <span className={cn('rounded px-1.5 py-0.5 text-[10px] font-bold text-white', item.badgeColor || 'bg-primary')}>
                                  {item.badge}
                                </span>
                              )}
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                      );
                    }

                    return <div key={item.path}>{navButton}</div>;
                  })}
                </div>
              </div>
            ))}
          </nav>
        </ScrollArea>

        <div className="border-t border-border/50 p-3">
          <div className="flex items-center gap-3 rounded-lg bg-primary/5 px-3 py-2">
            <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-pulse" />
            {!isCollapsed && (
              <div className="flex flex-col">
                <span className="text-xs font-medium text-foreground">System Online</span>
                <span className="text-[10px] text-muted-foreground">All services healthy</span>
              </div>
            )}
          </div>
        </div>
      </motion.aside>
    </AnimatePresence>
  );
}
