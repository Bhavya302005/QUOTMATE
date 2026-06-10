import { useCallback, useEffect, useState } from 'react';
import { Routes, Route, useNavigate, useParams, useLocation } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
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
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const queryClient = useQueryClient();

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
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      await load();
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Finalize failed'));
    } finally {
      setIsFinalizing(false);
    }
  };

  const confirmDelete = () => {
    setShowDeleteModal(true);
  };

  const handleDelete = async (deductRevenue = true) => {
    setIsDeleting(true);
    try {
      await quotationAPI.delete(id, deductRevenue);
      toast.success('Quotation deleted');
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      navigate('/quotations');
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Delete failed'));
    } finally {
      setIsDeleting(false);
      setShowDeleteModal(false);
    }
  };

  const handleRevertFinalization = async () => {
    setIsReverting(true);
    try {
      await quotationAPI.revertFinalize(id);
      toast.success('Quotation moved back to review');
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
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
        <Button type="button" variant="outline" size="sm" onClick={confirmDelete} className="ml-auto">
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

      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-md border border-black bg-surface-white p-6">
            <h2 className="mb-4 text-xl font-light tracking-tight text-on-surface">Delete Quotation</h2>
            <p className="mb-6 text-sm text-outline-muted">
              Are you sure you want to delete this quotation? This cannot be undone.
            </p>
            {quotation.status === 'finalized' && (
              <p className="mb-6 text-sm text-on-surface border-l-2 border-black pl-3 bg-surface-container py-2">
                This is a finalized quotation. Do you want to deduct its amount from your monthly revenue?
              </p>
            )}
            <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="border border-black bg-white px-4 py-2 text-sm transition-colors hover:bg-surface-container"
              >
                Cancel
              </button>
              {quotation.status === 'finalized' ? (
                <>
                  <button
                    type="button"
                    onClick={() => handleDelete(false)}
                    disabled={isDeleting}
                    className="border border-black bg-black px-4 py-2 text-sm text-white transition-colors hover:opacity-80 disabled:opacity-50"
                  >
                    Delete & Keep Revenue
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(true)}
                    disabled={isDeleting}
                    className="border border-error bg-error px-4 py-2 text-sm text-white transition-colors hover:opacity-80 disabled:opacity-50"
                  >
                    Delete & Deduct
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  onClick={() => handleDelete(true)}
                  disabled={isDeleting}
                  className="border border-error bg-error px-4 py-2 text-sm text-white transition-colors hover:opacity-80 disabled:opacity-50"
                >
                  Delete Quotation
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
