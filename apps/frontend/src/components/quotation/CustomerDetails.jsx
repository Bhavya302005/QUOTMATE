import Input from '../common/Input';

export default function CustomerDetails({ register, errors }) {
  return (
    <div className="space-y-4 border border-black bg-surface-white p-4">
      <h3 className="stitch-label opacity-80">Customer</h3>

      <Input
        label="Customer name"
        error={errors.customer_name?.message}
        registration={register('customer_name', {
          required: 'Customer name is required',
          minLength: { value: 2, message: 'Minimum 2 characters' },
        })}
        placeholder="Enter customer name"
      />

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Input
          label="Phone"
          error={errors.customer_phone?.message}
          registration={register('customer_phone')}
          placeholder="10-digit mobile"
        />

        <Input
          label="Email"
          type="email"
          error={errors.customer_email?.message}
          registration={register('customer_email', {
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: 'Invalid email address',
            },
          })}
          placeholder="customer@example.com"
        />
      </div>

      <Input
        label="Customer GST"
        error={errors.customer_gst?.message}
        registration={register('customer_gst')}
        placeholder="Optional"
      />

      <div>
        <label className="mb-1.5 block stitch-label">Address</label>
        <textarea
          rows={3}
          className="w-full border border-outline-variant bg-surface-white px-3 py-2.5 text-sm text-on-surface placeholder:text-outline-muted focus:border-black focus:outline-none focus:ring-0"
          {...register('customer_address')}
          placeholder="Billing address"
        />
        {errors.customer_address?.message && (
          <p className="mt-1    text-error">
            {errors.customer_address.message}
          </p>
        )}
      </div>
    </div>
  );
}
