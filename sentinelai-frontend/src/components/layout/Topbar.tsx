import { useState, useCallback, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useSidebar } from '@contexts/SidebarContext';
import { useTheme } from '@contexts/ThemeContext';
import { useAuth } from '@hooks/useAuth';
import { useWebSocket } from '@contexts/WebSocketContext';
import { notificationService } from '@services/notificationService';
import { cn } from '@utils/cn';
import {
  Menu,
  Search,
  Bell,
  Moon,
  Sun,
  User,
  LogOut,
  Settings,
  Keyboard,
  Command,
  ChevronDown,
  Shield,
  AlertTriangle,
  MessageSquare,
  CheckCheck,
  Trash2,
  Loader2,
  Clock,
} from 'lucide-react';
import { Button } from '@components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@components/ui/dropdown-menu';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from '@components/ui/command';
import type { Notification } from '@typings/notification';


const searchItems = [
  {
    heading: 'Pages',
    items: [
      { label: 'Dashboard', path: '/dashboard', icon: Shield },
      { label: 'Alerts', path: '/alerts', icon: AlertTriangle },
      { label: 'Incidents', path: '/incidents', icon: AlertTriangle },
      { label: 'Threat Intelligence', path: '/threats', icon: Shield },
      { label: 'AI Center', path: '/ai', icon: Command },
    ],
  },
  {
    heading: 'Actions',
    items: [
      { label: 'Generate Report', path: '/reports/builder', icon: FileText },
      { label: 'View Playbooks', path: '/playbooks', icon: Command },
      { label: 'Settings', path: '/settings', icon: Settings },
    ],
  },
];

export function Topbar() {
  const { toggleMobile } = useSidebar();
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchOpen, setSearchOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifLoading, setNotifLoading] = useState(false);
  const { lastEvent } = useWebSocket();

  const loadNotifications = useCallback(async () => {
    setNotifLoading(true)
    try {
      const [listRes, countRes] = await Promise.all([
        notificationService.list({ limit: 10 }),
        notificationService.getUnreadCount(),
      ])
      setNotifications(listRes.items)
      setUnreadCount(countRes.count)
    } catch { /* ignore */ }
    setNotifLoading(false)
  }, [])

  const loadUnreadCount = useCallback(async () => {
    try {
      const res = await notificationService.getUnreadCount()
      setUnreadCount(res.count)
    } catch { /* ignore */ }
  }, [])

  useEffect(() => { loadNotifications() }, [loadNotifications])

  useEffect(() => {
    if (lastEvent?.type === 'notification') {
      loadUnreadCount()
      setNotifications(prev => {
        if (lastEvent.notification) {
          return [lastEvent.notification, ...prev].slice(0, 50)
        }
        return prev
      })
    }
  }, [lastEvent, loadUnreadCount])

  const handleMarkAllRead = async () => {
    await notificationService.markAllAsRead()
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
    setUnreadCount(0)
  }

  const handleClearAll = async () => {
    await notificationService.clearAll()
    setNotifications([])
    setUnreadCount(0)
  }

  const handleMarkRead = async (id: string) => {
    await notificationService.markAsRead(id)
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
    setUnreadCount(prev => Math.max(0, prev - 1))
  }

  const severityColor = (sev: string) => {
    if (sev === 'critical') return 'bg-red-500'
    if (sev === 'warning') return 'bg-orange-500'
    if (sev === 'success') return 'bg-emerald-500'
    return 'bg-blue-500'
  }

  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 'Dashboard';
    if (path.startsWith('/alerts')) return 'Alerts';
    if (path.startsWith('/incidents')) return 'Incidents';
    if (path.startsWith('/threats')) return 'Threat Intelligence';
    if (path.startsWith('/assets')) return 'Asset Inventory';
    if (path.startsWith('/reports')) return 'Reports';
    if (path.startsWith('/ai')) return 'AI Security Center';
    if (path.startsWith('/playbooks')) return 'Playbooks';
    if (path.startsWith('/integrations')) return 'Integrations';
    if (path.startsWith('/admin')) return 'Administration';
    if (path.startsWith('/settings')) return 'Settings';
    return 'Dashboard';
  };

  return (
    <>
      <header className="flex h-16 items-center justify-between border-b border-border/50 bg-background/80 px-4 backdrop-blur-xl lg:px-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={toggleMobile}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-foreground">
              {getPageTitle()}
            </h1>
            <p className="text-xs text-muted-foreground hidden sm:block">
              Security Operations Center
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            className="hidden md:flex items-center gap-2 text-muted-foreground hover:text-foreground"
            onClick={() => setSearchOpen(true)}
          >
            <Search className="h-4 w-4" />
            <span className="text-sm">Search...</span>
            <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
              <span>⌘</span>K
            </kbd>
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setSearchOpen(true)}
          >
            <Search className="h-4 w-4" />
          </Button>

          <Button variant="ghost" size="icon" onClick={toggleTheme} className="text-muted-foreground">
            {theme === 'dark' ? <Sun className="h-4.5 w-4.5" /> : <Moon className="h-4.5 w-4.5" />}
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative text-muted-foreground">
                <Bell className="h-4.5 w-4.5" />
                {unreadCount > 0 && (
                  <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel className="flex items-center justify-between">
                <span>Notifications</span>
                <div className="flex items-center gap-1">
                  {unreadCount > 0 && (
                    <Button size="icon-sm" variant="ghost" onClick={handleMarkAllRead} title="Mark all as read">
                      <CheckCheck className="h-3.5 w-3.5" />
                    </Button>
                  )}
                  {notifications.length > 0 && (
                    <Button size="icon-sm" variant="ghost" onClick={handleClearAll} title="Clear all">
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  )}
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <div className="max-h-72 overflow-y-auto">
                {notifLoading && notifications.length === 0 ? (
                  <div className="flex justify-center py-4"><Loader2 className="h-5 w-5 animate-spin text-muted-foreground" /></div>
                ) : notifications.length === 0 ? (
                  <div className="text-center py-6 text-sm text-muted-foreground">No notifications</div>
                ) : (
                  notifications.slice(0, 10).map((notification) => (
                    <DropdownMenuItem
                      key={notification.id}
                      className="flex flex-col items-start gap-1 p-3 cursor-pointer"
                      onClick={() => handleMarkRead(notification.id)}
                    >
                      <div className="flex items-center gap-2 w-full">
                        <div className={cn('h-2 w-2 rounded-full shrink-0', severityColor(notification.severity))} />
                        <span className="text-sm font-medium flex-1 truncate">{notification.title}</span>
                        {!notification.is_read && (
                          <span className="h-2 w-2 rounded-full bg-[#00F5FF]" />
                        )}
                      </div>
                      {notification.message && (
                        <p className="text-xs text-muted-foreground pl-4 truncate">{notification.message}</p>
                      )}
                      <span className="text-[10px] text-muted-foreground/60 pl-4 flex items-center gap-1">
                        <Clock className="h-2.5 w-2.5" />
                        {timeAgo(notification.created_at)}
                      </span>
                    </DropdownMenuItem>
                  ))
                )}
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="justify-center text-sm text-primary cursor-pointer" onClick={() => navigate('/settings?tab=notifications')}>
                Notification Settings
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center gap-2 px-2">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="" alt={user?.full_name || 'User'} />
                  <AvatarFallback className="bg-primary/10 text-primary text-xs">
                    {user?.full_name
                      ? user.full_name.split(' ').map((n: string) => n[0]).join('').toUpperCase()
                      : 'SA'}
                  </AvatarFallback>
                </Avatar>
                <div className="hidden lg:flex flex-col items-start">
                  <span className="text-sm font-medium text-foreground">
                    {user?.full_name || 'Analyst'}
                  </span>
                  <span className="text-[10px] text-muted-foreground capitalize">
                    {user?.role || 'Security Analyst'}
                  </span>
                </div>
                <ChevronDown className="hidden lg:block h-3.5 w-3.5 text-muted-foreground" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col">
                  <span>{user?.full_name || 'Security Analyst'}</span>
                  <span className="text-xs font-normal text-muted-foreground">
                    {user?.email || 'analyst@sentinelai.dev'}
                  </span>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuGroup>
                <DropdownMenuItem onClick={() => navigate('/settings')}>
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/settings')}>
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Keyboard className="mr-2 h-4 w-4" />
                  Keyboard shortcuts
                </DropdownMenuItem>
              </DropdownMenuGroup>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={logout}
                className="text-red-400 focus:text-red-400"
              >
                <LogOut className="mr-2 h-4 w-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <CommandDialog open={searchOpen} onOpenChange={setSearchOpen}>
        <CommandInput placeholder="Search alerts, incidents, threats..." />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          {searchItems.map((group) => (
            <CommandGroup key={group.heading} heading={group.heading}>
              {group.items.map((item) => (
                <CommandItem
                  key={item.path}
                  onSelect={() => {
                    navigate(item.path);
                    setSearchOpen(false);
                  }}
                >
                  <item.icon className="mr-2 h-4 w-4" />
                  <span>{item.label}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          ))}
          <CommandSeparator />
          <CommandGroup heading="Quick Actions">
            <CommandItem>
              <MessageSquare className="mr-2 h-4 w-4" />
              <span>Chat with AI Assistant</span>
              <CommandShortcut>⌘I</CommandShortcut>
            </CommandItem>
            <CommandItem>
              <AlertTriangle className="mr-2 h-4 w-4" />
              <span>View Active Alerts</span>
              <CommandShortcut>⌘A</CommandShortcut>
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  );
}

function FileText(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  );
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  if (days < 30) return `${days}d ago`
  return new Date(ts).toLocaleDateString()
}
