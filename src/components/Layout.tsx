import React from 'react';
import { 
  LayoutDashboard, 
  FileText, 
  Pill, 
  AlertTriangle, 
  UserRound, 
  BarChart3, 
  Settings,
  Search,
  Bell,
  ChevronRight,
  Menu
} from 'lucide-react';
import { cn } from '@/src/lib/utils';

interface SidebarItemProps {
  icon: any;
  label: string;
  active?: boolean;
  onClick: () => void;
  key?: string | number;
}

const SidebarItem = ({ icon: Icon, label, active, onClick }: SidebarItemProps) => (
  <button
    onClick={onClick}
    className={cn(
      "flex items-center gap-3 px-3 py-2.5 w-full transition-all duration-200 font-headline text-sm rounded-lg group",
      active 
        ? "text-primary bg-surface-container-lowest shadow-sm font-semibold scale-95" 
        : "text-on-surface-variant hover:text-primary hover:translate-x-1"
    )}
  >
    <Icon className={cn("w-5 h-5", active && "fill-primary/10")} />
    <span>{label}</span>
  </button>
);

interface LayoutProps {
  children: React.ReactNode;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export default function Layout({ children, activeTab, setActiveTab }: LayoutProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'call-logs', label: 'Call Logs', icon: FileText },
    { id: 'medicines', label: 'Medicines', icon: Pill },
    { id: 'escalations', label: 'Escalations', icon: AlertTriangle },
    { id: 'doctors', label: 'Doctors', icon: UserRound },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <div className="flex min-h-screen bg-surface">
      {/* Sidebar - Desktop */}
      <aside className="hidden md:flex flex-col h-screen w-64 bg-surface-container-low py-6 px-4 gap-2 sticky top-0 overflow-y-auto no-scrollbar border-r border-surface-container">
        <div className="mb-8 px-2">
          <h1 className="text-lg font-black text-primary font-headline tracking-tight uppercase">Immihelp</h1>
          <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Rural Health AI</p>
        </div>
        
        <nav className="flex flex-col gap-1 flex-1">
          {menuItems.map((item) => (
            <SidebarItem
              key={item.id}
              icon={item.icon}
              label={item.label}
              active={activeTab === item.id}
              onClick={() => setActiveTab(item.id)}
            />
          ))}
        </nav>

        <div className="mt-auto pt-4 border-t border-surface-container">
          <SidebarItem
            icon={Settings}
            label="Settings"
            active={activeTab === 'settings'}
            onClick={() => setActiveTab('settings')}
          />
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="flex justify-between items-center w-full px-6 py-3 bg-surface/80 backdrop-blur-xl sticky top-0 z-50 border-b border-surface-container">
          <div className="flex items-center gap-4 flex-1">
            <button 
              className="md:hidden p-2 hover:bg-surface-container rounded-lg"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="relative w-full max-w-md group hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant group-focus-within:text-primary transition-colors" />
              <input 
                type="text" 
                placeholder="Search logs, patients, or data..."
                className="w-full bg-surface-container-low border-none rounded-full py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-primary-container focus:bg-surface-container-lowest transition-all outline-none"
              />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2 text-on-surface-variant hover:bg-surface-container rounded-full transition-colors relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full border-2 border-surface"></span>
            </button>
            
            <div className="h-8 w-[1px] bg-surface-container-high mx-1 hidden sm:block"></div>
            
            <div className="flex items-center gap-3 pl-2">
              <div className="text-right hidden sm:block">
                <p className="text-xs font-bold text-on-surface">Dr. Sarah Chen</p>
                <p className="text-[10px] text-on-surface-variant">System Admin</p>
              </div>
              <img 
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuCiupqUSS685tJZu75vOip89DlbIIK0vMedLbDS6EDD5avvzXp8FaNRQMqD9A2N4BbwIb7zgxzRcYonF8uH1cFA5Lb7YC8XRNf2eKDGF6AeB1H6K0x_FwUZsgrKVBOezzHrfJrXJzt0Yey50wiRtx0xLO6q8xkLFXhJWziv83leHb3cAGSv50VGEru_j0uWDQUirERsmiQP0tEOkEWwuk5EvdIDAMKnW9MGtlrXSFk9WtXY_n2k1Z92YJa8r2ehNEF0QrZIBEkE-ziP" 
                alt="Profile"
                className="w-9 h-9 rounded-full object-cover border-2 border-primary-container"
              />
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>

        {/* Footer */}
        <footer className="flex flex-col sm:flex-row justify-between items-center px-8 py-6 w-full mt-auto bg-surface-container-low border-t border-surface-container">
          <div className="flex flex-col gap-1 mb-4 sm:mb-0">
            <span className="text-xs font-bold text-primary font-headline uppercase tracking-wider">Immihelp</span>
            <p className="text-[10px] text-on-surface-variant">Immihelp Internal Admin Panel — Rural Healthcare Voice AI</p>
          </div>
          <div className="flex gap-6 items-center">
            <a href="#" className="text-[10px] font-medium text-on-surface-variant hover:text-primary transition-colors">Privacy Policy</a>
            <a href="#" className="text-[10px] font-medium text-on-surface-variant hover:text-primary transition-colors">Support</a>
            <span className="text-[10px] bg-surface-container-high text-on-surface-variant px-2 py-0.5 rounded font-bold">v2.4.0-Stable</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
