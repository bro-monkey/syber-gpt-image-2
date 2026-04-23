import { useEffect, useState } from 'react';
import { Activity, ArrowRight, CreditCard } from 'lucide-react';
import { BalanceInfo, LedgerEntry, formatBalance, formatDate, getBalance, getLedger } from '../api';

export default function Billing() {
  const [balance, setBalance] = useState<BalanceInfo>();
  const [ledger, setLedger] = useState<LedgerEntry[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([getBalance(), getLedger(50)])
      .then(([balanceData, ledgerData]) => {
        setBalance(balanceData);
        setLedger(ledgerData.items);
      })
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="md:ml-64 px-6 md:px-12 py-8 max-w-[1440px] mx-auto min-h-screen pt-24 pb-12 bg-[radial-gradient(ellipse_at_top,var(--color-surface-container-high),var(--color-background))] font-mono">
      <div className="flex flex-col gap-2 mb-10 border-b border-white/10 pb-6">
        <div className="flex items-center gap-2 text-[10px] text-primary uppercase font-bold tracking-widest">
          <span className="w-4 h-[1px] bg-primary"></span> Billing
        </div>
        <h1 className="text-4xl md:text-5xl text-on-surface font-bold tracking-tighter">BALANCE_</h1>
      </div>

      {error && <div className="mb-6 border border-error/40 bg-error/10 p-4 text-error text-xs">{error}</div>}

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-1 bg-black border border-secondary/30 p-6">
          <div className="flex items-center gap-2 text-secondary text-[10px] uppercase tracking-widest mb-6">
            <CreditCard size={16} /> Sub2API Remaining
          </div>
          <div className="text-5xl text-white font-black tracking-tighter">{formatBalance(balance)}</div>
          <div className="mt-4 text-xs text-white/40">{balance?.ok ? 'Synced from /v1/usage' : balance?.message || 'API key not configured'}</div>
        </div>

        <div className="lg:col-span-2 bg-black border border-primary/20 p-6">
          <div className="flex items-center gap-2 text-primary text-[10px] uppercase tracking-widest mb-6">
            <Activity size={16} /> Local Ledger
          </div>
          <div className="divide-y divide-white/5">
            {ledger.length === 0 && <div className="py-8 text-white/40 text-xs uppercase">NO LEDGER DATA</div>}
            {ledger.map((item) => (
              <div key={item.id} className="py-4 flex items-center justify-between gap-4 text-xs">
                <div>
                  <div className="text-white">{item.description}</div>
                  <div className="text-white/40 mt-1">{formatDate(item.created_at)}</div>
                </div>
                <div className="text-secondary flex items-center gap-2">
                  {item.amount.toFixed(4)} {item.currency}
                  <ArrowRight size={12} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
