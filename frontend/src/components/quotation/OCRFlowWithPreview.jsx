import { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';
import { ocrAPI, quotationAPI, getApiErrorMessage } from '../../services/api';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import ImageUpload from '../ocr/ImageUpload';
import OCRResult from '../ocr/OCRResult';
import QuotationForm from './QuotationForm';

export default function OCRFlowWithPreview({ onSuccess, onCancel }) {
  const [step, setStep] = useState('upload');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [ocrText, setOcrText] = useState('');
  const [ocrConfidence, setOcrConfidence] = useState(0);
  const [mappedData, setMappedData] = useState(null);

  const handleExtract = async (formData) => {
    setIsLoading(true);
    setLoadingMessage('Scanning handwriting...');

    try {
      const ocrResponse = await ocrAPI.upload(formData);
      const extractedText = ocrResponse.data?.ocr_result?.text || '';
      const confidence = ocrResponse.data?.ocr_result?.confidence || 0;

      if (!extractedText.trim()) {
        toast.error('No text was extracted from the image.');
        return;
      }

      setLoadingMessage('Structuring quotation data...');
      const mapResponse = await quotationAPI.fromOCR({
        ocr_text: extractedText,
      });

      setOcrText(extractedText);
      setOcrConfidence(confidence);
      setMappedData(mapResponse.data);
      setStep('review');
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to process image'));
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h2 className="text-base font-light tracking-tight text-on-surface">
          {step === 'upload' ? 'Scan handwritten notes' : step === 'review' ? 'Review OCR' : 'Create quotation'}
        </h2>
      </div>

      {step === 'upload' && (
        <ImageUpload onExtract={handleExtract} isLoading={isLoading} />
      )}

      {step === 'review' && (
        <OCRResult
          text={ocrText}
          confidence={ocrConfidence}
          mappedFields={mappedData}
          onRetake={() => setStep('upload')}
          onEdit={() => setStep('form')}
          onAccept={() => setStep('form')}
        />
      )}

      {step === 'form' && (
        <QuotationForm
          ocrData={{
            ...mappedData,
            document_id: mappedData?.document_id,
          }}
          onSuccess={onSuccess}
        />
      )}

      {isLoading && (
        <div className="fixed inset-0 z-50 md:left-64 flex flex-col items-center justify-center bg-surface">
          <LoadingSpinner size="lg" />
          <p className="mt-3    text-outline-muted">{loadingMessage || 'Processing…'}</p>
        </div>
      )}
    </div>
  );
}
