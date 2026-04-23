import { Link, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { AccountInfo, formatBalance, getAccount } from '../api';

export default function TopNavBar() {
  const location = useLocation();
  const [account, setAccount] = useState<AccountInfo | null>(null);

  useEffect(() => {
    getAccount().then(setAccount).catch(() => setAccount(null));
  }, []);

  return (
    <header className="fixed top-0 left-0 w-full z-[100] flex justify-between items-center px-6 h-16 bg-surface-bright border-b border-primary/30 shadow-[0_0_20px_rgba(0,243,255,0.1)] shrink-0 font-mono">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 bg-primary rounded-sm flex items-center justify-center">
            <div className="w-6 h-6 border-2 border-background rotate-45"></div>
          </div>
          <Link to="/" className="text-2xl font-black italic tracking-tighter text-white hover:text-primary transition-colors">
            CYBER<span className="text-secondary">GEN</span>
          </Link>
        </div>
        <nav className="hidden md:flex gap-6">
          <Link
            to="/history"
            className={`text-xs uppercase tracking-widest font-bold px-3 py-2 transition-all duration-300 hover:bg-primary/10 hover:text-primary ${
              location.pathname === '/history' ? 'text-primary border-b-2 border-primary' : 'text-on-surface-variant'
            }`}
          >
            History
          </Link>
        </nav>
      </div>
      <div className="flex items-center gap-6">
        <div className="hidden md:flex items-center gap-4">
          <div className="flex flex-col items-end">
            <span className="text-[10px] uppercase text-on-surface-variant">System Status</span>
            <span className="text-xs text-tertiary flex items-center gap-1">
              <span className={`w-1.5 h-1.5 rounded-full ${account?.user.api_key_set ? 'bg-tertiary animate-pulse' : 'bg-error'}`}></span>
              API: {account?.user.api_key_set ? 'ONLINE' : 'NO_KEY'}
            </span>
          </div>
          <div className="h-10 px-4 bg-surface-container-highest border border-primary/20 flex items-center gap-3 rounded-tr-xl">
            <span className="text-xs uppercase text-on-surface-variant">Credits</span>
            <span className="font-bold text-lg text-secondary">⚡ {formatBalance(account?.balance)}</span>
            <Link to="/billing" className="ml-2 px-3 py-1 bg-secondary text-white text-[10px] font-bold uppercase hover:bg-secondary/80 transition-colors shadow-[0_0_10px_rgba(255,0,255,0.3)]">
              Top Up
            </Link>
          </div>
        </div>
        <Link to="/config" className="w-10 h-10 rounded-full border-2 border-secondary bg-gradient-to-tr from-secondary/20 to-transparent overflow-hidden cursor-pointer hover:border-primary transition-colors shadow-[0_0_8px_rgba(255,0,255,0.2)]">
          <img
            alt="User Profile"
            className="w-full h-full object-cover mix-blend-luminosity hover:mix-blend-normal transition-all"
            src="https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?q=80&w=150&auto=format&fit=crop"
          />
        </Link>
      </div>
    </header>
  );
}
