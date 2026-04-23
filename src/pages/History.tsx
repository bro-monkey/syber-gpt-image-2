import { Search, Filter, Download, Trash2, RefreshCw, ArrowDown } from 'lucide-react';

const historyMock = [
  {
    id: 'ID:001A',
    img: 'https://images.unsplash.com/photo-1605806616949-1e87b487cb2a?q=80&w=600&auto=format&fit=crop',
    prompt: 'Neon drenched alleyway, volumetric fog, high contrast, 8k resolution, ray tracing',
    date: '2023.10.24',
    res: '1920x1080',
    colorMode: 'primary'
  },
  {
    id: 'ID:002B',
    img: 'https://images.unsplash.com/photo-1620336655055-088d06e36bf0?q=80&w=600&auto=format&fit=crop',
    prompt: 'Macro photography of synthetic iris, green glowing circuit patterns, photorealistic',
    date: '2023.10.23',
    res: '1024x1024',
    colorMode: 'secondary'
  },
  {
    id: 'ID:003C',
    img: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=600&auto=format&fit=crop',
    prompt: 'Vaporwave aesthetic wireframe terrain, synthwave sun, magenta grid, retrowave vibes',
    date: '2023.10.20',
    res: '1920x1080',
    colorMode: 'primary'
  },
  {
    id: 'ID:004D',
    img: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=600&auto=format&fit=crop',
    prompt: 'Quantum computing mainframe interior, dense cabling, cold blue atmospheric lighting',
    date: '2023.10.18',
    res: '1024x1024',
    colorMode: 'secondary'
  }
];

const getColorClasses = (colorMode: string) => {
  if (colorMode === 'primary') {
    return {
      borderHover: 'hover:border-primary/50',
      textId: 'text-primary',
      bgTag: 'bg-primary/10 border-primary/30',
      btnBg: 'bg-primary border-primary',
      btnText: 'text-black hover:text-white',
      btnShadow: 'shadow-[0_0_10px_rgba(0,243,255,0.5)]'
    };
  }
  return {
    borderHover: 'hover:border-secondary/50',
    textId: 'text-secondary',
    bgTag: 'bg-secondary/10 border-secondary/30',
    btnBg: 'bg-secondary border-secondary',
    btnText: 'text-white hover:text-black',
    btnShadow: 'shadow-[0_0_10px_rgba(255,0,255,0.5)]'
  };
};

export default function History() {
  return (
    <div className="md:ml-64 px-6 md:px-12 py-8 max-w-[1440px] mx-auto min-h-screen pt-24 pb-12 bg-[radial-gradient(ellipse_at_top,var(--color-surface-container-high),var(--color-background))] font-mono">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-10 gap-6 border-b border-white/10 pb-6">
        <div className="flex flex-col gap-2">
           <div className="flex items-center gap-2 text-[10px] text-primary uppercase font-bold tracking-widest">
              <span className="w-4 h-[1px] bg-primary"></span> Neural Database
           </div>
          <h1 className="text-4xl md:text-5xl text-on-surface font-bold tracking-tighter">ARCHIVE_</h1>
          <p className="text-white/50 text-sm">Access and manage previously synthesized visual data structures.</p>
        </div>
        
        <div className="flex gap-4 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-primary/50" size={16} />
            <input 
              className="w-full bg-black border border-primary/20 focus:border-primary focus:ring-0 text-primary pl-10 py-2 font-code-data transition-colors placeholder:text-primary/20 outline-none text-xs shadow-inner" 
              placeholder="QUERY_LOGS..." 
              type="text" 
            />
          </div>
          <button className="bg-black border border-primary/20 p-2 hover:border-primary hover:bg-primary/5 transition-colors flex items-center justify-center">
            <Filter size={16} className="text-primary" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {historyMock.map((item) => {
          const colors = getColorClasses(item.colorMode);
          return (
          <div 
            key={item.id} 
            className={`group relative aspect-[4/5] bg-black border border-white/10 overflow-hidden flex flex-col ${colors.borderHover} transition-all duration-300`}
          >
            <div className={`absolute top-3 right-3 z-10 px-2 py-1 border text-[9px] tracking-widest uppercase ${colors.textId} ${colors.bgTag} backdrop-blur-sm`}>
              {item.id}
            </div>
            
            <img 
              alt={item.prompt} 
              className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-all duration-500" 
              src={item.img} 
            />
            
            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent opacity-100 flex flex-col justify-end p-5">
               <div className="flex justify-between items-center mb-4 translate-y-8 group-hover:translate-y-0 opacity-0 group-hover:opacity-100 transition-all duration-300">
                  <button className={`w-8 h-8 rounded-none border border-white/20 bg-white/5 flex items-center justify-center text-white hover:text-primary hover:border-primary transition-all backdrop-blur-md`} title="Download">
                    <Download size={14} />
                  </button>
                  <button className="w-8 h-8 rounded-none border border-error/20 bg-error/5 flex items-center justify-center text-error hover:bg-error/20 transition-all backdrop-blur-md" title="Delete">
                    <Trash2 size={14} />
                  </button>
               </div>
               
               <div>
                  <p className={`text-sm text-on-surface line-clamp-2 mb-2 ${colors.textId} transition-colors min-h-[40px]`}>
                    {item.prompt}
                  </p>
                  <div className="flex items-center gap-3 text-white/40 text-[10px] uppercase tracking-wider mt-2 mb-4 font-bold">
                    <span>{item.date}</span>
                    <span className="w-1 h-1 rounded-full bg-white/20"></span>
                    <span>{item.res}</span>
                  </div>
               </div>
               
               <button className={`w-full py-3 ${colors.btnBg} ${colors.btnText} font-black text-xs uppercase flex items-center justify-center gap-2 ${colors.btnShadow} transform translate-y-12 group-hover:translate-y-0 transition-all duration-300 hover:bg-white hover:border-white shadow-white/50`}>
                 <RefreshCw size={14} />
                 Re-Generate
               </button>
            </div>
          </div>
          );
        })}
      </div>

      <div className="mt-12 flex justify-center">
        <button className="border border-primary/30 hover:border-primary text-primary px-8 py-3 uppercase tracking-widest transition-colors flex items-center gap-2 text-xs bg-primary/5 shadow-[0_0_15px_rgba(0,243,255,0.1)]">
          LOAD_MORE_DATA
          <ArrowDown size={14} />
        </button>
      </div>
    </div>
  );
}
