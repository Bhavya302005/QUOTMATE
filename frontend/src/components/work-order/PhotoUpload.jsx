import { useRef, useState } from 'react';
import { workOrderAPI } from '../../services/api';
import toast from 'react-hot-toast';

const API_BASE = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000';

export default function PhotoUpload({ workOrderId, beforeUrl, afterUrl, onChange }) {
  const [uploading, setUploading] = useState(null);
  const beforeRef = useRef();
  const afterRef = useRef();

  const handleUpload = async (photoType, file) => {
    if (!workOrderId) {
      toast.error('Save the work order first before uploading photos.');
      return;
    }
    setUploading(photoType);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const resp = await workOrderAPI.uploadPhoto(workOrderId, photoType, formData);
      toast.success(`${photoType === 'before' ? 'Before' : 'After'} photo uploaded`);
      onChange?.(photoType, resp.data.photo_url);
    } catch {
      toast.error('Upload failed');
    } finally {
      setUploading(null);
    }
  };

  const PhotoBox = ({ label, url, photoType, inputRef }) => (
    <div className="flex flex-col gap-2">
      <p className="stitch-label opacity-80">{label}</p>
      <div
        className="relative flex min-h-[140px] cursor-pointer items-center justify-center overflow-hidden border-2 border-dashed border-outline-variant bg-surface-container transition-colors hover:border-black"
        onClick={() => inputRef.current.click()}
      >
        {url ? (
          <img
            src={`${API_BASE}${url}`}
            alt={label}
            className="w-full object-cover"
            width="400"
            height="180"
            style={{ maxHeight: 180 }}
          />
        ) : (
          <div className="p-4 text-center">
            <p className="   text-outline-muted">
              Tap to upload {label.toLowerCase()}
            </p>
          </div>
        )}
        {uploading === photoType && (
          <div className="absolute inset-0 flex items-center justify-center bg-surface-white/80">
            <span className="animate-pulse    text-on-surface">
              Uploading…
            </span>
          </div>
        )}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => e.target.files[0] && handleUpload(photoType, e.target.files[0])}
      />
    </div>
  );

  return (
    <div className="space-y-3">
      <h3 className="stitch-label opacity-80">Before / after photos</h3>
      <div className="grid grid-cols-2 gap-4">
        <PhotoBox label="Before" url={beforeUrl} photoType="before" inputRef={beforeRef} />
        <PhotoBox label="After" url={afterUrl} photoType="after" inputRef={afterRef} />
      </div>
    </div>
  );
}
