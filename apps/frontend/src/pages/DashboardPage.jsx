import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Trash2, TrendingUp, FileText, ClipboardList, Users } from 'lucide-react';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import { dashboardAPI, documentsAPI } from '../services/api.js';

function fmt(n) {
  if (n === undefined || n === null) return '0';
  return Number(n).toLocaleString('en-IN');
}
function fmtCurrency(n) {
  return '₹ ' + fmt(n);
}
function relativeDate(iso) {
  if (!iso) return '—';
  const diff = Date.now() - new Date(iso).getTime();
  const d = Math.floor(diff / 86400000);
  if (d === 0) return 'Today';
  if (d === 1) return 'Yesterday';
  if (d < 7) return `${d}d ago`;
  if (d < 30) return `${Math.floor(d / 7)}w ago`;
  return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

const TYPE_LABEL = { quotation: 'Quotation', mom: 'MOM', work_order: 'Work order' };
const routesByType = { quotation: '/quotations', mom: '/moms', work_order: '/work-orders' };

function statusBadge(status) {
  const s = (status || '').toLowerCase();
  if (s === 'finalized') return 'border-black bg-black text-white';
  return 'border-black bg-white text-on-surface group-hover:border-white';
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [deleting, setDeleting] = useState(null);
  const [docToDelete, setDocToDelete] = useState(null);

  const { data: queryData, isLoading: loading, refetch: loadDashboard } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const res = await dashboardAPI.getStats();
      return res.data;
    },
  });

  const data = queryData || null;

  const confirmDelete = (e, doc) => {
    e.stopPropagation();
    setDocToDelete(doc);
  };

  const handleDeleteDoc = async (deductRevenue) => {
    if (!docToDelete) return;
    setDeleting(docToDelete.id);
    try {
      await documentsAPI.delete(docToDelete.id, deductRevenue);
      toast.success('Document deleted');
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      queryClient.invalidateQueries({ queryKey: ['moms'] });
      queryClient.invalidateQueries({ queryKey: ['work_orders'] });
    } catch {
      toast.error('Failed to delete document');
    } finally {
      setDeleting(null);
      setDocToDelete(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const stats = data?.stats ?? {};
  const qStatus = data?.quotation_status ?? {};
  const recent = data?.recent_documents ?? [];

  const greet = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="space-y-12 pb-8">
      <div className="grid grid-cols-1 gap-8 border-b border-black pb-10 md:grid-cols-12 md:items-end">
        <div className="md:col-span-8">
          <p className="mb-2 font-mono text-[10px] uppercase tracking-widest text-outline-muted">{greet()}</p>
          <h1 className="font-headline text-4xl font-light leading-[0.95] tracking-tighter uppercase text-on-surface md:text-6xl">
            Dashboard
          </h1>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <span className="border border-black bg-black px-3 py-1 font-mono text-[10px] uppercase tracking-widest text-white">
              Active session
            </span>
            <span className="font-mono text-[10px] uppercase tracking-widest text-outline-muted">
              {new Date().toLocaleDateString('en-IN', {
                weekday: 'long',
                day: 'numeric',
                month: 'long',
                year: 'numeric',
              })}
            </span>
          </div>
        </div>
        <div className="border-t border-black pt-6 md:col-span-4 md:border-l md:border-t-0 md:pl-8 md:pt-0">
          <p className="mb-2 font-mono text-[10px] uppercase tracking-widest text-outline-muted">Architectural summary</p>
          <p className="font-mono text-[10px] uppercase tracking-widest text-on-surface">
            {stats.total_documents ?? 0} documents on file.
            {qStatus.finalized ? ` ${qStatus.finalized} quotations finalized.` : ''}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-px border border-black bg-black md:grid-cols-4">
        <div className="group bg-surface-white p-6 transition-colors duration-200 hover:bg-black hover:text-white md:p-8">
          <p className="mb-8 flex justify-between font-mono text-[10px] uppercase tracking-widest">
            Total revenue
            <TrendingUp className="h-4 w-4" strokeWidth={1.5} />
          </p>
          <p className="text-3xl font-light leading-none tracking-tighter md:text-3xl lg:text-4xl">
            {fmtCurrency(stats.total_revenue)}
          </p>
          <p className="mt-2 font-mono text-[10px] uppercase tracking-widest opacity-70 group-hover:opacity-80">
            This month {fmtCurrency(stats.monthly_revenue)}
          </p>
        </div>
        <div className="group bg-surface-white p-6 transition-colors duration-200 hover:bg-black hover:text-white md:p-8">
          <p className="mb-8 flex justify-between font-mono text-[10px] uppercase tracking-widest">
            Quotations
            <FileText className="h-4 w-4" strokeWidth={1.5} />
          </p>
          <p className="text-3xl font-light leading-none tracking-tighter md:text-3xl lg:text-4xl">{fmt(stats.total_quotations)}</p>
          <p className="mt-2 font-mono text-[10px] uppercase tracking-widest opacity-70 group-hover:opacity-80">
            {qStatus.finalized ?? 0} finalized
          </p>
        </div>
        <div className="group bg-surface-white p-6 transition-colors duration-200 hover:bg-black hover:text-white md:p-8">
          <p className="mb-8 flex justify-between font-mono text-[10px] uppercase tracking-widest">
            MOMs
            <Users className="h-4 w-4" strokeWidth={1.5} />
          </p>
          <p className="text-3xl font-light leading-none tracking-tighter md:text-3xl lg:text-4xl">{fmt(stats.total_moms)}</p>
          <p className="mt-2 font-mono text-[10px] uppercase tracking-widest opacity-70 group-hover:opacity-80">Meeting minutes</p>
        </div>
        <div className="group bg-surface-white p-6 transition-colors duration-200 hover:bg-black hover:text-white md:p-8">
          <p className="mb-8 flex justify-between font-mono text-[10px] uppercase tracking-widest">
            Work orders
            <ClipboardList className="h-4 w-4" strokeWidth={1.5} />
          </p>
          <p className="text-3xl font-light leading-none tracking-tighter md:text-3xl lg:text-4xl">{fmt(stats.total_work_orders)}</p>
          <p className="mt-2 font-mono text-[10px] uppercase tracking-widest opacity-70 group-hover:opacity-80">Active work orders</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <button
          type="button"
          onClick={() => navigate('/quotations/new', { state: { skipDraft: true } })}
          className="border border-black bg-white py-4 text-center transition-colors duration-100 hover:bg-black hover:text-white"
        >
          <span className="block font-mono text-[10px] uppercase tracking-widest">New quote</span>
        </button>
        <button
          type="button"
          onClick={() => navigate('/moms/new', { state: { skipDraft: true } })}
          className="border border-black bg-white py-4 text-center transition-colors duration-100 hover:bg-black hover:text-white"
        >
          <span className="block font-mono text-[10px] uppercase tracking-widest">New MOM</span>
        </button>
        <button
          type="button"
          onClick={() => navigate('/work-orders')}
          className="border border-black bg-white py-4 text-center transition-colors duration-100 hover:bg-black hover:text-white"
        >
          <span className="block font-mono text-[10px] uppercase tracking-widest">NEW WO</span>
        </button>
      </div>

      <section>
        <div className="mb-6 flex flex-col gap-4 border-b border-black pb-4 sm:flex-row sm:items-end sm:justify-between">
          <h2 className="font-headline text-xl font-light tracking-tighter uppercase text-on-surface">Recent activity</h2>
          <span className="font-mono text-[10px] uppercase tracking-widest text-outline-muted">
            {stats.total_documents ?? 0} total documents
          </span>
        </div>

        {recent.length === 0 ? (
          <div className="border border-dashed border-outline-variant bg-surface-white p-10 text-center">
            <p className="font-mono text-[10px] uppercase tracking-widest text-outline-muted">No documents yet</p>
          </div>
        ) : (
          <div className="overflow-x-auto border-t border-black">
            <table className="w-full min-w-[600px] text-left font-sans text-sm font-light">
              <thead>
                <tr className="border-b border-black bg-surface-container font-mono text-[10px] uppercase tracking-widest">
                  <th className="px-4 py-3 font-normal">Document</th>
                  <th className="px-4 py-3 font-normal">Type</th>
                  <th className="px-4 py-3 font-normal">Status</th>
                  <th className="px-4 py-3 font-normal">Updated</th>
                  <th className="px-4 py-3 text-right font-normal"> </th>
                </tr>
              </thead>
              <tbody>
                {recent.map((doc) => (
                  <tr
                    key={doc.id}
                    className="group cursor-pointer border-b border-outline-variant transition-colors duration-100 hover:bg-black hover:text-white"
                    role="button"
                    tabIndex={0}
                    onClick={() => {
                      const base = routesByType[doc.document_type];
                      navigate(base ? `${base}/${doc.id}` : '/dashboard');
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        const base = routesByType[doc.document_type];
                        navigate(base ? `${base}/${doc.id}` : '/dashboard');
                      }
                    }}
                  >
                    <td className="px-4 py-4 font-mono text-[11px] uppercase tracking-widest">
                      {doc.document_number || doc.id?.slice(0, 8) || '—'}
                    </td>
                    <td className="px-4 py-4 text-xs uppercase">
                      {TYPE_LABEL[doc.document_type] || doc.document_type}
                    </td>
                    <td className="px-4 py-4">
                      <span
                        className={`inline-block border px-2 py-0.5 font-mono text-[9px] uppercase tracking-tighter ${statusBadge(doc.status)}`}
                      >
                        {doc.status}
                      </span>
                    </td>
                    <td className="px-4 py-4 font-mono text-[10px] uppercase tracking-widest opacity-80">
                      {relativeDate(doc.created_at)}
                    </td>
                    <td className="px-4 py-4 text-right">
                      <button
                        type="button"
                        onClick={(e) => confirmDelete(e, doc)}
                        disabled={deleting === doc.id}
                        className="inline-flex h-9 w-9 items-center justify-center border border-black bg-white text-on-surface transition-colors duration-100 hover:bg-error hover:text-white disabled:opacity-40 group-hover:border-white group-hover:bg-black group-hover:text-white"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" strokeWidth={2} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <footer className="flex flex-col gap-6 border-t border-outline-variant pt-8 text-outline-muted sm:flex-row sm:justify-between">
        <div>
          <p className="mb-1 font-mono text-[10px] uppercase tracking-widest opacity-60">Build</p>
          <p className="font-mono text-[10px] uppercase tracking-widest text-on-surface">QuotMate</p>
        </div>
        <div className="text-left sm:text-right">
          <p className="mb-1 font-mono text-[10px] uppercase tracking-widest opacity-60">Local time</p>
          <p className="font-mono text-[10px] uppercase tracking-widest text-on-surface">
            {new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
      </footer>

      {docToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-md border border-black bg-surface-white p-6">
            <h2 className="mb-4 text-xl font-light tracking-tight text-on-surface">Delete Document</h2>
            <p className="mb-6 text-sm text-outline-muted">
              Are you sure you want to delete "{docToDelete.title || docToDelete.document_number}"? This cannot be undone.
            </p>
            {docToDelete.document_type === 'quotation' && docToDelete.status === 'finalized' && (
              <p className="mb-6 text-sm text-on-surface border-l-2 border-black pl-3 bg-surface-container py-2">
                This is a finalized quotation. Do you want to deduct its amount from your monthly revenue?
              </p>
            )}
            <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
              <button
                type="button"
                onClick={() => setDocToDelete(null)}
                className="border border-black bg-white px-4 py-2 text-sm transition-colors hover:bg-surface-container"
              >
                Cancel
              </button>
              {docToDelete.document_type === 'quotation' && docToDelete.status === 'finalized' ? (
                <>
                  <button
                    type="button"
                    onClick={() => handleDeleteDoc(false)}
                    disabled={deleting === docToDelete.id}
                    className="border border-black bg-black px-4 py-2 text-sm text-white transition-colors hover:opacity-80 disabled:opacity-50"
                  >
                    Delete & Keep Revenue
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDeleteDoc(true)}
                    disabled={deleting === docToDelete.id}
                    className="border border-error bg-error px-4 py-2 text-sm text-white transition-colors hover:opacity-80 disabled:opacity-50"
                  >
                    Delete & Deduct
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  onClick={() => handleDeleteDoc(true)}
                  disabled={deleting === docToDelete.id}
                  className="border border-error bg-error px-4 py-2 text-sm text-white transition-colors hover:opacity-80 disabled:opacity-50"
                >
                  Delete Document
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
