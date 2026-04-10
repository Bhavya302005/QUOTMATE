import { Calculator } from 'lucide-react';

function money(value) {
  const number = Number(value || 0);
  return `₹ ${number.toFixed(2)}`;
}

export default function GSTSummary({ totals, isCalculating = false, lumpSumTotal = null }) {
  if (isCalculating) {
    return (
      <div className="border border-black bg-surface-white p-4    text-on-surface">
        <div className="flex items-center gap-2">
          <Calculator className="h-4 w-4 animate-pulse" strokeWidth={1.5} />
          Calculating…
        </div>
      </div>
    );
  }

  if (!totals) return null;

  return (
    <div className="border border-dashed border-black/30 bg-surface-container p-4">
      <h3 className="mb-3 stitch-label">Amount summary</h3>
      <div className="space-y-1.5 text-sm font-light text-on-surface">
        <div className="flex justify-between">
          <span>Subtotal</span>
          <span className="">{money(totals.subtotal)}</span>
        </div>

        {Number(totals.discount_amount || 0) > 0 && (
          <div className="flex justify-between border-b border-outline-variant pb-1">
            <span>Discount ({totals.discount_percent || 0}%)</span>
            <span className="">− {money(totals.discount_amount)}</span>
          </div>
        )}

        {totals.is_gst_on && Number(totals.cgst_amount || 0) > 0 && (
          <div className="flex justify-between">
            <span>CGST</span>
            <span className="">{money(totals.cgst_amount)}</span>
          </div>
        )}

        {totals.is_gst_on && Number(totals.sgst_amount || 0) > 0 && (
          <div className="flex justify-between">
            <span>SGST</span>
            <span className="">{money(totals.sgst_amount)}</span>
          </div>
        )}

        {totals.is_gst_on && Number(totals.igst_amount || 0) > 0 && (
          <div className="flex justify-between">
            <span>IGST</span>
            <span className="">{money(totals.igst_amount)}</span>
          </div>
        )}

        <div className="mt-2 border-t border-black pt-2">
          {totals.manual_total_amount !== null && (
            <div className="mb-1  text-[9px]   text-outline-muted">
              Manual override active
            </div>
          )}
          <div className="flex justify-between text-base font-normal text-on-surface">
            <span className=" tracking-tight">Grand total</span>
            <span className="">{money(totals.grand_total)}</span>
          </div>
        </div>

        {lumpSumTotal && Number(lumpSumTotal) > 0 && (
          <div className="mt-3 border border-black bg-surface-white p-2.5">
            <div className="flex justify-between text-sm font-normal">
              <span className=" tracking-tight">Written total</span>
              <span className="">{money(lumpSumTotal)}</span>
            </div>
            <p className="mt-1  text-[9px]  leading-relaxed  text-outline-muted">
              Lump-sum from handwritten quote; line rates may be approximate.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
