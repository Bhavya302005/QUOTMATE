import { useCallback, useEffect, useState } from 'react';
import { Routes, Route, useNavigate, useParams, useLocation } from 'react-router-dom';
import toast from 'react-hot-toast';
import { ArrowLeft, Trash2 } from 'lucide-react';
import { quotationAPI, getApiErrorMessage } from '../services/api';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import QuotationList from '../components/quotation/QuotationList';
import QuotationForm from '../components/quotation/QuotationForm';
import QuotationPreview from '../components/quotation/QuotationPreview';
import OCRFlowWithPreview from '../components/quotation/OCRFlowWithPreview';

export default function QuotationPage() {
  return (
    <Routes>
      <Route index element={<QuotationList />} />
      <Route path="new" element={<CreateQuotation />} />
      <Route path="scan" element={<ScanQuotation />} />
      <Route path=":id" element={<QuotationDetail />} />
      <Route path=":id/edit" element={<EditQuotation />} />
    </Routes>
  );
}

function CreateQuotation() {
  const navigate = useNavigate();
  const location = useLocation();
  const [mode, setMode] = useState(null);
  const resumeDraft = Boolean(location.state?.resumeDraft);

  useEffect(() => {
    if (location.state?.openManual) setMode('manual');
  }, [location.state]);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button type="button" variant="ghost" size="sm" onClick={() => navigate('/quotations')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-lg font-light tracking-tight text-on-surface">Create quotation</h1>
      </div>

      {!mode ? (
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <Button type="button" variant="outline" onClick={() => navigate('/quotations/scan')}>
            Scan Handwritten Notes
          </Button>
          <Button type="button" onClick={() => setMode('manual')}>
            Manual Entry
          </Button>
        </div>
      ) : (
        <QuotationForm
          resumeDraft={resumeDraft}
          onSuccess={(quotation) => {
            navigate(`/quotations/${quotation.id}`);
          }}
        />
      )}
    </div>
  );
}

function ScanQuotation() {
  const navigate = useNavigate();

  return (
    <OCRFlowWithPreview
      onCancel={() => navigate('/quotations')}
      onSuccess={(quotation) => navigate(`/quotations/${quotation.id}`)}
    />
  );
}

function EditQuotation() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [quotation, setQuotation] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await quotationAPI.get(id);
        setQuotation(response.data);
      } catch (error) {
        toast.error(getApiErrorMessage(error, 'Failed to load quotation'));
        navigate('/quotations');
      } finally {
        setIsLoading(false);
      }
    };

    load();
  }, [id, navigate]);

  if (isLoading) {
    return (
      <div className="flex min-h-48 items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button type="button" variant="ghost" size="sm" onClick={() => navigate(`/quotations/${id}`)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-lg font-light tracking-tight text-on-surface">Edit quotation</h1>
      </div>

      <QuotationForm
        initialData={quotation}
        onSuccess={(saved) => navigate(`/quotations/${saved.id}`)}
      />
    </div>
  );
}

function QuotationDetail() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [quotation, setQuotation] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFinalizing, setIsFinalizing] = useState(false);
  const [isReverting, setIsReverting] = useState(false);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await quotationAPI.get(id);
      setQuotation(response.data);
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to load quotation'));
      navigate('/quotations');
    } finally {
      setIsLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => {
    load();
  }, [load]);

  const handleDownload = async () => {
    try {
      const response = await quotationAPI.download(id);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${quotation?.quotation_number || id}.pdf`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Download failed'));
    }
  };

  const handleFinalize = async () => {
    setIsFinalizing(true);
    try {
      await quotationAPI.finalize(id);
      toast.success('Quotation finalized');
      await load();
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Finalize failed'));
    } finally {
      setIsFinalizing(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this quotation? This cannot be undone.')) return;
    try {
      await quotationAPI.delete(id);
      toast.success('Quotation deleted');
      navigate('/quotations');
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Delete failed'));
    }
  };

  const handleRevertFinalization = async () => {
    setIsReverting(true);
    try {
      await quotationAPI.revertFinalize(id);
      toast.success('Quotation moved back to review');
      await load();
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Revert failed'));
    } finally {
      setIsReverting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-48 items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button type="button" variant="ghost" size="sm" onClick={() => navigate('/quotations')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-lg font-light tracking-tight text-on-surface">Quotation details</h1>
        <Button type="button" variant="outline" size="sm" onClick={handleDelete} className="ml-auto">
          <Trash2 className="mr-2 h-4 w-4" strokeWidth={2} /> Delete
        </Button>
      </div>

      <QuotationPreview
        quotation={quotation}
        onDownload={handleDownload}
        onFinalize={handleFinalize}
        onRevertFinalization={handleRevertFinalization}
        isFinalizing={isFinalizing}
        isReverting={isReverting}
      />
    </div>
  );
}
