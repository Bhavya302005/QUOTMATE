import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import { createPortal } from 'react-dom';
import { Eye, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { quotationAPI, productAPI, getApiErrorMessage } from '../../services/api';
import { loadDraft, saveDraft, clearDraft, quotationDraftHasContent } from '../../utils/draftStorage';
import { useAuth } from '../../context/AuthContext';
import Button from '../common/Button';
import CustomerDetails from './CustomerDetails';
import LineItems from './LineItems';
import GSTSummary from './GSTSummary';
import QuotationPreview from './QuotationPreview';

function normalizeItem(item) {
  return {
    description: String(item.description || '').trim(),
    quantity: Number(item.quantity || 0),
    unit: item.unit || 'nos',
    unit_price: Number(item.unit_price || 0),
    gst_rate: Number(item.gst_rate ?? 18),
    product_id: item.product_id || null,
    is_free_text: item.is_free_text !== false,
  };
}

const EMPTY_SOURCE = {};

function buildDefaults(source, user) {
  const items = Array.isArray(source?.items) && source.items.length > 0
    ? source.items.map(normalizeItem)
    : [{ description: '', quantity: 1, unit: 'nos', unit_price: 0, gst_rate: 18, is_free_text: true, product_id: null }];

  return {
    document_id: source?.document_id || '',
    customer_name: source?.customer_name || '',
    customer_email: source?.customer_email || '',
    customer_phone: source?.customer_phone || '',
    customer_address: source?.customer_address || '',
    customer_gst: source?.customer_gst || '',
    discount_percent: Number(source?.discount_percent || 0),
    is_igst: Boolean(source?.is_igst || false),
    is_gst_on: source?.is_gst_on !== false,
    manual_total_amount: source?.manual_total_amount || '',
    valid_until: source?.valid_until || '',
    terms_conditions: source?.terms_conditions || user?.default_terms_conditions || '',
    notes: source?.notes || '',
    items,
  };
}

export default function QuotationForm({ initialData, ocrData, onSuccess, resumeDraft = false }) {
  const { user } = useAuth();
  const sourceData = useMemo(() => ocrData || initialData || EMPTY_SOURCE, [ocrData, initialData]);
  const draftSlot = initialData?.id || 'new';
  const exitCleanRef = useRef(false);
  const [products, setProducts] = useState([]);
  const [totals, setTotals] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const lumpSumTotal = sourceData?.lump_sum_total;
  const isLumpSum = sourceData?.is_lump_sum_total;

  const {
    register,
    control,
    handleSubmit,
    watch,
    reset,
    getValues,
    formState: { errors, isDirty },
  } = useForm({ defaultValues: buildDefaults(sourceData, user) });

  const getValuesRef = useRef(getValues);
  const draftSlotRef = useRef(draftSlot);
  const isDirtyRef = useRef(isDirty);
  getValuesRef.current = getValues;
  draftSlotRef.current = draftSlot;
  isDirtyRef.current = isDirty;

  const watchedItems = watch('items');
  const watchedDiscount = watch('discount_percent');
  const watchedIsIgst = watch('is_igst');
  const watchedIsGstOn = watch('is_gst_on');
  const watchedManualTotal = watch('manual_total_amount');
  const formValues = watch();

  const ocrFingerprint = useMemo(() => (ocrData ? JSON.stringify(ocrData) : ''), [ocrData]);

  useEffect(() => {
    exitCleanRef.current = false;
    const base = buildDefaults(sourceData, user);
    const shouldLoadDraft = draftSlot !== 'new' || resumeDraft;
    const stored = shouldLoadDraft ? loadDraft('quotation', draftSlot) : null;
    if (stored?.values && quotationDraftHasContent(stored.values)) {
      const merged = { ...base, ...stored.values };
      merged.items =
        Array.isArray(stored.values.items) && stored.values.items.length > 0
          ? stored.values.items.map(normalizeItem)
          : base.items;
      reset(merged);
    } else {
      reset(base);
    }
  }, [draftSlot, reset, sourceData, ocrFingerprint, resumeDraft, user]);

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const response = await productAPI.list({ page_size: 100, is_active: true });
        setProducts(response.data?.products || []);
      } catch {
        setProducts([]);
      }
    };

    loadProducts();
  }, []);

  useEffect(() => {
    const timer = setTimeout(async () => {
      const normalizedItems = (watchedItems || [])
        .map(normalizeItem)
        .filter((item) => item.description && item.quantity > 0);

      if (normalizedItems.length === 0) {
        setTotals(null);
        return;
      }

      setIsCalculating(true);
      try {
        const payload = {
          items: normalizedItems,
          discount_percent: Number(watchedDiscount || 0),
          is_igst: Boolean(watchedIsIgst),
          is_gst_on: Boolean(watchedIsGstOn),
        };
        // Only override if manual total is actually typed in
        if (watchedManualTotal !== '' && watchedManualTotal !== null) {
          payload.manual_total_amount = Number(watchedManualTotal);
        }

        const response = await quotationAPI.calculate(payload);
        setTotals(response.data);
      } catch {
        setTotals(null);
      } finally {
        setIsCalculating(false);
      }
    }, 800);

    return () => clearTimeout(timer);
  }, [watchedItems, watchedDiscount, watchedIsIgst, watchedIsGstOn, watchedManualTotal]);

  useEffect(() => {
    const t = setTimeout(() => {
      const values = getValues();
      if (quotationDraftHasContent(values)) {
        saveDraft('quotation', draftSlot, { values });
      } else {
        clearDraft('quotation', draftSlot);
      }
    }, 500);
    return () => clearTimeout(t);
  }, [formValues, draftSlot, getValues]);

  const flushDraft = useRef(() => {});
  flushDraft.current = () => {
    if (exitCleanRef.current) return;
    const values = getValuesRef.current();
    const slot = draftSlotRef.current;
    if (isDirtyRef.current || quotationDraftHasContent(values)) {
      saveDraft('quotation', slot, { values });
    } else {
      clearDraft('quotation', slot);
    }
  };

  useEffect(() => {
    const onPageLeave = () => flushDraft.current();
    const onVis = () => {
      if (document.visibilityState === 'hidden') flushDraft.current();
    };
    window.addEventListener('pagehide', onPageLeave);
    window.addEventListener('beforeunload', onPageLeave);
    document.addEventListener('visibilitychange', onVis);
    return () => {
      window.removeEventListener('pagehide', onPageLeave);
      window.removeEventListener('beforeunload', onPageLeave);
      document.removeEventListener('visibilitychange', onVis);
    };
  }, []);

  useLayoutEffect(() => {
    return () => {
      flushDraft.current();
    };
  }, []);

  useEffect(() => {
    setIsMounted(true);
    return () => setIsMounted(false);
  }, []);

  const onSubmit = async (data) => {
    setIsSubmitting(true);

    try {
      const payload = {
        document_id: data.document_id || undefined,
        customer_name: data.customer_name,
        customer_email: data.customer_email || null,
        customer_phone: data.customer_phone || null,
        customer_address: data.customer_address || null,
        customer_gst: data.customer_gst || null,
        discount_percent: Number(data.discount_percent || 0),
        is_igst: Boolean(data.is_igst),
        is_gst_on: Boolean(data.is_gst_on),
        manual_total_amount: data.manual_total_amount ? Number(data.manual_total_amount) : null,
        valid_until: data.valid_until || null,
        terms_conditions: data.terms_conditions || null,
        notes: data.notes || null,
        items: (data.items || []).map(normalizeItem).filter((item) => item.description && item.quantity > 0),
      };

      if (payload.items.length === 0) {
        toast.error('Add at least one valid item');
        return;
      }

      const response = initialData?.id
        ? await quotationAPI.update(initialData.id, payload)
        : await quotationAPI.create(payload);

      exitCleanRef.current = true;
      clearDraft('quotation', draftSlot);
      queueMicrotask(() => {
        exitCleanRef.current = false;
      });
      toast.success(initialData?.id ? 'Quotation updated' : 'Quotation created');
      onSuccess?.(response.data);
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to save quotation'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const previewData = useMemo(() => {
    const items = (formValues.items || []).map(normalizeItem).filter((item) => item.description);

    const subtotal = totals?.subtotal ?? items.reduce(
      (acc, item) => acc + Number(item.quantity || 0) * Number(item.unit_price || 0),
      0
    );
    const cgstAmount = totals?.cgst_amount ?? 0;
    const sgstAmount = totals?.sgst_amount ?? 0;
    const igstAmount = totals?.igst_amount ?? 0;
    const discountAmount = totals?.discount_amount ?? 0;
    const grandTotal = totals?.grand_total ?? (subtotal - discountAmount + cgstAmount + sgstAmount + igstAmount);

    return {
      ...formValues,
      id: initialData?.id,
      quotation_number: initialData?.quotation_number || 'DRAFT',
      status: initialData?.status || 'draft',
      items: items.map((item) => ({
        ...item,
        unit_price: item.unit_price,
        total: watchedManualTotal ? 0 : Number(item.quantity || 0) * Number(item.unit_price || 0),
      })),
      subtotal,
      cgst_amount: cgstAmount,
      sgst_amount: sgstAmount,
      igst_amount: igstAmount,
      discount_amount: discountAmount,
      grand_total: grandTotal,
    };
  }, [formValues, totals, initialData]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <input type="hidden" {...register('document_id')} />

      <CustomerDetails register={register} errors={errors} />

      <LineItems
        control={control}
        register={register}
        errors={errors}
        products={products}
        isGstOn={watchedIsGstOn}
      />

      <div className="space-y-4 border border-black bg-surface-white p-4">
        <h3 className="stitch-label opacity-80">Tax &amp; terms</h3>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block stitch-label">Discount %</label>
            <input
              type="number"
              step="0.01"
              className="stitch-input"
              {...register('discount_percent', { valueAsNumber: true })}
            />
          </div>

          <label className="flex items-center gap-2 border border-outline-variant bg-surface-white px-3 py-2.5    text-on-surface">
            <input type="checkbox" {...register('is_igst')} disabled={!watchedIsGstOn} />
            Use IGST
          </label>

          <label className="flex items-center gap-2 border border-outline-variant bg-surface-white px-3 py-2.5    text-on-surface">
            <input type="checkbox" {...register('is_gst_on')} />
            Apply GST
          </label>

          <div>
            <label className="mb-1.5 block stitch-label">Manual total override</label>
            <input
              type="number"
              step="0.01"
              placeholder="Blank = auto"
              className="stitch-input"
              {...register('manual_total_amount')}
            />
          </div>
        </div>

        <div>
          <label className="mb-1.5 block stitch-label">Valid until</label>
          <input type="date" className="stitch-input" {...register('valid_until')} />
        </div>

        <div>
          <label className="mb-1.5 block stitch-label">Terms &amp; conditions</label>
          <textarea rows={3} className="stitch-input min-h-[4.5rem]" {...register('terms_conditions')} />
        </div>

        <div>
          <label className="mb-1.5 block stitch-label">Notes</label>
          <textarea rows={2} className="stitch-input min-h-[3.5rem]" {...register('notes')} />
        </div>
      </div>

      <GSTSummary totals={totals} isCalculating={isCalculating} lumpSumTotal={isLumpSum ? lumpSumTotal : null} />

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        <Button type="button" variant="outline" fullWidth onClick={() => setShowPreview(true)}>
          <Eye className="mr-2 h-4 w-4" /> Preview
        </Button>
        <Button type="submit" fullWidth isLoading={isSubmitting}>
          {initialData?.id ? 'Update Quotation' : 'Create Quotation'}
        </Button>
      </div>

      {showPreview && isMounted && createPortal(
        <div className="fixed inset-0 z-[70] bg-black/50 p-3 sm:p-6">
          <div className="mx-auto flex h-full max-w-5xl flex-col overflow-hidden border border-black bg-surface-white">
            <div className="flex items-center justify-between border-b border-black px-4 py-3">
              <h2 className="text-on-surface">Preview</h2>
              <button
                type="button"
                onClick={() => setShowPreview(false)}
                className="border border-black bg-white p-2 text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto p-4">
              <QuotationPreview quotation={previewData} showActions={false} />
            </div>
          </div>
        </div>,
        document.body
      )}
    </form>
  );
}
