import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { ViewerInfo, getSession } from './api';

type AuthContextValue = {
  viewer: ViewerInfo | null;
  loading: boolean;
  refresh: () => Promise<void>;
  setViewer: (viewer: ViewerInfo | null) => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [viewer, setViewer] = useState<ViewerInfo | null>(null);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    try {
      const session = await getSession();
      setViewer(session);
    } catch {
      setViewer(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh().catch(() => setLoading(false));
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    viewer,
    loading,
    refresh,
    setViewer,
  }), [viewer, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return context;
}
