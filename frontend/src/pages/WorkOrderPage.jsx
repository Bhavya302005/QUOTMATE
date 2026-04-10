import { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import Card from '../components/common/Card.jsx';
import Button from '../components/common/Button.jsx';
import WorkOrderList from '../components/work-order/WorkOrderList.jsx';
import WorkOrderForm from '../components/work-order/WorkOrderForm.jsx';
import WorkOrderPreview from '../components/work-order/WorkOrderPreview.jsx';
import WorkOrderOCRFlow from '../components/work-order/WorkOrderOCRFlow.jsx';
import { workOrderAPI, getApiErrorMessage } from '../services/api';
import toast from 'react-hot-toast';

export default function WorkOrderPage() {
  const [view, setView] = useState('list');
  const [selectedId, setSelectedId] = useState(null);
  const [selectedWO, setSelectedWO] = useState(null);
  const [resumeNewDraft, setResumeNewDraft] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const refresh = () => setRefreshTrigger((t) => t + 1);

  const handleSelect = async (id) => {
    try {
      const resp = await workOrderAPI.get(id);
      setSelectedWO(resp.data);
      setSelectedId(id);
      setView('preview');
    } catch {
      toast.error('Failed to load work order');
    }
  };

  const handleSaved = (wo) => {
    refresh();
    if (wo) {
      setSelectedWO(wo);
      setSelectedId(wo.id);
      setView('preview');
    } else {
      setView('list');
    }
  };

  const handleDownload = async () => {
    if (!selectedId) return;
    try {
      const response = await workOrderAPI.download(selectedId);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${selectedWO?.work_order_number || selectedId}.pdf`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Download failed'));
    }
  };

  const handleRevertFinalization = async () => {
    if (!selectedId) return;
    try {
      await workOrderAPI.revertFinalize(selectedId);
      toast.success('Work order moved back to review');
      const refreshed = await workOrderAPI.get(selectedId);
      setSelectedWO(refreshed.data);
      refresh();
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Revert failed'));
    }
  };

  return (
    <div className="space-y-6 pb-20">
      {view === 'list' && (
        <WorkOrderList
          onSelect={handleSelect}
          onNew={() => {
            setSelectedId(null);
            setSelectedWO(null);
            setResumeNewDraft(false);
            setView('create');
          }}
          refreshTrigger={refreshTrigger}
          onResumeDraft={() => {
            setSelectedId(null);
            setSelectedWO(null);
            setResumeNewDraft(true);
            setView('new');
          }}
          onResumeEditDraft={async (id) => {
            try {
              const resp = await workOrderAPI.get(id);
              setSelectedWO(resp.data);
              setSelectedId(id);
              setResumeNewDraft(false);
              setView('edit');
            } catch {
              toast.error('Failed to load work order');
            }
          }}
        />
      )}

      {view === 'create' && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setView('list')}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <h1 className="text-lg font-light tracking-tight text-on-surface">Create work order</h1>
          </div>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <Button
              type="button"
              variant="outline"
              fullWidth
              onClick={() => {
                setSelectedId(null);
                setSelectedWO(null);
                setResumeNewDraft(false);
                setView('ocr');
              }}
            >
              Scan job card
            </Button>
            <Button
              type="button"
              fullWidth
              onClick={() => {
                setSelectedId(null);
                setSelectedWO(null);
                setResumeNewDraft(false);
                setView('new');
              }}
            >
              Manual entry
            </Button>
          </div>
        </div>
      )}

      {view !== 'list' && view !== 'create' && (
        <div className="flex items-start justify-between gap-4 border-b border-black pb-4">
          <div>
            <h1 className="text-2xl font-light  tracking-tighter text-on-surface md:text-3xl">Work orders</h1>
            <p className="mt-1    text-outline-muted">
              Service orders, costs &amp; photos
            </p>
          </div>
          <button
            type="button"
            onClick={() => setView('list')}
            className="shrink-0    underline decoration-black underline-offset-4 hover:bg-black hover:text-white hover:no-underline"
          >
            Back to list
          </button>
        </div>
      )}

      {(view === 'new' || view === 'edit') && (
        <Card>
          <h2 className="mb-4 text-base font-normal  tracking-tight text-on-surface">
            {view === 'new' ? 'New work order' : 'Edit work order'}
          </h2>
          <WorkOrderForm
            workOrderId={view === 'edit' ? selectedId : null}
            resumeDraft={view === 'new' ? resumeNewDraft : false}
            onSaved={handleSaved}
            onCancel={() => setView('list')}
          />
        </Card>
      )}

      {view === 'ocr' && (
        <Card>
          <WorkOrderOCRFlow onSuccess={handleSaved} onCancel={() => setView('create')} />
        </Card>
      )}

      {view === 'preview' && selectedWO && (
        <div className="space-y-3">
          <Card>
            <WorkOrderPreview workOrder={selectedWO} />
          </Card>
          <div className="flex flex-col gap-2 sm:flex-row">
            <button
              type="button"
              onClick={handleDownload}
              className="flex-1 border border-black bg-black py-2.5 text-center    text-white transition-colors duration-100 hover:bg-white hover:text-black"
            >
              Download PDF
            </button>
            {selectedWO?.status === 'completed' && (
              <button
                type="button"
                onClick={handleRevertFinalization}
                className="flex-1 border border-black bg-white py-2.5 text-center    text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
              >
                Revert finalization
              </button>
            )}
            <button
              type="button"
              onClick={() => setView('edit')}
              className="flex-1 border border-black bg-white py-2.5 text-center    text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
            >
              Edit
            </button>
            <button
              type="button"
              onClick={() => setView('list')}
              className="flex-1 border border-black bg-white py-2.5 text-center    text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
            >
              List
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
