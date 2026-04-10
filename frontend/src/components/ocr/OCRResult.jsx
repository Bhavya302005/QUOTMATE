import Button from '../common/Button';
import ConfidenceIndicator from './ConfidenceIndicator';

export default function OCRResult({ text, confidence, mappedFields, onEdit, onAccept, onRetake }) {
  const flags = mappedFields?.confidence_flags || [];
  const items = mappedFields?.items || [];
  const aiConfidence = mappedFields?.ai_confidence;
  const aiModel = mappedFields?.ai_model;
  const lumpSumTotal = mappedFields?.lump_sum_total;
  const isLumpSum = mappedFields?.is_lump_sum_total;

  return (
    <div className="space-y-4">
      <div className="border border-black bg-surface-white p-4">
        <h3 className="mb-3 stitch-label opacity-80">OCR output</h3>
        <ConfidenceIndicator confidence={confidence || 0} />
        {aiConfidence && (
          <div className="mt-2 flex flex-wrap items-center gap-2    text-on-surface">
            <span className="text-outline-muted">AI parse</span>
            <span className="border border-black px-2 py-0.5">{aiConfidence}</span>
            {aiModel && <span className="text-outline-muted">({aiModel.split('/').pop()})</span>}
          </div>
        )}
        <pre className="mt-3 max-h-52 overflow-auto whitespace-pre-wrap border border-outline-variant bg-surface-container p-3  text-on-surface">
          {text || 'No text extracted'}
        </pre>
      </div>

      <div className="border border-black bg-surface-white p-4">
        <h3 className="mb-3 stitch-label opacity-80">Mapped fields</h3>
        <div className="space-y-1 text-sm font-light text-on-surface">
          {mappedFields?.company_name && (
            <p>
              <span className="  text-outline-muted">Company: </span>
              {mappedFields.company_name}
            </p>
          )}
          {mappedFields?.quotation_date && (
            <p>
              <span className="  text-outline-muted">Date: </span>
              {mappedFields.quotation_date}
            </p>
          )}
          <p>
            <span className="  text-outline-muted">Customer: </span>
            {mappedFields?.customer_name || '—'}
          </p>
          <p>
            <span className="  text-outline-muted">Phone: </span>
            {mappedFields?.customer_phone || '—'}
          </p>
          {mappedFields?.customer_address && (
            <p>
              <span className="  text-outline-muted">Address: </span>
              {mappedFields.customer_address}
            </p>
          )}
          <p>
            <span className="  text-outline-muted">Email: </span>
            {mappedFields?.customer_email || '—'}
          </p>
          <p>
            <span className="  text-outline-muted">GST: </span>
            {mappedFields?.customer_gst || '—'}
          </p>
          <p>
            <span className="  text-outline-muted">Items: </span>
            {items.length}
          </p>
          {isLumpSum && lumpSumTotal && (
            <div className="mt-2 border border-dashed border-black/30 bg-surface-container p-2">
              <p className=" text-sm">
                Written total: ₹{Number(lumpSumTotal).toLocaleString('en-IN')}
              </p>
              <p className="mt-0.5    text-outline-muted">
                Lump-sum detected; line rates may be approximate.
              </p>
            </div>
          )}
        </div>

        {items.length > 0 && (
          <div className="mt-3 max-h-48 overflow-auto border border-outline-variant bg-surface-container p-2">
            <table className="w-full text-left text-xs font-light text-on-surface">
              <thead>
                <tr className="border-b border-black   ">
                  <th className="pb-1 pr-2 font-normal">#</th>
                  <th className="pb-1 pr-2 font-normal">Description</th>
                  <th className="pb-1 text-right font-normal">Qty</th>
                  {!isLumpSum && <th className="pb-1 text-right font-normal">Rate</th>}
                </tr>
              </thead>
              <tbody>
                {items.map((item, idx) => (
                  <tr key={idx} className="border-b border-outline-variant">
                    <td className="py-1 ">{idx + 1}</td>
                    <td className="py-1">{item.description}</td>
                    <td className="py-1 text-right ">
                      {item.quantity} {item.unit}
                    </td>
                    {!isLumpSum && (
                      <td className="py-1 text-right ">
                        ₹{Number(item.unit_price || 0).toLocaleString('en-IN')}
                      </td>
                    )}
                  </tr>
                ))}
                {isLumpSum && lumpSumTotal && (
                  <tr className="border-t-2 border-black font-normal">
                    <td colSpan={2} className="py-1.5  ">
                      Total (written)
                    </td>
                    <td className="py-1.5 text-right ">
                      ₹{Number(lumpSumTotal).toLocaleString('en-IN')}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {flags.length > 0 && (
          <div className="mt-3 border border-dashed border-black/30 bg-surface-container p-2    text-on-surface">
            Review: {flags.filter((f) => !f.startsWith('item_')).join(', ') || 'Some line items'}
          </div>
        )}

        {mappedFields?.notes && (
          <div className="mt-3 border border-outline-variant bg-surface-container p-2   leading-relaxed text-on-surface">
            <span className="text-outline-muted">Notes: </span>
            {mappedFields.notes}
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-2">
        <Button type="button" variant="outline" onClick={onRetake}>
          Retake
        </Button>
        <Button type="button" variant="ghost" onClick={onEdit}>
          Edit
        </Button>
        <Button type="button" onClick={onAccept}>
          Continue
        </Button>
      </div>
    </div>
  );
}
