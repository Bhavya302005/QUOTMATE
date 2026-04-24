import { useEffect } from 'react';
import { X } from 'lucide-react';
import { useCamera } from '../../hooks/useCamera';

export default function CameraCapture({ onCapture, onClose }) {
  const { videoRef, hasPermission, isStreaming, error, requestPermission, stopStream } = useCamera();

  useEffect(() => {
    requestPermission();
    return () => stopStream();
  }, [requestPermission, stopStream]);

  const handleCapture = async () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(videoRef.current, 0, 0);
    canvas.toBlob(
      (blob) => {
        if (!blob) return;
        const file = new File([blob], `capture-${Date.now()}.jpg`, { type: 'image/jpeg' });
        const preview = URL.createObjectURL(blob);
        onCapture({ file, preview });
        stopStream();
      },
      'image/jpeg',
      0.9
    );
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

      <div className="border-t border-white/20 bg-black px-6 py-6 text-center">
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
