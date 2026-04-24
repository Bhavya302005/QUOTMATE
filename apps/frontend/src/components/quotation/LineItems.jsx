import { useFieldArray } from 'react-hook-form';
import { Plus, Trash2 } from 'lucide-react';

const inputCls =
  'w-full border border-outline-variant bg-surface-white px-2 py-2 text-sm text-on-surface focus:border-black focus:outline-none focus:ring-0';

const EMPTY_ITEM = {
  description: '',
  quantity: 1,
  unit: 'nos',
  unit_price: 0,
  gst_rate: 18,
  is_free_text: true,
  product_id: null,
};

export default function LineItems({ control, register, errors, products = [], isGstOn = true }) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  const addFromProduct = (productId) => {
    const product = products.find((item) => item.id === productId);
    if (!product) return;

    append({
      description: product.name,
      quantity: 1,
      unit: product.unit || 'nos',
      unit_price: Number(product.default_price || 0),
      gst_rate: Number(product.gst_rate || 18),
      product_id: product.id,
      is_free_text: false,
    });
  };

  return (
    <div className="space-y-4 border border-black bg-surface-white p-4">
      <div className="flex items-center justify-between gap-2">
        <h3 className="stitch-label opacity-80">Line items</h3>
        <button
          type="button"
          onClick={() => append({ ...EMPTY_ITEM })}
          className="inline-flex items-center gap-1 border border-black bg-white px-3 py-1.5    text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
        >
          <Plus className="h-3.5 w-3.5" strokeWidth={2} /> Add
        </button>
      </div>

      {products.length > 0 && (
        <div>
          <label className="mb-1 block    text-outline-muted">
            Quick add from inventory
          </label>
          <select
            defaultValue=""
            onChange={(event) => {
              addFromProduct(event.target.value);
              event.target.value = '';
            }}
            className={inputCls}
          >
            <option value="">Select product…</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.name} — ₹{Number(product.default_price || 0).toFixed(2)}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="space-y-3">
        {fields.map((field, index) => (
          <div key={field.id} className="mb-3 border border-outline-variant bg-surface-white p-3">
            <div className="mb-2 flex items-center justify-between">
              <p className="   text-outline-muted">
                Item {index + 1}
              </p>
              {fields.length > 1 && (
                <button
                  type="button"
                  onClick={() => remove(index)}
                  className="border border-black bg-white p-1 text-on-surface transition-colors duration-100 hover:bg-error hover:text-white"
                >
                  <Trash2 className="h-4 w-4" strokeWidth={2} />
                </button>
              )}
            </div>

            <div className="space-y-2">
              <input
                {...register(`items.${index}.description`, { required: 'Description required' })}
                placeholder="Description"
                className={inputCls}
              />
              {errors.items?.[index]?.description && (
                <p className=" text-error">{errors.items[index].description.message}</p>
              )}

              <div className={`grid grid-cols-2 gap-2 ${isGstOn ? 'sm:grid-cols-5' : 'sm:grid-cols-4'}`}>
                <input
                  type="number"
                  step="0.01"
                  {...register(`items.${index}.quantity`, {
                    required: 'Required',
                    min: { value: 0.01, message: 'Min 0.01' },
                    valueAsNumber: true,
                  })}
                  placeholder="Qty"
                  className={inputCls}
                />

                <select {...register(`items.${index}.unit`)} className={inputCls}>
                  <option value="nos">Nos</option>
                  <option value="pcs">Pcs</option>
                  <option value="kg">Kg</option>
                  <option value="ltr">Ltr</option>
                  <option value="box">Box</option>
                </select>

                <input
                  type="number"
                  step="0.01"
                  {...register(`items.${index}.unit_price`, {
                    required: 'Required',
                    min: { value: 0, message: 'Min 0' },
                    valueAsNumber: true,
                  })}
                  placeholder="Rate"
                  className={inputCls}
                />

                {isGstOn && (
                  <select
                    {...register(`items.${index}.gst_rate`, { valueAsNumber: true })}
                    className={inputCls}
                  >
                    <option value={0}>0%</option>
                    <option value={5}>5%</option>
                    <option value={12}>12%</option>
                    <option value={18}>18%</option>
                    <option value={28}>28%</option>
                  </select>
                )}

                <input type="hidden" {...register(`items.${index}.is_free_text`)} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
