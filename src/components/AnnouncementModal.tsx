import { Bell, X } from 'lucide-react';
import { useSite } from '../site';

export default function AnnouncementModal() {
  const { announcementOpen, closeAnnouncement, siteSettings, t } = useSite();

  if (!announcementOpen) {
    return null;
  }

  const announcement = siteSettings?.announcement;
  const hasContent = Boolean(announcement?.title || announcement?.body);

  return (
    <div className="fixed inset-0 z-[120] flex items-center justify-center bg-black/75 px-4 backdrop-blur-sm" onClick={closeAnnouncement}>
      <div
        className="w-full max-w-2xl border border-primary/30 bg-surface-container-high p-6 shadow-[0_0_40px_rgba(0,243,255,0.18)]"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-4 flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center border border-secondary/40 bg-secondary/10 text-secondary">
              <Bell size={18} />
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-widest text-secondary">{t('top_announcement')}</div>
              <h2 className="mt-1 text-xl font-bold text-white">{announcement?.title || t('top_announcement')}</h2>
            </div>
          </div>
          <button
            className="flex h-10 w-10 items-center justify-center border border-white/10 text-white/60 transition-colors hover:border-primary hover:text-primary"
            type="button"
            onClick={closeAnnouncement}
            title={t('modal_close')}
          >
            <X size={16} />
          </button>
        </div>

        <div className="max-h-[60vh] overflow-y-auto border border-white/10 bg-black/40 p-5 text-sm leading-7 text-white/80 whitespace-pre-wrap">
          {hasContent ? announcement?.body || announcement?.title : t('announcement_empty')}
        </div>

        <div className="mt-5 flex justify-end">
          <button
            className="border border-primary/30 px-5 py-2 text-xs font-bold uppercase tracking-widest text-primary transition-colors hover:bg-primary/10"
            type="button"
            onClick={closeAnnouncement}
          >
            {t('modal_close')}
          </button>
        </div>
      </div>
    </div>
  );
}
