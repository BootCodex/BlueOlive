'use client';

import StockTransactions from '@/components/stock-control/transactions/StockTransactions';

export default function StockControlTransactionsPage() {
  const handleBack = () => {
    window.history.back();
  };

  return (
    <div className="p-6">
      <StockTransactions onBack={handleBack} />
    </div>
  );
}

