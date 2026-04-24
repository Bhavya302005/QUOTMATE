import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Download, Eye, FileText, Plus, Search, ChevronDown } from 'lucide-react';
import toast from 'react-hot-toast';
import { quotationAPI, getApiErrorMessage } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import {
  loadDraft,
  listDraftSlots,
  formatDraftTime,
  quotationDraftHasContent,
  clearDraft,
} from '../../utils/draftStorage';

function formatCurrency(value) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

function formatDate(value) {
  if (!value) return '-';
  return new Date(value).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function statusClass(status) {
  const s = (status || '').toLowerCase();
  if (s === 'finalized') return 'bg-black text-white border-black';
  return 'border-black bg-white text-on-surface';
}

export default function QuotationList() {
  const [quotations, setQuotations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [draftVersion, setDraftVersion] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 250);
    return () => clearTimeout(timer);
  }, [search]);

  const loadQuotations = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await quotationAPI.list({ page: 1, page_size: 100, search: debouncedSearch || undefined });
      setQuotations(response.data?.quotations || []);
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to load quotations'));
      setQuotations([]);
    } finally {
      setIsLoading(false);
    }
  }, [debouncedSearch]);

  useEffect(() => {
    loadQuotations();
  }, [loadQuotations]);

  const filteredQuotations = useMemo(() => {
    if (statusFilter === 'all') return quotations;
    if (statusFilter === 'draft') {
      return quotations.filter((q) => {
        const status = (q.status || '').toLowerCase();
        // OCR-detected quotations commonly start in review; include them in Draft view.
        return status === 'draft' || status === 'review';
      });
    }
    return quotations.filter((q) => q.status === statusFilter);
  }, [quotations, statusFilter]);

  const newDraft = loadDraft('quotation', 'new');
  const showNewDraft = newDraft?.updatedAt && quotationDraftHasContent(newDraft.values || {});
  const editDraftSlots = listDraftSlots('quotation').filter((s) => s.slot !== 'new');

  const handleDeleteLocalDraft = (slot) => {
    clearDraft('quotation', slot);
    setDraftVersion((v) => v + 1);
    toast.success('Draft removed');
  };

  const handleDownload = async (quotation) => {
    try {
      const response = await quotationAPI.download(quotation.id);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${quotation.quotation_number || quotation.id}.pdf`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Unable to download PDF'));
    }
  };



  return (
    <div className="relative min-h-[80vh] space-y-6 pb-20">
      <div className="flex items-center justify-between border-b border-black pb-4">
        <h1 className="text-2xl font-light uppercase tracking-tighter text-on-surface md:text-3xl">QUOTATIONS</h1>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-on-surface" strokeWidth={2} />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="SEARCH QUOTATIONS..."
            className="w-full border border-outline-variant bg-surface-white py-3 pl-10 pr-4 font-mono text-[10px] uppercase tracking-widest text-on-surface placeholder:text-outline-muted focus:border-black focus:outline-none focus:ring-0"
          />
        </div>
        <div className="relative">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="appearance-none rounded-none border border-outline-variant bg-surface-white py-3 pl-3 pr-10 font-mono text-[10px] uppercase tracking-widest text-on-surface focus:border-black focus:outline-none focus:ring-0"
          >
            <option value="all">All</option>
            <option value="draft">Draft</option>
            <option value="review">Review</option>
            <option value="finalized">Finalized</option>
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-on-surface" strokeWidth={2} />
        </div>
      </div>

      {(showNewDraft || editDraftSlots.length > 0) && (
        <div className="space-y-2 border border-dashed border-black bg-surface-container p-4">
          <p className="   text-outline-muted">Saved locally — continue editing</p>
          <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
            {showNewDraft && (
              <div className="inline-flex items-center border border-black bg-white">
                <Link
                  to="/quotations/new"
                  state={{ openManual: true, resumeDraft: true }}
                  className="px-4 py-2    text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
                >
                  New quotation draft · {formatDraftTime(newDraft.updatedAt)}
                </Link>
                <button
                  type="button"
                  onClick={() => handleDeleteLocalDraft('new')}
                  className="border-l border-black px-3 py-2    text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
                  aria-label="Delete new quotation draft"
                  title="Delete draft"
                >
                  ×
                </button>
              </div>
            )}
            {editDraftSlots.map(({ slot, updatedAt }) => (
              <div key={`${slot}-${draftVersion}`} className="inline-flex items-center border border-black bg-white">
                <Link
                  to={`/quotations/${slot}/edit`}
                  className="px-4 py-2    text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
                >
                  Edit draft · {slot.slice(0, 8)}… · {formatDraftTime(updatedAt)}
                </Link>
                <button
                  type="button"
                  onClick={() => handleDeleteLocalDraft(slot)}
                  className="border-l border-black px-3 py-2    text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
                  aria-label={`Delete draft ${slot}`}
                  title="Delete draft"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="mt-6 flex min-h-48 items-center justify-center">
          <LoadingSpinner />
        </div>
      ) : filteredQuotations.length === 0 ? (
        <div className="mt-6 flex flex-col items-center justify-center border border-black bg-surface-white p-10 text-center">
          <div className="mb-4 border border-black bg-black p-4 text-white">
            <FileText className="h-8 w-8" strokeWidth={1.75} />
          </div>
          <p className="mb-2 font-mono text-[10px] uppercase tracking-widest text-on-surface">No quotations</p>
          <p className="font-mono text-[10px] uppercase tracking-widest text-outline-muted">Create your first quote.</p>
        </div>
      ) : (
        <div className="mt-6 space-y-3">
          {filteredQuotations.map((quotation) => (
            <div key={quotation.id} className="border border-black bg-surface-white p-4 sm:p-5">
              <div className="mb-4 flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h3 className="truncate text-base font-normal  tracking-tight text-on-surface">
                    {quotation.customer_name}
                  </h3>
                  <div className="mt-1 flex flex-wrap items-center gap-2">
                    <span className="border border-black bg-white px-2 py-0.5  text-[9px]  ">
                      {quotation.quotation_number || quotation.id.slice(0, 8)}
                    </span>
                    <span className="border border-black px-2 py-0.5  text-[9px]  ">
                      {formatDate(quotation.created_at)}
                    </span>
                  </div>
                </div>
                <span
                  className={`shrink-0 border px-2 py-1  text-[9px]   ${statusClass(quotation.status)}`}
                >
                  {quotation.status || 'draft'}
                </span>
              </div>
              <div className="flex items-end justify-between border-t border-black pt-4">
                <span className="text-xl font-light tracking-tighter text-on-surface md:text-2xl">
                  {formatCurrency(quotation.grand_total)}
                </span>
                <div className="flex items-center gap-2">
                  <Link
                    to={`/quotations/${quotation.id}`}
                    className="flex h-10 w-10 items-center justify-center border border-black bg-white text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
                  >
                    <Eye className="h-4 w-4" strokeWidth={2} />
                  </Link>
                  <button
                    type="button"
                    onClick={() => handleDownload(quotation)}
                    className="flex h-10 w-10 items-center justify-center border border-black bg-white text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
                  >
                    <Download className="h-4 w-4" strokeWidth={2} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Link to="/quotations/new" state={{ skipDraft: true }} className="fixed bottom-20 right-4 z-40 sm:right-6 md:bottom-8 md:right-8 lg:right-12">
        <div className="flex h-14 w-14 items-center justify-center border-2 border-black bg-black text-white transition-colors duration-100 hover:bg-white hover:text-black md:h-16 md:w-16">
          <Plus className="h-7 w-7" strokeWidth={2} />
        </div>
      </Link>
    </div>
  );
}
