import { Routes, Route } from 'react-router-dom';
import TopNavBar from './components/TopNavBar';
import SideNavBar from './components/SideNavBar';
import Home from './pages/Home';
import History from './pages/History';
import Config from './pages/Config';

export default function App() {
  return (
    <div className="min-h-screen bg-background text-on-background font-mono overflow-x-hidden selection:bg-secondary-container selection:text-secondary">
      <TopNavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/history" element={
          <>
            <SideNavBar />
            <History />
          </>
        } />
        <Route path="/config" element={
          <>
            <SideNavBar />
            <Config />
          </>
        } />
      </Routes>
    </div>
  );
}
