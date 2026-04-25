import { useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';

type MasonryGridProps<T> = {
  items: T[];
  getKey: (item: T, index: number) => string;
  renderItem: (item: T, index: number) => ReactNode;
};

function getColumnCount() {
  if (typeof window === 'undefined') return 1;
  if (window.matchMedia('(min-width: 1280px)').matches) return 4;
  if (window.matchMedia('(min-width: 1024px)').matches) return 3;
  if (window.matchMedia('(min-width: 640px)').matches) return 2;
  return 1;
}

export default function MasonryGrid<T>({ items, getKey, renderItem }: MasonryGridProps<T>) {
  const [columnCount, setColumnCount] = useState(getColumnCount);

  useEffect(() => {
    const updateColumnCount = () => setColumnCount(getColumnCount());
    updateColumnCount();
    window.addEventListener('resize', updateColumnCount);
    return () => window.removeEventListener('resize', updateColumnCount);
  }, []);

  const columns = useMemo(() => {
    const nextColumns: Array<Array<{ item: T; index: number }>> = Array.from({ length: columnCount }, () => []);
    items.forEach((item, index) => {
      nextColumns[index % columnCount].push({ item, index });
    });
    return nextColumns;
  }, [columnCount, items]);

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {columns.map((column, columnIndex) => (
        <div className="flex min-w-0 flex-col gap-6" key={columnIndex}>
          {column.map(({ item, index }) => (
            <div key={getKey(item, index)}>{renderItem(item, index)}</div>
          ))}
        </div>
      ))}
    </div>
  );
}
