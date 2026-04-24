import { useEffect, useRef, useState } from 'react';
import { Camera, Upload, X } from 'lucide-react';
import toast from 'react-hot-toast';
import Button from '../common/Button';
import CameraCapture from './CameraCapture';

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE = 10 * 1024 * 1024;
const MAX_UPLOAD_DIMENSION = 1200;
const JPEG_QUALITY = 0.82;

const pickBtn =
  'flex min-h-28 flex-col items-center justify-center border-2 border-dashed border-outline-variant bg-surface-white transition-colors duration-100 hover:border-black hover:bg-surface-container';

export default function ImageUpload({ onImageSelect, onExtract, isLoading = false }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [showCamera, setShowCamera] = useState(false);
  const galleryInputRef = useRef(null);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const setFile = (file, preview) => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      toast.error('Please select a JPEG, PNG, or WEBP image.');
      return;
    }
    if (file.size > MAX_SIZE) {
      toast.error('Image must be under 10MB.');
      return;
    }
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(file);
    setPreviewUrl(preview || URL.createObjectURL(file));
    onImageSelect?.(file);
  };

  const onPickGallery = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setFile(file);
  };

  const onCapture = ({ file, preview }) => {
    setShowCamera(false);
    setFile(file, preview);
  };

  const clearSelection = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl('');
    setSelectedFile(null);
    if (galleryInputRef.current) galleryInputRef.current.value = '';
  };

  const handleExtract = async () => {
    if (!selectedFile) {
      toast.error('Select an image first.');
      return;
    }
    const optimizedFile = await optimizeForOCR(selectedFile);
    const formData = new FormData();
    formData.append('file', optimizedFile);
    formData.append('preprocess', 'true');
    formData.append('mode', 'speed');
    await onExtract(formData);
  };

  return (
    <div className="space-y-4">
      {showCamera && <CameraCapture onCapture={onCapture} onClose={() => setShowCamera(false)} />}

      {!previewUrl ? (
        <div className="grid grid-cols-2 gap-3">
          <button type="button" onClick={() => setShowCamera(true)} className={pickBtn}>
            <Camera className="mb-2 h-8 w-8 text-outline-muted" strokeWidth={1.5} />
            <span className="   text-on-surface">Camera</span>
          </button>

          <button type="button" onClick={() => galleryInputRef.current?.click()} className={pickBtn}>
            <Upload className="mb-2 h-8 w-8 text-outline-muted" strokeWidth={1.5} />
            <span className="   text-on-surface">Upload</span>
          </button>

          <input
            ref={galleryInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={onPickGallery}
            className="hidden"
          />
        </div>
      ) : (
        <div className="space-y-3">
          <div className="relative overflow-hidden border border-black bg-surface-container">
            <img
              src={previewUrl}
              alt="Selected document"
              className="max-h-80 w-full object-contain"
              width="800"
              height="600"
            />
            <button
              type="button"
              onClick={clearSelection}
              className="absolute right-2 top-2 border border-white bg-black/70 p-1.5 text-white"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <Button type="button" fullWidth isLoading={isLoading} onClick={handleExtract}>
            Extract text
          </Button>
        </div>
      )}
    </div>
  );
}

async function optimizeForOCR(file) {
  try {
    const bitmap = await createImageBitmap(file);
    const scale = Math.min(1, MAX_UPLOAD_DIMENSION / Math.max(bitmap.width, bitmap.height));
    const width = Math.max(1, Math.round(bitmap.width * scale));
    const height = Math.max(1, Math.round(bitmap.height * scale));

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return file;
    ctx.drawImage(bitmap, 0, 0, width, height);

    const blob = await new Promise((resolve) => {
      canvas.toBlob(resolve, 'image/jpeg', JPEG_QUALITY);
    });

    if (!blob) return file;
    // Keep original if optimization did not reduce size materially.
    if (blob.size >= file.size * 0.95) return file;

    return new File([blob], `${file.name.replace(/\.[^.]+$/, '') || 'scan'}.jpg`, {
      type: 'image/jpeg',
      lastModified: Date.now(),
    });
  } catch {
    return file;
  }
}
