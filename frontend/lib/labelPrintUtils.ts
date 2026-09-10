/**
 * Shelf / Barcode Label Print Utilities
 *
 * Generates CODE128 barcode + price shelf labels for stock items and prints
 * them via the browser print dialog — same window.open + document.write
 * pattern as printUtils.ts and PrintStockTakeForms.tsx — so it works with
 * any printer installed at the OS level: sheet-fed label paper on a normal
 * printer, or a thermal label printer that registers as a Windows printer.
 *
 * Barcodes are rendered to SVG with JsBarcode *before* the print window is
 * opened (on a detached, offscreen <svg> element in this document), then the
 * resulting markup is embedded as a plain string in the print window's HTML.
 * The print window itself never needs to load JsBarcode.
 */

import JsBarcode from 'jsbarcode';

function escapeHtml(value: unknown): string {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatCurrency(value: number): string {
  return `R ${(value || 0).toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export interface LabelStockItem {
  stock_code: string;
  description: string;
  barcode?: string | null;
  selling_price_1?: number | string;
}

export interface LabelPrintRequest {
  item: LabelStockItem;
  quantity: number;
}

export type LabelLayout = 'sheet' | 'roll';

/**
 * Render a CODE128 barcode as SVG markup. The code printed on the label is
 * the item's own barcode when set, otherwise its stock_code — every item
 * gets a scannable label even if no barcode/EAN was ever captured for it.
 */
function renderBarcodeSvg(value: string): string {
  if (typeof document === 'undefined' || !value) return '';
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  try {
    JsBarcode(svg, value, {
      format: 'CODE128',
      displayValue: false,
      margin: 0,
      height: 40,
      width: 1.6,
    });
  } catch {
    // CODE128 can't encode every possible stock_code/barcode value (e.g.
    // stray control characters from a legacy import) — skip the barcode
    // rather than letting one bad value break the whole print run.
    return '';
  }
  return svg.outerHTML;
}

const LAYOUT_CSS: Record<LabelLayout, string> = {
  // Sheet: multiple labels per A4 page, e.g. for pre-cut label sheets.
  sheet: `
    @page { size: A4; margin: 10mm; }
    .label-sheet { display: flex; flex-wrap: wrap; gap: 3mm; }
    .label { width: 63mm; height: 33mm; border: 1px dashed #bbb; }
  `,
  // Roll: one label per physical page, sized for a common 50x30mm thermal
  // label roll. Printer driver handles continuous feed.
  roll: `
    @page { size: 50mm 30mm; margin: 2mm; }
    .label-sheet { display: block; }
    .label { width: 46mm; height: 26mm; page-break-after: always; }
  `,
};

/**
 * Build the print-window HTML for a batch of labels. Each request repeats
 * `quantity` times (one physical label per unit going on the shelf/stock).
 */
export function generateLabelSheetHTML(requests: LabelPrintRequest[], layout: LabelLayout = 'sheet'): string {
  const labels: string[] = [];
  for (const { item, quantity } of requests) {
    const code = (item.barcode || item.stock_code || '').trim();
    const barcodeSvg = renderBarcodeSvg(code);
    const labelHtml = `
        <div class="label">
          <div class="label-desc">${escapeHtml(item.description || item.stock_code)}</div>
          <div class="label-barcode">${barcodeSvg}</div>
          <div class="label-code">${escapeHtml(code)}</div>
          <div class="label-price">${formatCurrency(Number(item.selling_price_1 || 0))}</div>
        </div>
    `;
    const copies = Math.max(1, Math.floor(quantity) || 1);
    for (let i = 0; i < copies; i++) {
      labels.push(labelHtml);
    }
  }

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Price Labels</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: Arial, sans-serif; }
    .label {
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      text-align: center; padding: 2mm; overflow: hidden;
    }
    .label-desc { font-size: 8pt; font-weight: bold; line-height: 1.1; max-height: 2.2em; overflow: hidden; }
    .label-barcode svg { width: 100%; height: 10mm; }
    .label-code { font-size: 6pt; color: #333; letter-spacing: 1px; }
    .label-price { font-size: 12pt; font-weight: bold; margin-top: 1mm; }
    ${LAYOUT_CSS[layout]}
  </style>
</head>
<body>
  <div class="label-sheet">
    ${labels.join('')}
  </div>
</body>
</html>
  `;
}

/**
 * Open the print window and trigger the browser print dialog, mirroring
 * printUtils.ts's openPrintWindow.
 */
export function printLabels(requests: LabelPrintRequest[], layout: LabelLayout = 'sheet'): void {
  const html = generateLabelSheetHTML(requests, layout);
  const printWindow = window.open('', '_blank', 'width=800,height=600');
  if (printWindow) {
    printWindow.document.write(html);
    printWindow.document.close();
    printWindow.onload = () => {
      printWindow.print();
    };
  }
}
