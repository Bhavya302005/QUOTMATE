/**
 * Client-side form drafts (localStorage). Keys are namespaced per document kind + id.
 * "new" = unsaved create flow; UUID = edit flow for that entity.
 */

const PREFIX = 'quotmate_draft_v1';

function storageKey(kind, slot) {
  const id = slot === 'new' || !slot ? 'new' : String(slot);
  return `${PREFIX}_${kind}_${id}`;
}

function safeParse(raw) {
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function loadDraft(kind, slot) {
  return safeParse(localStorage.getItem(storageKey(kind, slot)));
}

export function saveDraft(kind, slot, payload) {
  const record = {
    v: 1,
    updatedAt: Date.now(),
    ...payload,
  };
  try {
    localStorage.setItem(storageKey(kind, slot), JSON.stringify(record));
  } catch {
    // quota exceeded — ignore
  }
}

export function clearDraft(kind, slot) {
  localStorage.removeItem(storageKey(kind, slot));
}

export function hasDraft(kind, slot) {
  const d = loadDraft(kind, slot);
  return Boolean(d?.values || d?.form);
}

/** List all drafts for a kind: [{ slot, updatedAt, label? }] */
export function listDraftSlots(kind) {
  const p = `${PREFIX}_${kind}_`;
  const out = [];
  for (let i = 0; i < localStorage.length; i += 1) {
    const k = localStorage.key(i);
    if (!k || !k.startsWith(p)) continue;
    const d = safeParse(localStorage.getItem(k));
    if (!d?.updatedAt) continue;
    const slot = k.slice(p.length);
    out.push({
      slot: slot === 'new' ? 'new' : slot,
      updatedAt: d.updatedAt,
    });
  }
  return out.sort((a, b) => b.updatedAt - a.updatedAt);
}

export function formatDraftTime(ts) {
  if (!ts) return '';
  try {
    return new Date(ts).toLocaleString(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  } catch {
    return '';
  }
}

export function quotationDraftHasContent(v) {
  if (!v) return false;
  const textFields = [
    'customer_name',
    'customer_email',
    'customer_phone',
    'customer_address',
    'customer_gst',
    'notes',
    'terms_conditions',
  ];
  if (textFields.some((f) => String(v[f] || '').trim())) return true;
  if (v.items?.some((i) => String(i?.description || '').trim())) return true;
  if (Number(v.discount_percent) > 0) return true;
  if (v.manual_total_amount !== '' && v.manual_total_amount != null && v.manual_total_amount !== undefined)
    return true;
  if (String(v.valid_until || '').trim()) return true;
  if (String(v.document_id || '').trim()) return true;
  return false;
}

export function momDraftHasContent(v) {
  if (!v) return false;
  const fields = [
    'meeting_title',
    'meeting_date',
    'location',
    'attendees_text',
    'raw_notes',
    'meeting_context',
    'ai_summary',
    'key_points_text',
    'decisions_text',
    'next_steps_text',
  ];
  if (fields.some((f) => String(v[f] || '').trim())) return true;
  return false;
}

export function workOrderDraftHasContent(state) {
  if (!state?.form) return false;
  const f = state.form;
  if (String(f.client_name || '').trim()) return true;
  const rest = ['client_phone', 'client_email', 'service_location', 'work_description', 'assigned_to', 'remarks'];
  if (rest.some((k) => String(f[k] || '').trim())) return true;
  if (f.labor_hours || f.labor_rate) return true;
  if (state.materials?.length) return true;
  return false;
}
