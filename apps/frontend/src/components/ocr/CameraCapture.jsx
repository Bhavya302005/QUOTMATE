import { useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { useCamera } from '../../hooks/useCamera';

export default function CameraCapture({ onCapture, onClose }) {
  const location = useLocation();
  const lastPathRef = useRef(location.pathname);
  const { captureImage, hasPermission, isStreaming, error, requestPermission, stopStream, videoRef } = useCamera();

  useEffect(() => {
    requestPermission();
    return () => {
      stopStream();
    };
  }, []);

  // Safety: if user navigates to another menu while modal is open, stop camera.
  useEffect(() => {
    if (lastPathRef.current === location.pathname) return;
    lastPathRef.current = location.pathname;
    stopStream();
    onClose?.();
  }, [location.pathname]);

  const handleCapture = async () => {
    const shot = await captureImage();
    if (!shot?.blob) return;

    const file = new File([shot.blob], `capture-${Date.now()}.jpg`, { type: 'image/jpeg' });
    const preview = URL.createObjectURL(shot.blob);
    onCapture({ file, preview });
    stopStream();
  };

  return (
    <div className="fixed inset-0 z-50 md:left-64 flex flex-col bg-black text-white">
      <div className="flex items-center justify-between border-b border-white/20 px-4 py-3">
        <h2 className="font-mono uppercase tracking-widest">Camera</h2>
        <button
          type="button"
          onClick={() => {
            stopStream();
            onClose();
          }}
          className="border border-white/30 p-2 transition-colors hover:bg-white hover:text-black"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="flex-1 bg-surface-container relative">
        <video ref={videoRef} autoPlay playsInline muted className="absolute inset-0 h-full w-full object-cover" />
      </div>

      <div className="border-t border-white/20 bg-black px-6 pt-6 pb-28 md:pb-6 text-center">
        {!hasPermission && (
          <p className="mb-3 font-mono text-sm text-error">{error || 'Camera permission required'}</p>
        )}
        <button
          type="button"
          onClick={handleCapture}
          disabled={!isStreaming}
          className="mx-auto flex h-14 w-full max-w-xs items-center justify-center border-2 border-white bg-white/10 font-mono text-lg uppercase tracking-widest text-white transition-colors hover:bg-white hover:text-black disabled:cursor-not-allowed disabled:opacity-40"
        >
          Capture Frame
        </button>
      </div>
    </div>
  );
}
