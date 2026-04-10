import { useRef, useState, useEffect } from 'react';
import { workOrderAPI } from '../../services/api';
import Button from '../common/Button.jsx';
import toast from 'react-hot-toast';

export default function SignaturePad({ workOrderId, existingUrl, onChange }) {
  const canvasRef = useRef(null);
  const [drawing, setDrawing] = useState(false);
  const [isEmpty, setIsEmpty] = useState(true);
  const [saving, setSaving] = useState(false);
  const lastPos = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    canvas.width = canvas.offsetWidth * window.devicePixelRatio;
    canvas.height = canvas.offsetHeight * window.devicePixelRatio;
    const ctx = canvas.getContext('2d');
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
  }, []);

  const getPos = (e, canvas) => {
    const rect = canvas.getBoundingClientRect();
    const touch = e.touches ? e.touches[0] : e;
    return { x: touch.clientX - rect.left, y: touch.clientY - rect.top };
  };

  const startDraw = (e) => {
    e.preventDefault();
    setDrawing(true);
    setIsEmpty(false);
    lastPos.current = getPos(e, canvasRef.current);
  };

  const draw = (e) => {
    e.preventDefault();
    if (!drawing) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const pos = getPos(e, canvas);
    ctx.beginPath();
    ctx.moveTo(lastPos.current.x, lastPos.current.y);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    lastPos.current = pos;
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);
    setIsEmpty(true);
  };

  const saveSignature = async () => {
    if (isEmpty) {
      toast.error('Please sign first');
      return;
    }
    if (!workOrderId) {
      toast.error('Save the work order first');
      return;
    }
    setSaving(true);
    try {
      const canvas = canvasRef.current;
      const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
      const formData = new FormData();
      formData.append('file', blob, 'signature.png');
      const resp = await workOrderAPI.uploadSignature(workOrderId, formData);
      toast.success('Signature saved');
      onChange?.(resp.data.signature_url);
    } catch {
      toast.error('Failed to save signature');
    } finally {
      setSaving(false);
    }
  };

  const API_BASE = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000';

  return (
    <div className="space-y-3">
      <h3 className="stitch-label opacity-80">Customer signature</h3>
      {existingUrl ? (
        <div className="space-y-2">
          <div className="inline-block border border-black bg-surface-container p-3">
            <img src={`${API_BASE}${existingUrl}`} alt="Signature" className="h-16" width="150" height="64" />
          </div>
          <p className="   text-on-surface">Captured</p>
          <button
            type="button"
            className="   underline"
            onClick={() => onChange?.(null)}
          >
            Re-sign
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="overflow-hidden border border-black bg-surface-white" style={{ height: 120 }}>
            <canvas
              ref={canvasRef}
              className="h-full w-full touch-none"
              onMouseDown={startDraw}
              onMouseMove={draw}
              onMouseUp={() => setDrawing(false)}
              onMouseLeave={() => setDrawing(false)}
              onTouchStart={startDraw}
              onTouchMove={draw}
              onTouchEnd={() => setDrawing(false)}
            />
          </div>
          <p className="   text-outline-muted">Sign above</p>
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={clearCanvas}>
              Clear
            </Button>
            <Button size="sm" onClick={saveSignature} disabled={isEmpty || saving} isLoading={saving}>
              Save
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
