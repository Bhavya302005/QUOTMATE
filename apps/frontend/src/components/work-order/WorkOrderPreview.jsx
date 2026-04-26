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

export default function WorkOrderPreview({
  workOrder,
  onDownload,
  onFinalize,
  onRevertFinalization,
  isFinalizing = false,
  isReverting = false,
  showActions = true,
}) {
  const { user } = useAuth();
  if (!workOrder) return null;

  const finalized = (workOrder.status || '').toLowerCase() === 'finalized' || (workOrder.status || '').toLowerCase() === 'completed';
  const issueDate = formatDateDot(workOrder.created_at);
  const companyDisplayName = String(user?.company_name || user?.full_name || '').toUpperCase();
  const companyAddress = String(user?.address || '').toUpperCase();

  // Logo Resolution
  const logoUrl = user?.company_logo_url
    ? (user.company_logo_url.startsWith('http') ? user.company_logo_url : `${VITE_API_URL}${user.company_logo_url}`)
    : null;
  return (
    <div className="space-y-4">
      <div className="document-a4 bg-white p-12 flex flex-col font-['Inter'] relative selection:bg-black selection:text-white border border-neutral-200 shadow-sm mx-auto w-full max-w-[210mm] min-h-[297mm]">
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
            <h2 className="font-headline font-bold text-5xl uppercase tracking-tighter mb-4 leading-none text-on-surface">Work Order</h2>
            <div className="font-mono text-[10px] leading-relaxed uppercase font-light text-on-surface">
              <div className="font-bold mb-1"><span className="opacity-40 font-normal">BY,</span> {companyDisplayName}</div>
              <span className="opacity-40">{issueDate && 'DATE:'}</span> {issueDate}
            </div>
          </div>
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-2 gap-12 mb-20">
          <div className="space-y-2">
            <span className="font-mono text-[8px] uppercase tracking-widest border-b border-black block pb-1 font-medium text-on-surface">Client_Info:</span>
            <div className="font-headline font-semibold text-base uppercase text-on-surface">{workOrder.client_name || ''}</div>
            <div className="font-mono text-[9px] opacity-60 uppercase font-light leading-relaxed text-on-surface">
              {workOrder.client_phone && <p>PHONE: {workOrder.client_phone}</p>}
              {workOrder.client_email && <p>EMAIL: {workOrder.client_email}</p>}
              {workOrder.service_location && <p>LOC: {workOrder.service_location}</p>}
            </div>
          </div>
          <div className="space-y-2">
            <span className="font-mono text-[8px] uppercase tracking-widest border-b border-black block pb-1 font-medium text-on-surface">Assigned_To:</span>
            <div className="font-headline font-semibold text-base uppercase text-on-surface">{workOrder.assigned_to || user?.full_name || ''}</div>
            <div className="font-mono text-[9px] opacity-60 uppercase font-light leading-relaxed text-on-surface pt-1">
                {user?.phone && `PH: ${user.phone}`}
            </div>
            <div className="font-mono text-[9px] opacity-60 uppercase font-light leading-relaxed text-on-surface">
              {workOrder.start_date && <p>START: {workOrder.start_date}</p>}
              {workOrder.end_date && <p>END: {workOrder.end_date}</p>}
            </div>
          </div>
        </div>

        {/* Content Section */}
        <div className="mb-8">
            <div className="font-mono text-[8px] uppercase tracking-widest opacity-60 mb-2">WORK_DESCRIPTION</div>
            <div className="text-xs font-normal uppercase leading-relaxed text-on-surface whitespace-pre-wrap">
                {workOrder.work_description || ''}
            </div>
        </div>

        {/* Line Items Table */}
        {(workOrder.materials || []).length > 0 && (
          <div className="flex-grow">
            <div className="font-mono text-[8px] uppercase tracking-widest opacity-60 mb-2">MATERIALS_&_RESOURCES</div>
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-black">
                  <th className="py-3 font-mono text-[9px] uppercase tracking-widest font-medium text-on-surface">Description</th>
                  <th className="py-3 font-mono text-[9px] uppercase tracking-widest text-right font-medium text-on-surface">Qty</th>
                  <th className="py-3 font-mono text-[9px] uppercase tracking-widest text-right font-medium text-on-surface">Unit_Price</th>
                  <th className="py-3 font-mono text-[9px] uppercase tracking-widest text-right font-medium text-on-surface">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100 font-mono text-xs font-light text-on-surface">
                {workOrder.materials.map((m, idx) => (
                  <tr key={idx}>
                    <td className="py-6 uppercase leading-relaxed text-on-surface">{m.material_name}</td>
                    <td className="py-6 text-right font-mono text-on-surface">{m.quantity} {m.unit}</td>
                    <td className="py-6 text-right font-mono text-on-surface">{formatAmount(m.unit_cost)}</td>
                    <td className="py-6 text-right font-mono text-on-surface">{formatAmount(m.total_cost)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Totals */}
        <div className="mt-12 border-t border-black pt-6">
          <div className="flex justify-end gap-16">
            <div className="space-y-1">
              <div className="font-mono text-[10px] text-right uppercase opacity-60 font-light text-on-surface">Labor Cost ({workOrder.labor_hours || 0} hrs @ {formatAmount(workOrder.labor_rate)})</div>
              <div className="font-mono text-[10px] text-right uppercase opacity-60 font-light text-on-surface">Material Sum</div>
              <div className="font-mono text-xl font-bold text-right uppercase pt-4 text-on-surface">Total (₹)</div>
            </div>
            <div className="space-y-1">
              <div className="font-mono text-[10px] text-right font-light text-on-surface">{formatAmount(workOrder.labor_cost)}</div>
              <div className="font-mono text-[10px] text-right font-light text-on-surface">{formatAmount(workOrder.material_cost)}</div>
              <div className="font-mono text-xl font-bold text-right pt-4 text-on-surface">{formatAmount(workOrder.total_cost)}</div>
            </div>
          </div>
        </div>

        {/* Remarks Section */}
        {workOrder.remarks && (
          <div className="mt-12 mb-8">
            <div className="font-mono text-[8px] uppercase tracking-widest opacity-60 mb-2">REMARKS</div>
            <div className="font-mono text-[9px] uppercase opacity-60 font-light leading-relaxed text-on-surface">
                {workOrder.remarks}
            </div>
          </div>
        )}

        {/* Footer Fine Print */}
        <div className="mt-auto pt-8 border-t border-neutral-100">
          <div className="flex justify-between items-end">
            <p className="font-mono text-[7px] leading-tight text-neutral-400 uppercase font-light max-w-sm text-on-surface">
              This document is a digital representation and remains valid for 30 days.
              Final binding execution requires cryptographic signature from both parties.
            </p>
            <div className="font-mono text-[7px] text-neutral-400 uppercase tracking-widest text-on-surface">
              Page 01 // 01
            </div>
          </div>
        </div>
      </div>

      {showActions && (
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          <Link to={`/work-orders/${workOrder.id}/edit`}>
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
