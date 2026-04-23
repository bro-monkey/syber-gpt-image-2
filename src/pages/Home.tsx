import { useState } from 'react';
import { ImagePlus, Grid, List, RefreshCw } from 'lucide-react';

const mockFeed = [
  {
    id: '#001_CYBER',
    img: 'https://images.unsplash.com/photo-1605806616949-1e87b487cb2a?q=80&w=600&auto=format&fit=crop',
    prompt: 'A neon-lit cyberpunk street alley, rain slicked pavement reflecting cyan and magenta holographic advertisements. Tall imposing brutalist skyscrapers in the background.'
  },
  {
    id: '#002_MECHA',
    img: 'https://images.unsplash.com/photo-1535295972055-1c762f4483e5?q=80&w=600&auto=format&fit=crop',
    prompt: 'Heavy tactical mecha suit glowing with internal neon orange energy. Standing in a desolate, post-apocalyptic wasteland under a dark sky.'
  },
  {
    id: '#003_PORTRAIT',
    img: 'https://images.unsplash.com/photo-1620336655055-088d06e36bf0?q=80&w=600&auto=format&fit=crop',
    prompt: 'Close up portrait of a rogue hacker with intricate glowing cybernetic facial implants. Harsh rim lighting in vibrant magenta and deep blue.'
  },
  {
    id: '#004_VEHICLE',
    img: 'https://images.unsplash.com/photo-1542382257-80da9fb9f5abc?q=80&w=600&auto=format&fit=crop',
    prompt: 'Sleek hover motorcycle speeding through a dark, rain-drenched highway tunnel. Trailing light streaks of bright cyan.'
  },
  {
    id: '#005_LANDSCAPE',
    img: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=600&auto=format&fit=crop',
    prompt: 'Surreal alien landscape with massive glowing crystal monoliths emitting toxic green light. A huge shattered moon in the background sky.'
  },
  {
    id: '#006_INTERIOR',
    img: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=600&auto=format&fit=crop',
    prompt: 'Cluttered hacker den illuminated only by the glow of dozens of floating holographic screens displaying scrolling red code.'
  }
];

export default function Home() {
  const [promptValue, setPromptValue] = useState('');

  return (
    <div className="pt-24 pb-48 px-6 max-w-[1440px] mx-auto min-h-screen bg-[radial-gradient(ellipse_at_top,var(--color-surface-container-high),var(--color-background))] font-mono">
      <div className="flex justify-between items-end mb-8">
        <div className="flex flex-col gap-2">
           <div className="flex items-center gap-2 text-[10px] text-secondary uppercase font-bold tracking-widest">
              <span className="w-4 h-[1px] bg-secondary"></span> System.Scan
           </div>
          <h1 className="text-4xl md:text-5xl text-on-surface font-bold tracking-tighter">INSPIRATION_FEED</h1>
        </div>
        <div className="hidden sm:flex gap-2">
          <button className="w-10 h-10 border border-outline-variant flex items-center justify-center text-outline-variant hover:text-primary hover:border-primary bg-surface-container-low transition-colors">
            <Grid size={20} />
          </button>
          <button className="w-10 h-10 border border-outline-variant flex items-center justify-center text-outline-variant hover:text-primary hover:border-primary bg-surface-container-low transition-colors">
            <List size={20} />
          </button>
        </div>
      </div>

      <div className="masonry-grid flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-primary/20">
        {mockFeed.map((item) => (
          <div key={item.id} className="masonry-item relative group aspect-[3/4] border border-primary/30 overflow-hidden bg-black flex flex-col">
            <img 
              alt={item.id} 
              className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-all duration-500" 
              src={item.img} 
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
            
            <div className="absolute top-4 right-4 z-10 font-code-data text-white/50 text-[10px] border border-white/20 px-2 py-1 bg-black/50 backdrop-blur-sm shadow-[0_0_10px_rgba(0,0,0,0.5)]">
              {item.id}
            </div>

            <div className="absolute bottom-0 left-0 right-0 p-4 transform translate-y-8 group-hover:translate-y-0 transition-transform flex flex-col gap-3 backdrop-blur-sm bg-gradient-to-t from-black/90 to-transparent">
              <p className="font-body-md text-white mb-2 line-clamp-3 text-sm">{item.prompt}</p>
              <button 
                onClick={() => setPromptValue(item.prompt)}
                className="w-full py-2 bg-primary text-black font-black text-xs uppercase shadow-[0_0_10px_rgba(0,243,255,0.5)] flex items-center justify-center gap-2 hover:bg-white hover:shadow-white/50 transition-all"
              >
                <RefreshCw size={14} />
                CLONE PROMPT
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* FIXED INPUT AREA */}
      <div className="fixed bottom-6 left-6 right-6 md:left-auto md:right-auto md:w-[calc(100%-3rem)] max-w-[960px] mx-auto bg-surface-container/90 backdrop-blur-xl border border-primary/40 p-5 rounded-sm shadow-[0_-20px_40px_rgba(0,0,0,0.8)] z-50 font-mono">
        <div className="flex items-center gap-4 mb-4">
          <div className="flex items-center gap-2 text-[10px] text-white/50 border-r border-white/10 pr-4">
             <span className="w-2 h-2 bg-secondary rounded-full animate-pulse"></span> MODE: CREATION
          </div>
          <div className="text-[10px] text-primary uppercase tracking-widest truncate">
            {promptValue ? "Selected Configuration Loaded" : "Awaiting Input..."}
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 flex flex-col gap-2 relative">
            <textarea 
              value={promptValue}
              onChange={(e) => setPromptValue(e.target.value)}
              className="w-full h-20 bg-black border border-primary/20 p-3 text-sm text-primary focus:outline-none focus:border-primary placeholder:text-primary/20 resize-none shadow-inner" 
              placeholder="Enter your neural commands here..." 
            ></textarea>
            <div className="absolute top-0 right-0 p-2 text-[8px] text-primary/40 uppercase">
              UTF-8 // AI-GEN // [{promptValue.length}/500]
            </div>
          </div>
          
          <div className="flex gap-4">
             <button className="w-20 md:w-24 h-20 border border-dashed border-primary/20 flex flex-col items-center justify-center cursor-pointer hover:bg-primary/5 transition-colors group">
                 <ImagePlus className="w-6 h-6 mb-1 text-white/30 group-hover:text-primary transition-colors" />
                 <span className="text-[9px] uppercase text-white/40 group-hover:text-primary">Ref Image</span>
             </button>
            <button className="w-32 bg-primary text-black font-black flex flex-col items-center justify-center hover:scale-95 transition-transform shadow-[0_0_15px_rgba(0,243,255,0.4)]">
               <span className="text-xl mb-[-4px]">EXECUTE</span>
               <span className="text-[10px] opacity-70 italic">GENERATE</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
