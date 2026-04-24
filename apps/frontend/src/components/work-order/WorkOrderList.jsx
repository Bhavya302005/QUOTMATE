import { useState, useEffect, useCallback } from 'react';
import { Plus, Search, ClipboardList, ChevronDown } from 'lucide-react';
import { workOrderAPI } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner.jsx';
import toast from 'react-hot-toast';
import {
  loadDraft,
  listDraftSlots,
  formatDraftTime,
  workOrderDraftHasContent,
  clearDraft,
} from '../../utils/draftStorage';

const STATUS_STYLES = {
  pending: 'border-black bg-white text-on-surface',
  in_progress: 'border-black bg-black text-white',
  completed: 'border-black bg-surface-container text-on-surface',
  cancelled: 'border-black bg-white text-outline-muted line-through decoration-black',
};

const STATUS_LABELS = {
  pending: 'Pending',
  in_progress: 'Active',
  completed: 'Done',
  cancelled: 'Cancelled',
};

export default function WorkOrderList({ onSelect, onNew, refreshTrigger, onResumeDraft, onResumeEditDraft }) {
  const [workOrders, setWorkOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [draftVersion, setDraftVersion] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 250);
    return () => clearTimeout(timer);
  }, [search]);

  const fetchWorkOrders = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await workOrderAPI.list({
        page,
        page_size: 10,
        search: debouncedSearch || undefined,
        status: statusFilter || undefined,
      });
      setWorkOrders(resp.data?.items ?? []);
      setTotalPages(resp.data?.total_pages ?? 1);
    } catch {
      toast.error('Failed to load work orders');
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearch, statusFilter, refreshTrigger]);

  useEffect(() => {
    fetchWorkOrders();
  }, [fetchWorkOrders]);

  const newDraft = loadDraft('workorder', 'new');
  const showNewDraft = newDraft?.updatedAt && workOrderDraftHasContent(newDraft);
  const editDraftSlots = listDraftSlots('workorder').filter((s) => s.slot !== 'new');

  const handleDeleteLocalDraft = (slot) => {
    clearDraft('workorder', slot);
    setDraftVersion((v) => v + 1);
    toast.success('Draft removed');
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Delete this work order?')) return;
    try {
      await workOrderAPI.delete(id);
      toast.success('Work order deleted');
      fetchWorkOrders();
    } catch {
      toast.error('Failed to delete work order');
    }
  };



  return (
    <div className="relative min-h-[80vh] space-y-6 pb-20">
      <div className="flex items-center justify-between border-b border-black pb-4">
        <h2 className="text-2xl font-light uppercase tracking-tighter text-on-surface md:text-3xl">WORK ORDERS</h2>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-on-surface" strokeWidth={2} />
          <input
            type="text"
            placeholder="SEARCH CLIENT OR WO..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full border border-outline-variant bg-surface-white py-3 pl-10 pr-4 font-mono text-[10px] uppercase tracking-widest text-on-surface placeholder:text-outline-muted focus:border-black focus:outline-none focus:ring-0"
          />
        </div>
        <div className="relative">
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="appearance-none rounded-none border border-outline-variant bg-surface-white py-3 pl-3 pr-10 font-mono text-[10px] uppercase tracking-widest text-on-surface focus:border-black focus:outline-none focus:ring-0"
          >
            <option value="">All</option>
            <option value="pending">Pending</option>
            <option value="in_progress">Active</option>
            <option value="completed">Done</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-on-surface" strokeWidth={2} />
        </div>
      </div>

      {(showNewDraft || editDraftSlots.length > 0) && (
        <div className="space-y-2 border border-dashed border-black bg-surface-container p-4">
          <p className="   text-outline-muted">Saved locally — continue editing</p>
          <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
            {showNewDraft && onResumeDraft && (
              <div className="inline-flex items-center border border-black bg-white">
                <button
                  type="button"
                  onClick={onResumeDraft}
                  className="px-4 py-2    text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
                >
                  New work order draft · {formatDraftTime(newDraft.updatedAt)}
                </button>
                <button
                  type="button"
                  onClick={() => handleDeleteLocalDraft('new')}
                  className="border-l border-black px-3 py-2    text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
                  aria-label="Delete new work order draft"
                  title="Delete draft"
                >
                  ×
                </button>
              </div>
            )}
            {editDraftSlots.map(({ slot, updatedAt }) => (
              <div key={`${slot}-${draftVersion}`} className="inline-flex items-center border border-black bg-white">
                <button
                  type="button"
                  onClick={() => onResumeEditDraft?.(slot)}
                  className="px-4 py-2    text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
                >
                  Edit draft · {slot.slice(0, 8)}… · {formatDraftTime(updatedAt)}
                </button>
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

      {loading ? (
        <div className="mt-6 flex min-h-48 items-center justify-center">
          <LoadingSpinner />
        </div>
      ) : workOrders.length === 0 ? (
        <div className="mt-6 flex flex-col items-center justify-center border border-black bg-surface-white p-10 text-center">
          <div className="mb-4 border border-black bg-black p-4 text-white">
            <ClipboardList className="h-8 w-8" strokeWidth={1.75} />
          </div>
          <p className="mb-2 font-mono text-[10px] uppercase tracking-widest text-on-surface">No work orders</p>
          <p className="font-mono text-[10px] uppercase tracking-widest text-outline-muted">Create your first work order.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {workOrders.map((wo) => (
            <div
              key={wo.id}
              onClick={() => onSelect(wo.id)}
              onKeyDown={(e) => e.key === 'Enter' && onSelect(wo.id)}
              role="button"
              tabIndex={0}
              className="cursor-pointer border border-black bg-surface-white p-4 transition-colors duration-100 hover:bg-surface-container sm:p-5"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    <span className="border border-black bg-white px-2 py-0.5  text-[9px]  ">
                      {wo.work_order_number || wo.id.slice(0, 8)}
                    </span>
                    <span
                      className={`border px-2 py-0.5  text-[9px]   ${STATUS_STYLES[wo.status] || STATUS_STYLES.pending}`}
                    >
                      {STATUS_LABELS[wo.status]}
                    </span>
                  </div>
                  <p className="truncate text-base font-normal  tracking-tight">{wo.client_name}</p>
                  <div className="mt-2 space-y-1 border-l border-black pl-2">
                    {wo.assigned_to && (
                      <p className="  text-outline-muted">{wo.assigned_to}</p>
                    )}
                    {wo.start_date && (
                      <p className="  text-outline-muted">
                        {wo.start_date}
                        {wo.end_date ? ` → ${wo.end_date}` : ''}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-3">
                  {wo.total_cost != null && (
                    <span className="text-lg font-light tracking-tighter md:text-xl">
                      ₹{Number(wo.total_cost).toLocaleString('en-IN')}
                    </span>
                  )}
                  <button
                    type="button"
                    onClick={(e) => handleDelete(e, wo.id)}
                    className="flex h-10 w-10 items-center justify-center border border-black bg-white text-on-surface transition-colors duration-100 hover:bg-error hover:text-white"
                  >
                    <span className="text-sm" aria-hidden>
                      ×
                    </span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-4 pt-4">
          <button
            type="button"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="border border-black bg-white px-4 py-2    transition-colors duration-100 hover:bg-black hover:text-white disabled:opacity-40"
          >
            Prev
          </button>
          <span className="   text-outline-muted">
            {page} / {totalPages}
          </span>
          <button
            type="button"
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="border border-black bg-white px-4 py-2    transition-colors duration-100 hover:bg-black hover:text-white disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}

      <button
        type="button"
        onClick={onNew}
        className="fixed bottom-20 right-4 z-40 sm:right-6 md:bottom-8 md:right-8 lg:right-12"
        aria-label="New work order"
      >
        <div className="flex h-14 w-14 items-center justify-center border-2 border-black bg-black text-white transition-colors duration-100 hover:bg-white hover:text-black md:h-16 md:w-16">
          <Plus className="h-7 w-7" strokeWidth={2} />
        </div>
      </button>
    </div>
  );
}
