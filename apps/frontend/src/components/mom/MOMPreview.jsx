import React from 'react';
import { Link } from 'react-router-dom';
import { Download, FileDown, Pencil } from 'lucide-react';
import Button from '../common/Button';
import { useAuth } from '../../hooks/useAuth';
import { getCompanyLogoSrc } from '../../services/api';


function formatDateDot(input) {
  const d = input ? new Date(input) : new Date();
  if (Number.isNaN(d.getTime())) return '';
  const year = d.getFullYear();
  const month = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${year}.${month}.${day}`;
}

function formatTime(value) {
  if (!value) return '';
  const parsed = new Date(`1970-01-01T${value}`);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

export default function MOMPreview({
  mom,
  onDownload,
  onFinalize,
  onRevertFinalization,
  isFinalizing = false,
  isReverting = false,
  showActions = true,
}) {
  const { user } = useAuth();
  if (!mom) return null;

  const finalized = (mom.status || '').toLowerCase() === 'finalized';
  const companyDisplayName = String(user?.company_name || user?.full_name || '').toUpperCase();
  const companyAddress = String(user?.address || '').toUpperCase();
  const issueDate = formatDateDot(mom.created_at || mom.meeting_date);

  // Logo Resolution
  const logoUrl = getCompanyLogoSrc(user);
  return (
    <div className="space-y-4">
      <div className="w-full overflow-x-auto overflow-y-hidden max-w-full pb-4">
        <div className="document-a4 bg-white p-12 md:p-16 flex flex-col font-['Inter'] relative selection:bg-black selection:text-white border border-black shadow-none mx-auto min-w-[794px] max-w-[794px] min-h-[1123px] overflow-hidden">
          {/* Decorative Blueprint Elements */}
        <div className="absolute top-0 right-0 w-32 h-32 border-r border-t border-black/5 -translate-y-16 translate-x-16 rotate-45 pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-32 h-32 border-l border-b border-black/5 translate-y-16 -translate-x-16 rotate-45 pointer-events-none"></div>

        {/* Branding Header */}
        <div className="flex justify-between items-start mb-12 border-b-2 border-black pb-8">
          <div className="space-y-4">
            <span className="font-mono text-[10px] uppercase tracking-widest text-neutral-400 block font-light">
              Meeting Documentation / Internal
            </span>
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
            <h1 className="text-4xl font-extrabold uppercase tracking-tighter leading-none text-on-surface w-full max-w-lg mt-4">
              {mom.meeting_title || 'MINUTES OF MEETING'}
            </h1>
          </div>
          <div className="text-right flex flex-col items-end">
            <div className="font-mono text-[10px] leading-relaxed uppercase font-light text-on-surface mb-4">
               <div className="font-bold mb-1"><span className="opacity-40 font-normal">BY,</span> {companyDisplayName}</div>
               <span className="opacity-40">{issueDate && 'DATE:'}</span> {issueDate}
            </div>
            <div className="font-mono text-xs font-bold bg-black text-white px-3 py-1 mb-2">REF: {mom.reference_number || `MOM-${new Date().getFullYear()}-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`}</div>
            <div className="font-mono text-[10px] text-neutral-400 uppercase">STATUS: {finalized ? 'FINALIZED' : 'DRAFT'}</div>
          </div>
        </div>

        {/* Meta Grid */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-12 mb-16">
          <div className="space-y-6">
            <div className="border-l border-black pl-4">
              <label className="font-mono text-[10px] uppercase text-neutral-400 block mb-1 font-light">Date</label>
              <span className="font-semibold text-sm uppercase">{mom.meeting_date ? formatDateDot(mom.meeting_date) : '—'}</span>
            </div>
            <div className="border-l border-black pl-4">
              <label className="font-mono text-[10px] uppercase text-neutral-400 block mb-1 font-light">Time</label>
              <span className="font-semibold text-sm uppercase">{mom.meeting_time ? formatTime(mom.meeting_time) : '—'}</span>
            </div>
            <div className="border-l border-black pl-4">
              <label className="font-mono text-[10px] uppercase text-neutral-400 block mb-1 font-light">Chairperson</label>
              <span className="font-semibold text-sm uppercase block truncate">{user?.full_name || '—'}</span>
              {(user?.phone || user?.email) && (
                <span className="font-mono text-[8px] opacity-60 uppercase block mt-1">
                  {user.phone && `PH: ${user.phone}`}
                  {user.phone && user.email && ' | '}
                  {user.email && `EMAIL: ${user.email}`}
                </span>
              )}
            </div>
            <div className="border-l border-black pl-4">
              <label className="font-mono text-[10px] uppercase text-neutral-400 block mb-1 font-light">Location</label>
              <span className="font-semibold text-sm uppercase">{mom.location || '—'}</span>
            </div>
          </div>
          <div className="md:col-span-2">
            <label className="font-mono text-[10px] uppercase text-neutral-400 block mb-4 border-b border-neutral-200 pb-1 font-light">Attendees</label>
            <div className="grid grid-cols-2 gap-y-2 text-[11px] font-mono uppercase">
              {mom.attendees && mom.attendees.length > 0 ? (
                mom.attendees.map((att, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-black"></span> {att}
                  </div>
                ))
              ) : (
                <div className="text-neutral-300 italic">No attendees listed</div>
              )}
            </div>
          </div>
        </section>

        {/* Discussion Points */}
        <section className="mb-12">
          <h2 className="font-mono text-[10px] font-bold uppercase tracking-[0.2em] mb-8 flex items-center gap-4">
            01 Discussion Points
            <span className="flex-grow h-px bg-neutral-200"></span>
          </h2>
          <div className="space-y-8">
            {mom.ai_summary && (
              <article className="flex gap-8">
                <div className="font-mono text-[10px] text-neutral-400 pt-1 shrink-0 font-light">1.1</div>
                <div className="space-y-2">
                  <h3 className="font-bold text-sm uppercase">Executive Summary</h3>
                  <p className="text-[11px] text-on-surface leading-relaxed font-light uppercase whitespace-pre-wrap">
                    {mom.ai_summary}
                  </p>
                </div>
              </article>
            )}
            
            {(mom.key_points || []).length > 0 && (
              <article className="flex gap-8">
                <div className="font-mono text-[10px] text-neutral-400 pt-1 shrink-0 font-light">1.2</div>
                <div className="space-y-4 w-full">
                  <h3 className="font-bold text-sm uppercase">Key Points & Observations</h3>
                  <ul className="font-mono text-[10px] uppercase font-light space-y-2">
                    {mom.key_points.map((p, i) => (
                      <li key={i} className="flex gap-4 border-b border-neutral-50 pb-2">
                         <span className="opacity-40 shrink-0 select-none">[{String(i+1).padStart(2, '0')}]</span>
                         <span className="leading-relaxed">{p}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </article>
            )}

            {(mom.decisions || []).length > 0 && (
              <article className="flex gap-8">
                <div className="font-mono text-[10px] text-neutral-400 pt-1 shrink-0 font-light">1.3</div>
                <div className="space-y-4 w-full">
                  <h3 className="font-bold text-sm uppercase">Decisions & Outcomes</h3>
                  <div className="grid grid-cols-1 gap-4">
                    {mom.decisions.map((p, i) => (
                      <div key={i} className="p-4 bg-neutral-50 border-l border-black">
                         <div className="text-[10px] uppercase font-light leading-relaxed">{p}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </article>
            )}
          </div>
        </section>

        {/* Action Items Table */}
        {(mom.action_items || []).length > 0 && (
          <section className="mb-12">
            <h2 className="font-mono text-[10px] font-bold uppercase tracking-[0.2em] mb-8 flex items-center gap-4">
              02 Action Items
              <span className="flex-grow h-px bg-neutral-200"></span>
            </h2>
            <div className="border border-black overflow-hidden">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-black text-white font-mono text-[10px] uppercase">
                    <th className="p-4 border-r border-white/20 font-bold">Ref No</th>
                    <th className="p-4 border-r border-white/20 font-bold">Action Item Description</th>
                    <th className="p-4 border-r border-white/20 font-bold">Owner</th>
                    <th className="p-4 font-bold">Due Date</th>
                  </tr>
                </thead>
                <tbody className="text-[10px] font-mono uppercase">
                  {mom.action_items.map((item, idx) => (
                    <tr key={idx} className="border-b border-neutral-200 hover:bg-neutral-50 transition-colors">
                      <td className="p-4 border-r border-neutral-200 font-light">#{String(idx + 1).padStart(3, '0')}</td>
                      <td className="p-4 border-r border-neutral-200">
                        <div className="font-bold">{item.title}</div>
                        {item.description && <div className="text-[8px] opacity-40 mt-1 font-light normal-case">Note: {item.description}</div>}
                      </td>
                      <td className="p-4 border-r border-neutral-200 font-medium">{item.assigned_to || '—'}</td>
                      <td className="p-4 font-bold">{item.due_date ? formatDateDot(item.due_date) : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* Approval Section */}
        <section className="mt-auto pt-12 border-t border-neutral-200 flex justify-between items-start">
          <div className="space-y-8">
            <div>
              <div className="h-10 border-b border-black w-64 mb-2 flex items-end px-2 pb-1">
                <span className="font-mono text-[10px] uppercase font-bold">{user?.full_name}</span>
                <span className="font-mono text-[8px] opacity-40 ml-2">
                  {user?.phone && `PH: ${user.phone}`}
                  {user?.phone && user?.email && ' | '}
                  {user?.email && `EMAIL: ${user.email}`}
                </span>
              </div>
              <label className="font-mono text-[10px] uppercase text-neutral-400 font-light">Meeting Chairperson / Issued By</label>
            </div>
            <div className="text-[8px] font-mono text-neutral-300 uppercase leading-tight max-w-xs">
              This document serves as an official record of decisions made during the specified session. 
              Digital copy is stored and secured in project archives.
            </div>
          </div>
        </section>

        {/* Page Metadata Footer */}
        <div className="mt-8 flex items-center justify-between text-neutral-300 font-mono text-[8px] uppercase tracking-widest">
          <div className="flex gap-8">
            <div>Generated: {new Date().toISOString().replace('T', ' ').substring(0, 19)}</div>
            <div>Confidentiality: Internal / Tier 1</div>
          </div>
          <div>Page 01 of 01</div>
        </div>
      </div>
      </div>

      {showActions && (
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          <Link to={`/moms/${mom.id}/edit`}>
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
