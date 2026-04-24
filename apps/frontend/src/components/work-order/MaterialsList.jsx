import { useState } from 'react';
import Button from '../common/Button.jsx';

const emptyMaterial = { material_name: '', quantity: '', unit: '', unit_cost: '', total_cost: '' };

const inputCls =
  'w-full border border-outline-variant bg-surface-white px-2 py-1  text-on-surface focus:border-black focus:outline-none focus:ring-0';

export default function MaterialsList({ materials = [], onChange, onSave, onDelete, readOnly = false }) {
  const [editing, setEditing] = useState(null);
  const [draft, setDraft] = useState(emptyMaterial);
  const [adding, setAdding] = useState(false);

  const computeTotal = (qty, uc) => {
    const q = parseFloat(qty) || 0;
    const u = parseFloat(uc) || 0;
    return q * u || '';
  };

  const handleDraftChange = (field, value) => {
    const updated = { ...draft, [field]: value };
    if (field === 'quantity' || field === 'unit_cost') {
      updated.total_cost = computeTotal(
        field === 'quantity' ? value : draft.quantity,
        field === 'unit_cost' ? value : draft.unit_cost
      );
    }
    setDraft(updated);
  };

  const toMat = (d) => ({
    ...d,
    quantity: d.quantity !== '' ? parseFloat(d.quantity) : null,
    unit_cost: d.unit_cost !== '' ? parseFloat(d.unit_cost) : null,
    total_cost: d.total_cost !== '' ? parseFloat(d.total_cost) : null,
  });

  const handleAddSave = () => {
    if (!draft.material_name.trim()) return;
    const mat = toMat(draft);
    if (onSave) onSave(mat);
    else onChange([...materials, mat]);
    setAdding(false);
    setDraft(emptyMaterial);
  };

  const handleEditSave = (idx) => {
    const mat = toMat(draft);
    if (onSave) onSave(mat, materials[idx].id);
    else {
      const u = [...materials];
      u[idx] = mat;
      onChange(u);
    }
    setEditing(null);
  };

  const handleDelete = (idx) => {
    if (onDelete) onDelete(materials[idx].id);
    else onChange(materials.filter((_, i) => i !== idx));
  };

  const totalAll = materials.reduce((sum, m) => sum + (parseFloat(m.total_cost) || 0), 0);

  const FIELDS = ['material_name', 'quantity', 'unit', 'unit_cost', 'total_cost'];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="stitch-label opacity-80">Materials</h3>
        {!readOnly && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              setDraft(emptyMaterial);
              setAdding(true);
            }}
          >
            + Add
          </Button>
        )}
      </div>

      <div className="overflow-x-auto border border-black">
        <table className="w-full text-sm font-light">
          <thead className="border-b border-black bg-surface-container   ">
            <tr>
              {['Material', 'Qty', 'Unit', 'Unit cost', 'Total'].map((h) => (
                <th
                  key={h}
                  className={`py-2 px-3 font-normal ${h === 'Material' || h === 'Unit' ? 'text-left' : 'text-right'}`}
                >
                  {h}
                </th>
              ))}
              {!readOnly && <th className="py-2 px-3" />}
            </tr>
          </thead>
          <tbody>
            {materials.map((m, idx) =>
              editing === idx ? (
                <tr key={idx} className="border-b border-outline-variant bg-surface-container">
                  {FIELDS.map((f) => (
                    <td key={f} className="py-1 px-2">
                      <input
                        type={f === 'material_name' || f === 'unit' ? 'text' : 'number'}
                        value={draft[f] ?? ''}
                        onChange={(e) => handleDraftChange(f, e.target.value)}
                        className={inputCls}
                      />
                    </td>
                  ))}
                  <td className="py-1 px-2">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => handleEditSave(idx)}
                        className="   text-on-surface underline"
                      >
                        Save
                      </button>
                      <button
                        type="button"
                        onClick={() => setEditing(null)}
                        className="   text-outline-muted"
                      >
                        Cancel
                      </button>
                    </div>
                  </td>
                </tr>
              ) : (
                <tr key={idx} className="border-b border-outline-variant hover:bg-surface-container">
                  <td className="py-2 px-3">{m.material_name}</td>
                  <td className="py-2 px-3 text-right ">{m.quantity ?? '—'}</td>
                  <td className="py-2 px-3 ">{m.unit ?? '—'}</td>
                  <td className="py-2 px-3 text-right ">
                    {m.unit_cost != null ? `₹${m.unit_cost}` : '—'}
                  </td>
                  <td className="py-2 px-3 text-right  font-normal">
                    {m.total_cost != null ? `₹${Number(m.total_cost).toLocaleString('en-IN')}` : '—'}
                  </td>
                  {!readOnly && (
                    <td className="py-2 px-3">
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => {
                            setEditing(idx);
                            setDraft({
                              ...m,
                              quantity: m.quantity ?? '',
                              unit_cost: m.unit_cost ?? '',
                              total_cost: m.total_cost ?? '',
                              unit: m.unit ?? '',
                            });
                          }}
                          className="   underline"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(idx)}
                          className="   text-error"
                        >
                          Del
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              )
            )}

            {adding && (
              <tr className="border-b border-black bg-surface-container">
                {FIELDS.map((f) => (
                  <td key={f} className="py-1 px-2">
                    <input
                      type={f === 'material_name' || f === 'unit' ? 'text' : 'number'}
                      value={draft[f]}
                      onChange={(e) => handleDraftChange(f, e.target.value)}
                      className={inputCls}
                      placeholder={f.replace(/_/g, ' ')}
                    />
                  </td>
                ))}
                <td className="py-1 px-2">
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={handleAddSave}
                      className="   underline"
                    >
                      Add
                    </button>
                    <button
                      type="button"
                      onClick={() => setAdding(false)}
                      className="  text-outline-muted"
                    >
                      Cancel
                    </button>
                  </div>
                </td>
              </tr>
            )}

            {materials.length > 0 && (
              <tr className="border-t-2 border-black bg-surface-container font-normal">
                <td colSpan={4} className="py-2 px-3 text-right   ">
                  Material total
                </td>
                <td className="py-2 px-3 text-right ">
                  ₹{totalAll.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </td>
                {!readOnly && <td />}
              </tr>
            )}
          </tbody>
        </table>
        {materials.length === 0 && !adding && (
          <p className="py-4 text-center    text-outline-muted">
            No materials yet.
          </p>
        )}
      </div>
    </div>
  );
}
