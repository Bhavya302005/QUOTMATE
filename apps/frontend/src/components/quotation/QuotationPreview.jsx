import React from 'react';
import { Link } from 'react-router-dom';
import { Download, FileDown, Pencil } from 'lucide-react';
import Button from '../common/Button';
import { useAuth } from '../../hooks/useAuth';

const VITE_API_URL = import.meta.env.VITE_API_URL || 'https://quotmate-backend.onrender.com';

function formatAmount(value) {
  return Number(value || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function formatDateDot(input) {
  const d = input ? new Date(input) : new Date();
  if (Number.isNaN(d.getTime())) return '';
  const year = d.getFullYear();
  const month = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${year}.${month}.${day}`;
}

export default function QuotationPreview({
  quotation,
  onFinalize,
  onRevertFinalization,
  onDownload,
  isFinalizing = false,
  isReverting = false,
  showActions = true,
}) {
  const { user } = useAuth();
  if (!quotation) return null;

  const finalized = (quotation.status || '').toLowerCase() === 'finalized';
  const companyDisplayName = String(user?.company_name || user?.full_name || '').toUpperCase();
  const companyAddress = String(user?.address || '').toUpperCase();
  const issueDate = formatDateDot(quotation.created_at || quotation.issue_date);
  const taxTotal = Number(quotation.cgst_amount || 0) + Number(quotation.sgst_amount || 0) + Number(quotation.igst_amount || 0);

  // Logo Resolution
  const logoUrl = user?.company_logo_url
    ? (user.company_logo_url.startsWith('http') ? user.company_logo_url : `${VITE_API_URL}${user.company_logo_url}`)
    : null;
  return (
    <div className="space-y-4">
      <div className="w-full overflow-x-auto overflow-y-hidden max-w-full pb-4">
        <div className="document-a4 bg-white p-12 flex flex-col font-['Inter'] relative selection:bg-black selection:text-white border border-neutral-200 shadow-sm mx-auto min-w-[794px] max-w-[794px] min-h-[1123px]">
          {/* Branding Header */}
        <div className="flex justify-between items-start mb-16">
          <div className="space-y-2">
            {/* Logo Box */}
            <div className="h-24 w-40 flex items-center justify-start overflow-hidden">
              {logoUrl ? (
                <img src={logoUrl} alt="Logo" className="max-h-full max-w-full object-contain" />
              ) : (
                <div className="h-16 w-16 bg-black flex items-center justify-center">
                  <span className="text-white font-bold text-2xl">{companyDisplayName.charAt(0)}</span>
                </div>
              )}
            </div>
            <div className="font-mono text-[10px] leading-tight uppercase font-light text-on-surface">
              {companyAddress && companyAddress.split(',').map((line, i) => (
                <React.Fragment key={i}>
                  {line.trim()}<br />
                </React.Fragment>
              ))}
            </div>
          </div>
          <div className="text-right">
            <h2 className="font-headline font-bold text-6xl uppercase tracking-tighter mb-4 leading-none text-on-surface">Quotation</h2>
            <div className="font-mono text-[10px] leading-relaxed uppercase font-light text-on-surface">
              <div className="font-bold mb-1"><span className="opacity-40 font-normal">BY,</span> {companyDisplayName}</div>
              <span className="opacity-40">{issueDate && 'DATE:'}</span> {issueDate}
            </div>
          </div>
        </div>

        {/* Client Info */}
        <div className="grid grid-cols-2 gap-12 mb-20">
          <div className="space-y-2">
            <span className="font-mono text-[8px] uppercase tracking-widest border-b border-black block pb-1 font-medium text-on-surface">Bill_To:</span>
            <div className="font-headline font-semibold text-base uppercase text-on-surface">{quotation.customer_name || ''}</div>
            <div className="font-mono text-[9px] opacity-60 uppercase font-light leading-relaxed text-on-surface">
              {quotation.customer_address && <>{quotation.customer_address.replace(/,/g, '\n')}<br /></>}
              {quotation.customer_gst && <>{`TAX_ID: ${quotation.customer_gst}`}<br /></>}
              {quotation.customer_phone && <>{`PHONE: ${quotation.customer_phone}`}<br /></>}
              {quotation.customer_email && `EMAIL: ${quotation.customer_email}`}
            </div>
          </div>
          <div className="space-y-2">
            <span className="font-mono text-[8px] uppercase tracking-widest border-b border-black block pb-1 font-medium text-on-surface">Issued_By:</span>
            <div className="font-headline font-semibold text-base uppercase text-on-surface">{user?.full_name || ''}</div>
            <div className="font-mono text-[9px] opacity-60 uppercase font-light leading-relaxed text-on-surface pt-1">
                {user?.phone && <>{`PH: ${user.phone}`}<br /></>}
                {user?.email && `EMAIL: ${user.email}`}
            </div>
          </div>
        </div>

        {/* Line Items Table */}
        <div className="flex-grow">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-black">
                <th className="py-3 font-mono text-[9px] uppercase tracking-widest font-medium text-on-surface">Description</th>
                <th className="py-3 font-mono text-[9px] uppercase tracking-widest text-right font-medium text-on-surface">Qty</th>
                <th className="py-3 font-mono text-[9px] uppercase tracking-widest text-right font-medium text-on-surface">Unit_Price</th>
                <th className="py-3 font-mono text-[9px] uppercase tracking-widest text-right font-medium text-on-surface">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {(quotation.items || []).map((item, idx) => (
                <tr key={idx}>
                  <td className="py-6 text-xs font-normal uppercase leading-relaxed max-w-[300px] text-on-surface">{item.description}</td>
                  <td className="py-6 font-mono text-xs text-right font-light align-top text-on-surface">{item.quantity} {item.unit}</td>
                  <td className="py-6 font-mono text-xs text-right font-light align-top text-on-surface">{formatAmount(item.unit_price)}</td>
                  <td className="py-6 font-mono text-xs text-right font-light align-top text-on-surface">{formatAmount(item.total)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Totals */}
        <div className="mt-12 border-t border-black pt-6">
          <div className="flex justify-end gap-16">
            <div className="space-y-1">
              <div className="font-mono text-[10px] text-right uppercase opacity-60 font-light text-on-surface">Subtotal</div>
              {taxTotal > 0 && (
                <div className="font-mono text-[10px] text-right uppercase opacity-60 font-light text-on-surface">Tax ({(((taxTotal / quotation.subtotal) * 100).toFixed(1))}%)</div>
              )}
              <div className="font-mono text-xl font-bold text-right uppercase pt-4 text-on-surface">Total (₹)</div>
            </div>
            <div className="space-y-1">
              <div className="font-mono text-[10px] text-right font-light text-on-surface">{formatAmount(quotation.subtotal)}</div>
              {taxTotal > 0 && (
                <div className="font-mono text-[10px] text-right font-light text-on-surface">{formatAmount(taxTotal)}</div>
              )}
              <div className="font-mono text-xl font-bold text-right pt-4 text-on-surface">{formatAmount(quotation.grand_total)}</div>
            </div>
          </div>
        </div>

        {/* Terms and Conditions Section */}
        {quotation.terms_conditions && (
          <div className="mt-12 pt-6 border-t border-neutral-100">
            <div className="font-mono text-[8px] uppercase tracking-widest opacity-60 mb-2">Terms_&_Conditions</div>
            <div className="text-[9px] font-normal uppercase leading-relaxed text-on-surface whitespace-pre-wrap opacity-80">
              {quotation.terms_conditions}
            </div>
          </div>
        )}

        {/* Notes Section */}
        {quotation.notes && (
          <div className="mt-6">
            <div className="font-mono text-[8px] uppercase tracking-widest opacity-60 mb-2">Notes</div>
            <div className="text-[9px] font-normal uppercase leading-relaxed text-on-surface whitespace-pre-wrap opacity-80">
              {quotation.notes}
            </div>
          </div>
        )}

        {/* Footer Fine Print */}
        <div className="mt-auto pt-8 border-t border-neutral-100">
          <div className="flex justify-between items-end">
            <p className="font-mono text-[7px] leading-tight text-neutral-400 uppercase font-light max-w-sm text-on-surface">
            </p>
            <div className="font-mono text-[7px] text-neutral-400 uppercase tracking-widest text-on-surface">
              Page 01 // 01
            </div>
          </div>
        </div>
      </div>
      </div>

      {showActions && (
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          <Link to={`/quotations/${quotation.id}/edit`}>
            <Button type="button" variant="outline" fullWidth>
              <Pencil className="mr-2 h-4 w-4" strokeWidth={2} /> Edit
            </Button>
          </Link>
          <Button type="button" variant="outline" fullWidth onClick={onDownload}>
            <Download className="mr-2 h-4 w-4" strokeWidth={2} /> PDF
          </Button>
          <Button
            type="button"
            fullWidth
            onClick={finalized ? onRevertFinalization : onFinalize}
            isLoading={finalized ? isReverting : isFinalizing}
          >
            <FileDown className="mr-2 h-4 w-4" strokeWidth={2} />
            {finalized ? 'REVERT' : 'FINALIZE'}
          </Button>
        </div>
      )}
    </div>
  );
}
