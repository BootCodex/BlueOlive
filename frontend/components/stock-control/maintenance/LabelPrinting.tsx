'use client';

import { useMemo, useState } from 'react';
import { ArrowLeft, Minus, Plus, Printer, Trash2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { printLabels, LabelLayout, LabelStockItem } from '@/lib/labelPrintUtils';

interface LabelPrintingProps {
  onBack: () => void;
}

interface SelectedLabel {
  item: LabelStockItem;
  quantity: number;
}

export default function LabelPrinting({ onBack }: LabelPrintingProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [layout, setLayout] = useState<LabelLayout>('sheet');
  const [selected, setSelected] = useState<Record<string, SelectedLabel>>({});

  const { data: items = [], isFetching } = useQuery({
    queryKey: ['stock-items-for-labels', searchTerm],
    queryFn: async () => {
      const params = new URLSearchParams({ page_size: '25', ordering: 'stock_code', search: searchTerm });
      const response = await api.get(`/api/stock-control/stock-items/?${params}`);
      return (response.data.results || response.data) as LabelStockItem[];
    },
    enabled: searchTerm.trim().length > 0,
  });

  const selectedList = useMemo(() => Object.values(selected), [selected]);
  const totalLabels = selectedList.reduce((sum, s) => sum + s.quantity, 0);

  const addItem = (item: LabelStockItem) => {
    setSelected((prev) => ({
      ...prev,
      [item.stock_code]: { item, quantity: prev[item.stock_code]?.quantity ?? 1 },
    }));
  };

  const removeItem = (stockCode: string) => {
    setSelected((prev) => {
      const next = { ...prev };
      delete next[stockCode];
      return next;
    });
  };

  const setQuantity = (stockCode: string, quantity: number) => {
    setSelected((prev) => ({
      ...prev,
      [stockCode]: { ...prev[stockCode], quantity: Math.max(1, quantity) },
    }));
  };

  const handlePrint = () => {
    if (selectedList.length === 0) return;
    printLabels(
      selectedList.map(({ item, quantity }) => ({ item, quantity })),
      layout
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={onBack}
          className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
        >
          <ArrowLeft size={20} />
          Back
        </button>
        <h3 className="text-2xl font-bold">Print Shelf / Barcode Labels</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">Search Stock Items (code, description, or barcode)</label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Type to search..."
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Label Layout</label>
          <select
            value={layout}
            onChange={(e) => setLayout(e.target.value as LabelLayout)}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="sheet">A4 Sheet (multiple labels per page)</option>
            <option value="roll">Thermal Roll (one label per page, 50x30mm)</option>
          </select>
        </div>
      </div>

      {searchTerm.trim().length > 0 && (
        <div className="border rounded-lg mb-6 max-h-64 overflow-y-auto">
          {isFetching && <div className="p-4 text-sm text-gray-500">Searching...</div>}
          {!isFetching && items.length === 0 && (
            <div className="p-4 text-sm text-gray-500">No matching stock items.</div>
          )}
          {items.map((item) => (
            <button
              key={item.stock_code}
              onClick={() => addItem(item)}
              className="w-full flex items-center justify-between px-4 py-2 text-left border-b last:border-b-0 hover:bg-blue-50"
            >
              <div>
                <span className="font-medium">{item.stock_code}</span>
                <span className="text-gray-500 ml-2">{item.description}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                {item.barcode && <span>{item.barcode}</span>}
                <Plus size={16} className="text-blue-600" />
              </div>
            </button>
          ))}
        </div>
      )}

      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Labels to Print ({totalLabels})</h4>
        {selectedList.length === 0 ? (
          <div className="text-sm text-gray-500 border rounded-lg p-4">
            Search above and select stock items to add them here.
          </div>
        ) : (
          <div className="border rounded-lg divide-y">
            {selectedList.map(({ item, quantity }) => (
              <div key={item.stock_code} className="flex items-center justify-between px-4 py-2">
                <div>
                  <span className="font-medium">{item.stock_code}</span>
                  <span className="text-gray-500 ml-2">{item.description}</span>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setQuantity(item.stock_code, quantity - 1)}
                    className="p-1 rounded hover:bg-gray-100"
                    aria-label="Decrease quantity"
                  >
                    <Minus size={16} />
                  </button>
                  <input
                    type="number"
                    min={1}
                    value={quantity}
                    onChange={(e) => setQuantity(item.stock_code, parseInt(e.target.value, 10) || 1)}
                    className="w-16 text-center border rounded px-2 py-1"
                  />
                  <button
                    onClick={() => setQuantity(item.stock_code, quantity + 1)}
                    className="p-1 rounded hover:bg-gray-100"
                    aria-label="Increase quantity"
                  >
                    <Plus size={16} />
                  </button>
                  <button
                    onClick={() => removeItem(item.stock_code)}
                    className="p-1 rounded hover:bg-red-50 text-red-600"
                    aria-label="Remove item"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex gap-4 justify-center">
        <button
          onClick={onBack}
          className="px-6 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition"
        >
          Cancel
        </button>
        <button
          onClick={handlePrint}
          disabled={selectedList.length === 0}
          className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
        >
          <Printer size={20} />
          Print {totalLabels > 0 ? `${totalLabels} ` : ''}Label{totalLabels === 1 ? '' : 's'}
        </button>
      </div>
    </div>
  );
}
