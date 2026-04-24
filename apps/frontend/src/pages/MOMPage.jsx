import { useCallback, useEffect, useState } from 'react';
import { Routes, Route, useNavigate, useParams, useLocation } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';
import { momAPI, getApiErrorMessage } from '../services/api';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import MOMList from '../components/mom/MOMList';
import MOMForm from '../components/mom/MOMForm';
import MOMPreview from '../components/mom/MOMPreview';
import OCRFlowWithMOM from '../components/mom/OCRFlowWithMOM';
import { loadDraft } from '../utils/draftStorage';

export default function MOMPage() {
  return (
    <Routes>
      <Route index element={<MOMList />} />
      <Route path="new" element={<CreateMOM />} />
      <Route path="scan" element={<ScanMOM />} />
      <Route path=":id" element={<MOMDetail />} />
      <Route path=":id/edit" element={<EditMOM />} />
    </Routes>
  );
}

function CreateMOM() {
  const navigate = useNavigate();
  const location = useLocation();
  const [mode, setMode] = useState(null);
  const resumeDraft = Boolean(location.state?.resumeDraft);

  useEffect(() => {
    if (!location.state?.resumeDraft) return;
    const d = loadDraft('mom', 'new');
    setMode(d?.defaultMode === 'ai' ? 'ai' : 'manual');
  }, [location.state]);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button type="button" variant="ghost" size="sm" onClick={() => navigate('/moms')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-lg font-light tracking-tight text-on-surface">Create MOM</h1>
      </div>

      {!mode ? (
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <Button type="button" variant="outline" onClick={() => navigate('/moms/scan')}>
            Scan Handwritten Notes
          </Button>
          <Button type="button" onClick={() => setMode('manual')}>
            Manual Entry
          </Button>
        </div>
      ) : (
        <MOMForm
          defaultMode={mode}
          resumeDraft={resumeDraft}
          onSuccess={(mom) => {
            navigate(`/moms/${mom.id}`);
          }}
        />
      )}
    </div>
  );
}

function ScanMOM() {
  const navigate = useNavigate();

  return (
    <OCRFlowWithMOM
      onCancel={() => navigate('/moms')}
      onSuccess={(mom) => navigate(`/moms/${mom.id}`)}
    />
  );
}

function MOMDetail() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [mom, setMom] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFinalizing, setIsFinalizing] = useState(false);
  const [isReverting, setIsReverting] = useState(false);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await momAPI.get(id);
      setMom(response.data);
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to load MOM'));
      navigate('/moms');
    } finally {
      setIsLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => {
    load();
  }, [load]);

  const handleDownload = async () => {
    try {
      const response = await momAPI.download(id);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${mom?.mom_number || id}.pdf`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Download failed'));
    }
  };

  const handleFinalize = async () => {
    setIsFinalizing(true);
    try {
      await momAPI.finalize(id);
      toast.success('MOM finalized');
      await load();
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Finalize failed'));
    } finally {
      setIsFinalizing(false);
    }
  };

  const handleRevertFinalization = async () => {
    setIsReverting(true);
    try {
      await momAPI.revertFinalize(id);
      toast.success('MOM moved back to review');
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
        <Button type="button" variant="ghost" size="sm" onClick={() => navigate('/moms')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-lg font-light tracking-tight text-on-surface">MOM details</h1>
      </div>

      <MOMPreview
        mom={mom}
        onDownload={handleDownload}
        onFinalize={handleFinalize}
        onRevertFinalization={handleRevertFinalization}
        isFinalizing={isFinalizing}
        isReverting={isReverting}
      />
    </div>
  );
}

function EditMOM() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [mom, setMom] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await momAPI.get(id);
        setMom(response.data);
      } catch (error) {
        toast.error(getApiErrorMessage(error, 'Failed to load MOM'));
        navigate('/moms');
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
        <Button type="button" variant="ghost" size="sm" onClick={() => navigate(`/moms/${id}`)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-lg font-light tracking-tight text-on-surface">Edit MOM</h1>
      </div>

      <MOMForm
        initialData={mom}
        onSuccess={(saved) => navigate(`/moms/${saved.id}`)}
      />
    </div>
  );
}
