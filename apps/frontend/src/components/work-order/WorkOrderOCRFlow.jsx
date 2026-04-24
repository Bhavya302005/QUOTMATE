import { useState } from 'react';
import { ArrowLeft, ScanLine } from 'lucide-react';
import toast from 'react-hot-toast';
import { ocrAPI, workOrderAPI, getApiErrorMessage } from '../../services/api';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import ImageUpload from '../ocr/ImageUpload';
import WorkOrderForm from './WorkOrderForm';

// step: 'upload' → 'review' → 'form'
export default function WorkOrderOCRFlow({ onSuccess, onCancel }) {
  const [step, setStep] = useState('upload');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [ocrText, setOcrText] = useState('');
  const [ocrConfidence, setOcrConfidence] = useState(0);
  const [mappedData, setMappedData] = useState(null);

  const handleExtract = async (formData) => {
    setIsLoading(true);
    setLoadingMessage('Scanning work order image...');
    try {
      // Step 1 — extract raw text from image
      const ocrResp = await ocrAPI.upload(formData);
      const extractedText = ocrResp.data?.ocr_result?.text || '';
      const confidence = ocrResp.data?.ocr_result?.confidence || 0;

      if (!extractedText.trim()) {
        toast.error('No text was extracted from the image.');
        return;
      }

      setLoadingMessage('Structuring work order data...');
      // Step 2 — map text to work order fields via AI
      const mapResp = await workOrderAPI.fromOCR({ ocr_text: extractedText });

      setOcrText(extractedText);
      setOcrConfidence(confidence);
      setMappedData(mapResp.data);
      setStep('review');
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to process image'));
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const stepLabel = {
    upload: 'Scan Work Order / Job Card',
    review: 'Review Extracted Data',
    form: 'Create Work Order',
  }[step];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex items-center gap-2">
          <ScanLine className="h-4 w-4 text-on-surface" strokeWidth={1.5} />
          <h2 className="text-base font-light tracking-tight text-on-surface">{stepLabel}</h2>
        </div>
      </div>

      {/* Upload step */}
      {step === 'upload' && (
        <ImageUpload onExtract={handleExtract} isLoading={isLoading} />
      )}

      {/* Review step */}
      {step === 'review' && mappedData && (
        <ReviewStep
          ocrText={ocrText}
          ocrConfidence={ocrConfidence}
          mappedData={mappedData}
          onRetake={() => setStep('upload')}
          onProceed={() => setStep('form')}
        />
      )}

      {/* Form step — pre-filled with OCR data */}
      {step === 'form' && (
        <WorkOrderForm
          ocrData={mappedData}
          onSaved={onSuccess}
          onCancel={onCancel}
        />
      )}

      {/* Full-screen loading overlay */}
      {isLoading && (
        <div className="fixed inset-0 z-50 md:left-64 flex flex-col items-center justify-center bg-surface">
          <LoadingSpinner size="lg" />
          <p className="mt-3    text-outline-muted">
            {loadingMessage || 'Processing…'}
          </p>
        </div>
      )}
    </div>
  );
}

// ─── Review sub-component ──────────────────────────────────────────────────────

function ReviewStep({ ocrText, ocrConfidence, mappedData, onRetake, onProceed }) {
  const suggested = mappedData?.suggested_work_order;
  const flags = mappedData?.confidence_flags || [];
  const aiConfidence = mappedData?.ai_confidence;
  const materials = suggested?.materials || [];

  const Field = ({ label, value, flagged }) => (
    <div
      className={`border px-3 py-2 ${
        flagged ? 'border-dashed border-black bg-surface-container' : 'border-outline-variant bg-surface-white'
      }`}
    >
      <p className="stitch-label opacity-70">
        {label}
        {flagged && ' · review'}
      </p>
      <p className="mt-0.5 text-sm font-light text-on-surface">
        {value || <span className="text-outline-muted italic">Not detected</span>}
      </p>
    </div>
  );

  return (
    <div className="space-y-4">
      {/* Confidence badge */}
      <div className="flex flex-wrap items-center gap-2    text-on-surface">
        <span className="text-outline-muted">OCR</span>
        <span className="border border-black px-2 py-0.5">{Math.round(ocrConfidence)}%</span>
        {aiConfidence && (
          <span className="border border-black px-2 py-0.5">AI · {aiConfidence}</span>
        )}
      </div>

      {/* Extracted fields */}
      {suggested ? (
        <div className="space-y-3">
          <p className="stitch-label opacity-80">Extracted fields</p>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <Field label="Client Name"     value={suggested.client_name}       flagged={flags.includes('client_name')} />
            <Field label="Phone"           value={suggested.client_phone} />
            <Field label="Email"           value={suggested.client_email} />
            <Field label="Assigned To"     value={suggested.assigned_to} />
          </div>
          <Field label="Service Location"  value={suggested.service_location} />
          <Field label="Work Description"  value={suggested.work_description} />
          {suggested.remarks && <Field label="Remarks" value={suggested.remarks} />}

          {/* Materials preview */}
          {materials.length > 0 && (
            <div>
              <p className="mb-2 stitch-label opacity-80">Materials ({materials.length})</p>
              <div className="overflow-x-auto border border-black">
                <table className="min-w-full text-left text-xs font-light">
                  <thead className="border-b border-black bg-surface-container   ">
                    <tr>
                      <th className="px-3 py-2 font-normal text-on-surface">Material</th>
                      <th className="px-3 py-2 text-right font-normal text-on-surface">Qty</th>
                      <th className="px-3 py-2 font-normal text-on-surface">Unit</th>
                      <th className="px-3 py-2 text-right font-normal text-on-surface">Unit cost</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant">
                    {materials.map((m, i) => (
                      <tr key={i}>
                        <td className="px-3 py-1.5 text-on-surface">{m.material_name}</td>
                        <td className="px-3 py-1.5 text-right  text-on-surface">{m.quantity ?? '—'}</td>
                        <td className="px-3 py-1.5  text-outline-muted">{m.unit || '—'}</td>
                        <td className="px-3 py-1.5 text-right  text-on-surface">
                          {m.unit_cost != null ? `₹${m.unit_cost}` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="border border-dashed border-black/40 bg-surface-container p-3   leading-relaxed  text-on-surface">
          Could not auto-extract fields — continue manually in the form.
        </div>
      )}

      {/* Raw OCR text */}
      <details className="group">
        <summary className="cursor-pointer select-none    text-on-surface hover:underline">
          Raw OCR text
        </summary>
        <pre className="stitch-input mt-2 max-h-40 overflow-y-auto whitespace-pre-wrap  text-on-surface">
          {ocrText}
        </pre>
      </details>

      {/* Actions */}
      <div className="flex gap-2 pt-1">
        <Button variant="outline" size="sm" onClick={onRetake} className="flex-1">
          ↺ Retake
        </Button>
        <Button size="sm" onClick={onProceed} className="flex-1">
          {suggested ? 'Continue to Form →' : 'Fill Manually →'}
        </Button>
      </div>
    </div>
  );
}
