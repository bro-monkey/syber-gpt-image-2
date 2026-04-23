import { EyeOff, Save, Activity, ShieldAlert, ArrowRight, Server } from 'lucide-react';

export default function Config() {
  return (
    <div className="md:ml-64 px-6 md:px-12 py-8 max-w-[1440px] mx-auto min-h-screen pt-24 pb-12 bg-[radial-gradient(ellipse_at_top,var(--color-surface-container-high),var(--color-background))] font-mono">
      <section className="flex flex-col md:flex-row items-start md:items-center gap-6 mb-12">
        <div className="w-24 h-24 border border-secondary relative bg-black p-1 shadow-[0_0_15px_rgba(255,0,255,0.2)]">
          <div className="absolute -top-1 -left-1 w-2 h-2 bg-secondary"></div>
          <div className="absolute -bottom-1 -right-1 w-2 h-2 bg-secondary"></div>
          <img 
            alt="Avatar" 
            className="w-full h-full object-cover filter grayscale sepia-[.2] hue-rotate-[250deg]" 
            src="https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?q=80&w=150&auto=format&fit=crop" 
          />
        </div>
        <div className="flex flex-col gap-1">
          <div className="text-[10px] text-secondary uppercase font-bold tracking-widest flex items-center gap-2">
            <span className="w-4 h-[1px] bg-secondary"></span> User Profile
          </div>
          <h1 className="text-3xl md:text-5xl text-on-surface font-bold">NEON_USER_404</h1>
          <div className="flex items-center gap-4 text-xs mt-2 border border-white/10 bg-white/5 py-1 px-3 w-fit">
            <span className="text-white/50 uppercase">Session: <span className="text-tertiary">Active</span></span>
            <span className="text-white/20">|</span>
            <span className="text-primary uppercase flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-primary rounded-full"></span> Credits: 8,402
            </span>
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-8 bg-black border border-primary/20 p-6 md:p-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-3 text-[9px] text-primary/40 uppercase border-b border-l border-primary/20 bg-primary/5">Node_CFG_01</div>
          
          <h2 className="text-xl text-primary mb-8 uppercase flex items-center gap-3 font-bold border-b border-primary/20 pb-4">
            <Server className="text-primary" size={20} />
            External Proxy Binding
          </h2>

          <div className="bg-primary/5 border border-primary/20 border-l-2 border-l-tertiary p-5 mb-8 flex gap-4 relative">
            <ShieldAlert className="text-tertiary mt-1 shrink-0" size={20} />
            <div>
              <h3 className="text-white mb-1 font-bold tracking-widest text-[10px] uppercase">Secure Tunnel Active</h3>
              <p className="text-white/50 text-xs leading-relaxed">
                Your requests are routed through an encrypted backend proxy to bypass browser CORS restrictions. Keys are volatile and strictly bound to the current session hash.
              </p>
            </div>
          </div>

          <form className="flex flex-col gap-6">
            <div className="flex flex-col gap-2 relative">
              <label className="text-secondary text-[10px] uppercase tracking-widest font-bold mb-1" htmlFor="api_key">OPENAI_PROXY_KEY</label>
              <div className="relative">
                <input 
                  className="w-full bg-surface-container border border-white/10 focus:border-secondary focus:ring-0 text-white p-3 transition-colors duration-300 placeholder:text-white/20 outline-none text-sm shadow-inner" 
                  id="api_key" 
                  placeholder="sk-..." 
                  type="password" 
                  defaultValue="sk-1234567890abcdef1234567890abcdef" 
                />
                <button className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-secondary transition-colors" type="button">
                  <EyeOff size={16} />
                </button>
              </div>
              <span className="text-[9px] text-white/30 text-right uppercase">Hash: 0x9A4F2AB8</span>
            </div>

            <div className="pt-6 flex justify-end border-t border-white/10 mt-4">
              <button 
                className="bg-secondary text-white font-bold px-8 py-3 uppercase tracking-widest hover:bg-white hover:text-black transition-colors flex items-center gap-2 text-xs shadow-[0_0_15px_rgba(255,0,255,0.3)]" 
                type="button"
              >
                <Save size={14} />
                SAVE CONFIG
              </button>
            </div>
          </form>
        </div>

        <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
          <div className="bg-black border border-white/10 p-6 relative flex-1">
            <h3 className="text-primary mb-6 uppercase flex items-center gap-2 font-bold tracking-wider text-[10px] border-b border-primary/20 pb-4">
              <Activity size={16} />
              Consumption Matrix
            </h3>
            
            <div className="flex flex-col gap-0 text-xs">
              <div className="flex justify-between items-center py-3 border-b border-white/5">
                <div className="flex flex-col">
                  <span className="text-white">GEN_REQ_#892</span>
                  <span className="text-[9px] text-white/40 mt-1 uppercase">12:45:01 UTC</span>
                </div>
                <span className="text-secondary">-12 CR</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-white/5">
                <div className="flex flex-col">
                  <span className="text-white">GEN_REQ_#891</span>
                  <span className="text-[9px] text-white/40 mt-1 uppercase">11:22:14 UTC</span>
                </div>
                <span className="text-secondary">-8 CR</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-white/5">
                <div className="flex flex-col">
                  <span className="text-white">UPL_IMG_#104</span>
                  <span className="text-[9px] text-white/40 mt-1 uppercase">09:15:40 UTC</span>
                </div>
                <span className="text-tertiary">+50 CR</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <div className="flex flex-col">
                  <span className="text-white">GEN_REQ_#890</span>
                  <span className="text-[9px] text-white/40 mt-1 uppercase">08:01:22 UTC</span>
                </div>
                <span className="text-secondary">-24 CR</span>
              </div>
            </div>

            <button className="w-full mt-6 py-2 border border-primary/30 text-primary text-[10px] uppercase tracking-widest hover:bg-primary/10 transition-colors flex items-center justify-center gap-2">
              VIEW FULL LEDGER <ArrowRight size={12} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
