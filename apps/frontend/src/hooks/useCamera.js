import { useState, useCallback, useRef, useEffect } from 'react';
import toast from 'react-hot-toast';

export const useCamera = () => {
  const [hasPermission, setHasPermission] = useState(false);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const videoRef = useRef(null);

  const requestPermission = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' } }
      });
      setStream(mediaStream);
      setHasPermission(true);
      setError(null);
      setIsStreaming(true);
      return true;
    } catch (err) {
      console.error('Camera permission denied:', err);
      setError('Camera permission denied or not available');
      setHasPermission(false);
      setIsStreaming(false);
      toast.error('Could not access camera. Please check permissions.');
      return false;
    }
  };

  const stopStream = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setIsStreaming(false);
    }
  }, [stream]);

  const captureImage = useCallback(() => {
    if (!videoRef.current || !isStreaming) return null;

    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;

    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.drawImage(videoRef.current, 0, 0);

    // Convert to blob for upload and dataURL for preview
    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        const previewUrl = canvas.toDataURL('image/jpeg');
        resolve({ blob, previewUrl });
      }, 'image/jpeg', 0.95);
    });
  }, [isStreaming]);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
      videoRef.current.play().catch(e => console.error("Video play failed:", e));
    }
  }, [stream]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopStream();
    };
  }, [stopStream]);

  return {
    videoRef,
    hasPermission,
    isStreaming,
    error,
    requestPermission,
    stopStream,
    captureImage
  };
};
