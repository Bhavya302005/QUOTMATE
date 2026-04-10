import { useState, useEffect, useLayoutEffect, useRef, useMemo } from 'react';
import { workOrderAPI, getApiErrorMessage } from '../../services/api';
import Button from '../common/Button.jsx';
import MaterialsList from './MaterialsList.jsx';
import PhotoUpload from './PhotoUpload.jsx';
import SignaturePad from './SignaturePad.jsx';
import toast from 'react-hot-toast';
import {
  loadDraft,
  saveDraft,
  clearDraft,
  workOrderDraftHasContent,
} from '../../utils/draftStorage';

function draftPhotosForStorage(photos) {
  const p = photos && typeof photos === 'object' ? photos : {};
  return {
    before: typeof p.before === 'string' && p.before.startsWith('http') ? p.before : null,
    after: typeof p.after === 'string' && p.after.startsWith('http') ? p.after : null,
  };
}

function trimOrNull(v) {
  if (v == null) return null;
  const s = String(v).trim();
  return s || null;
}

function parseLaborNum(v) {
  if (v === '' || v == null) return null;
  const n = parseFloat(v);
  return Number.isFinite(n) ? n : null;
}

function materialsForApi(list) {
  return (Array.isArray(list) ? list : [])
    .filter((m) => m && String(m.material_name || '').trim())
    .map((m) => ({
      material_name: String(m.material_name).trim(),
      quantity: m.quantity === '' || m.quantity == null ? null : parseFloat(m.quantity),
      unit: trimOrNull(m.unit),
      unit_cost: m.unit_cost === '' || m.unit_cost == null ? null : parseFloat(m.unit_cost),
      total_cost: m.total_cost === '' || m.total_cost == null ? null : parseFloat(m.total_cost),
    }));
}

const EMPTY_FORM = {
  client_name: '',
  client_phone: '',
  client_email: '',
  service_location: '',
  work_description: '',
  assigned_to: '',
  start_date: '',
  end_date: '',
  labor_hours: '',
  labor_rate: '',
  remarks: '',
  linked_quotation_id: '',
};

export default function WorkOrderForm({ workOrderId, ocrData, onSaved, onCancel, resumeDraft = false }) {
  // Pre-fill from OCR data when creating a new work order via scan
  const ocrSuggested = ocrData?.suggested_work_order || null;
  const exitCleanRef = useRef(false);

  const ocrFormDefaults = useMemo(
    () =>
      ocrSuggested
        ? {
            client_name: ocrSuggested.client_name || '',
            client_phone: ocrSuggested.client_phone || '',
            client_email: ocrSuggested.client_email || '',
            service_location: ocrSuggested.service_location || '',
            work_description: ocrSuggested.work_description || '',
            assigned_to: ocrSuggested.assigned_to || '',
            remarks: ocrSuggested.remarks || '',
          }
        : {},
    [ocrSuggested]
  );

  const [form, setForm] = useState(() => {
    const base = { ...EMPTY_FORM, ...ocrFormDefaults };
    if (workOrderId) return base;
    if (!resumeDraft) return base;
    const d = loadDraft('workorder', 'new');
    if (d?.form && workOrderDraftHasContent(d)) {
      return { ...base, ...d.form };
    }
    return base;
  });

  const [materials, setMaterials] = useState(() => {
    if (workOrderId) return [];
    const d = resumeDraft ? loadDraft('workorder', 'new') : null;
    if (d?.materials?.length) return d.materials;
    return (
      ocrSuggested?.materials?.map((m, i) => ({
        ...m,
        id: `tmp-ocr-${i}`,
        total_cost:
          m.total_cost ?? (m.quantity && m.unit_cost ? parseFloat(m.quantity) * parseFloat(m.unit_cost) : null),
      })) || []
    );
  });
  const [savedId, setSavedId] = useState(workOrderId || null);
  const [photos, setPhotos] = useState(() => {
    if (workOrderId) return { before: null, after: null };
    const d = resumeDraft ? loadDraft('workorder', 'new') : null;
    return d?.photos || { before: null, after: null };
  });
  const [signatureUrl, setSignatureUrl] = useState(() => {
    if (workOrderId) return null;
    const d = resumeDraft ? loadDraft('workorder', 'new') : null;
    return d?.signatureUrl ?? null;
  });
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(!!workOrderId);
  const [costs, setCosts] = useState({ labor_cost: null, material_cost: null, total_cost: null });
  const [tab, setTab] = useState(() => {
    if (workOrderId) return loadDraft('workorder', workOrderId)?.tab || 'details';
    if (!resumeDraft) return 'details';
    return loadDraft('workorder', 'new')?.tab || 'details';
  });

  const draftSlot = workOrderId || savedId || 'new';

  const stateRef = useRef({
    form,
    materials,
    tab,
    savedId,
    photos,
    signatureUrl,
    draftSlot,
  });
  stateRef.current = { form, materials, tab, savedId, photos, signatureUrl, draftSlot };

  const flushDraft = useRef(() => {});
  flushDraft.current = () => {
    if (exitCleanRef.current) return;
    const s = stateRef.current;
    const payload = {
      form: s.form,
      materials: Array.isArray(s.materials) ? s.materials : [],
      tab: s.tab,
      savedId: s.savedId,
      photos: draftPhotosForStorage(s.photos),
      signatureUrl: typeof s.signatureUrl === 'string' && s.signatureUrl.startsWith('http') ? s.signatureUrl : null,
    };
    if (workOrderDraftHasContent(payload)) {
      saveDraft('workorder', s.draftSlot, payload);
    } else {
      clearDraft('workorder', s.draftSlot);
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

  // Load existing work order
  useEffect(() => {
    if (!workOrderId) return;
    setLoading(true);
    workOrderAPI
      .get(workOrderId)
      .then((resp) => {
        const wo = resp.data;
        const baseForm = {
          client_name: wo.client_name || '',
          client_phone: wo.client_phone || '',
          client_email: wo.client_email || '',
          service_location: wo.service_location || '',
          work_description: wo.work_description || '',
          assigned_to: wo.assigned_to || '',
          start_date: wo.start_date || '',
          end_date: wo.end_date || '',
          labor_hours: wo.labor_hours || '',
          labor_rate: wo.labor_rate || '',
          remarks: wo.remarks || '',
          linked_quotation_id: wo.linked_quotation_id || '',
        };
        setForm(baseForm);
        setMaterials(wo.materials || []);
        setPhotos({ before: wo.before_photo_url, after: wo.after_photo_url });
        setSignatureUrl(wo.customer_signature_url);
        setCosts({ labor_cost: wo.labor_cost, material_cost: wo.material_cost, total_cost: wo.total_cost });

        const d = loadDraft('workorder', workOrderId);
        if (d?.form && workOrderDraftHasContent(d)) {
          setForm((f) => ({ ...f, ...d.form }));
          if (d.materials?.length) setMaterials(d.materials);
          if (d.tab) setTab(d.tab);
          if (d.photos) {
            setPhotos((p) => ({
              before: d.photos.before || p.before,
              after: d.photos.after || p.after,
            }));
          }
          if (d.signatureUrl) setSignatureUrl(d.signatureUrl);
        }
      })
      .catch(() => toast.error('Failed to load work order'))
      .finally(() => setLoading(false));
  }, [workOrderId]);

  useEffect(() => {
    const t = setTimeout(() => {
      const payload = {
        form,
        materials: Array.isArray(materials) ? materials : [],
        tab,
        savedId,
        photos: draftPhotosForStorage(photos),
        signatureUrl: typeof signatureUrl === 'string' && signatureUrl.startsWith('http') ? signatureUrl : null,
      };
      if (workOrderDraftHasContent(payload)) {
        saveDraft('workorder', draftSlot, payload);
      } else {
        clearDraft('workorder', draftSlot);
      }
    }, 500);
    return () => clearTimeout(t);
  }, [form, materials, tab, savedId, photos, signatureUrl, draftSlot]);

  const handleChange = (field, value) => setForm(f => ({ ...f, [field]: value }));

  // Auto-calculate costs when labor fields change
  useEffect(() => {
    const h = parseFloat(form.labor_hours) || 0;
    const r = parseFloat(form.labor_rate) || 0;
    const laborCost = h * r;
    const matTotal = (Array.isArray(materials) ? materials : []).reduce((s, m) => s + (parseFloat(m.total_cost) || 0), 0);
    setCosts({ labor_cost: laborCost, material_cost: matTotal, total_cost: laborCost + matTotal });
  }, [form.labor_hours, form.labor_rate, materials]);

  const handleSave = async () => {
    if (!form.client_name.trim()) { toast.error('Client name is required'); return; }
    setSaving(true);
    try {
      const base = {
        client_name: form.client_name.trim(),
        client_phone: trimOrNull(form.client_phone),
        client_email: trimOrNull(form.client_email),
        service_location: trimOrNull(form.service_location),
        work_description: trimOrNull(form.work_description),
        assigned_to: trimOrNull(form.assigned_to),
        start_date: trimOrNull(form.start_date),
        end_date: trimOrNull(form.end_date),
        labor_hours: parseLaborNum(form.labor_hours),
        labor_rate: parseLaborNum(form.labor_rate),
        remarks: trimOrNull(form.remarks),
        linked_quotation_id: trimOrNull(form.linked_quotation_id),
      };

      let resp;
      if (savedId) {
        resp = await workOrderAPI.update(savedId, base);
      } else {
        resp = await workOrderAPI.create({ ...base, materials: materialsForApi(materials) });
        setSavedId(resp.data.id);
      }
      exitCleanRef.current = true;
      clearDraft('workorder', savedId || 'new');
      if (resp.data?.id) clearDraft('workorder', resp.data.id);
      queueMicrotask(() => {
        exitCleanRef.current = false;
      });
      toast.success(`Work order ${savedId ? 'updated' : 'created'} — ${resp.data.work_order_number}`);
      onSaved?.(resp.data);
    } catch (e) {
      toast.error(getApiErrorMessage(e, 'Save failed'));
    } finally {
      setSaving(false);
    }
  };

  // Materials CRUD callbacks when work order already exists
  const handleMaterialSave = async (mat, existingId) => {
    if (!savedId) {
      if (existingId) {
        setMaterials(ms => ms.map(m => m.id === existingId ? { ...m, ...mat } : m));
      } else {
        setMaterials(ms => [...ms, { ...mat, id: `tmp-${Date.now()}` }]);
      }
      return;
    }
    try {
      if (existingId) {
        const resp = await workOrderAPI.updateMaterial(savedId, existingId, mat);
        setMaterials(ms => ms.map(m => m.id === existingId ? resp.data : m));
      } else {
        const resp = await workOrderAPI.addMaterial(savedId, mat);
        setMaterials(ms => [...ms, resp.data]);
      }
    } catch { toast.error('Failed to save material'); }
  };

  const handleMaterialDelete = async (matId) => {
    if (!savedId || matId.startsWith('tmp-')) {
      setMaterials(ms => ms.filter(m => m.id !== matId));
      return;
    }
    try {
      await workOrderAPI.deleteMaterial(savedId, matId);
      setMaterials(ms => ms.filter(m => m.id !== matId));
    } catch { toast.error('Failed to delete material'); }
  };

  const handlePhotoChange = (photoType, url) => {
    setPhotos(p => ({ ...p, [photoType]: url }));
  };

  const handleFinalize = async () => {
    if (!savedId) { toast.error('Save the work order first'); return; }
    try {
      await workOrderAPI.finalize(savedId);
      exitCleanRef.current = true;
      clearDraft('workorder', savedId);
      queueMicrotask(() => {
        exitCleanRef.current = false;
      });
      toast.success('Work order completed!');
      onSaved?.();
    } catch { toast.error('Failed to finalize'); }
  };

  const fieldCls =
    'w-full border border-outline-variant bg-surface-white px-3 py-2 text-sm text-on-surface focus:border-black focus:outline-none focus:ring-0';

  const Field = ({ label, field, type = 'text', required, ...props }) => (
    <div>
      <label className="mb-1 block stitch-label">
        {label}
        {required && ' *'}
      </label>
      {type === 'textarea' ? (
        <textarea
          rows={3}
          value={form[field]}
          onChange={(e) => handleChange(field, e.target.value)}
          className={`${fieldCls} min-h-[4.5rem]`}
          {...props}
        />
      ) : (
        <input
          type={type}
          value={form[field]}
          onChange={(e) => handleChange(field, e.target.value)}
          className={fieldCls}
          {...props}
        />
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="py-6 text-center    text-outline-muted">
        Loading…
      </div>
    );
  }

  const TABS = [
    { id: 'details', label: 'Details' },
    { id: 'materials', label: `Materials (${materials.length})` },
    { id: 'photos', label: 'Photos' },
    { id: 'signature', label: 'Signature' },
  ];

  return (
    <div className="space-y-4">
      {/* Tab Bar */}
      <div className="flex gap-1 border-b border-black">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`border-b-2 px-3 py-2    transition-colors duration-100 ${
              tab === t.id
                ? 'border-black text-on-surface'
                : 'border-transparent text-outline-muted hover:text-on-surface'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === 'details' && (
        <div className="space-y-3">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field label="Client Name" field="client_name" required placeholder="Client or company name" />
            <Field label="Phone" field="client_phone" type="tel" placeholder="+91 9XXXXXXXX" />
            <Field label="Email" field="client_email" type="email" placeholder="client@example.com" />
            <Field label="Assigned To" field="assigned_to" placeholder="Technician name" />
            <Field label="Start Date" field="start_date" type="date" />
            <Field label="End Date" field="end_date" type="date" />
            <Field label="Labor Hours" field="labor_hours" type="number" min="0" step="0.5" placeholder="Hours" />
            <Field label="Labor Rate (₹/hr)" field="labor_rate" type="number" min="0" step="0.01" placeholder="Rate per hour" />
          </div>
          <Field label="Service Location" field="service_location" type="textarea" placeholder="Job site address" />
          <Field label="Work Description" field="work_description" type="textarea" placeholder="Describe the work to be done…" />
          <Field label="Remarks" field="remarks" type="textarea" placeholder="Additional notes…" />

          {/* Cost Summary */}
          {(costs.labor_cost > 0 || costs.material_cost > 0) && (
            <div className="space-y-1 border border-dashed border-black/30 bg-surface-container p-3 text-sm font-light">
              <p className="stitch-label opacity-80">Cost preview</p>
              <div className="flex justify-between">
                <span className="text-outline-muted">Labor</span>
                <span className="">₹{(costs.labor_cost || 0).toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-outline-muted">Materials</span>
                <span className="">₹{(costs.material_cost || 0).toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between border-t border-black pt-1 font-normal">
                <span>Total</span>
                <span className="">₹{(costs.total_cost || 0).toLocaleString('en-IN')}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {tab === 'materials' && (
        <MaterialsList
          materials={materials}
          onChange={setMaterials}
          onSave={savedId ? handleMaterialSave : undefined}
          onDelete={savedId ? handleMaterialDelete : undefined}
        />
      )}

      {tab === 'photos' && (
        <PhotoUpload
          workOrderId={savedId}
          beforeUrl={photos.before}
          afterUrl={photos.after}
          onChange={handlePhotoChange}
        />
      )}

      {tab === 'signature' && (
        <SignaturePad
          workOrderId={savedId}
          existingUrl={signatureUrl}
          onChange={setSignatureUrl}
        />
      )}

      {/* Action Buttons */}
      <div className="flex gap-2 border-t border-black pt-3">
        <Button variant="outline" onClick={onCancel} className="flex-1">
          Cancel
        </Button>
        <Button onClick={handleSave} disabled={saving} isLoading={saving} className="flex-1">
          {savedId ? 'Update' : 'Create'}
        </Button>
        {savedId && (
          <Button type="button" onClick={handleFinalize} className="flex-1">
            Complete
          </Button>
        )}
      </div>
    </div>
  );
}


