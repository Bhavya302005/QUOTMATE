import { useState, useCallback, useRef, useEffect } from 'react';
import toast from 'react-hot-toast';

export const useCamera = () => {
  const [hasPermission, setHasPermission] = useState(false);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const stopTracks = useCallback((mediaStream) => {
    if (!mediaStream) return;
    mediaStream.getTracks().forEach((track) => {
      try {
        track.stop();
      } catch {
        // ignore
      }
    });
  }, []);

  const stopStream = useCallback(() => {
    stopTracks(streamRef.current);
    streamRef.current = null;
    setStream(null);
    setIsStreaming(false);
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, [stopTracks]);

  const requestPermission = useCallback(async () => {
    if (!navigator?.mediaDevices?.getUserMedia) {
      setError('Camera API not supported in this browser');
      setHasPermission(false);
      setIsStreaming(false);
      toast.error('Camera is not supported in this browser.');
      return false;
    }

    const constraints = [
      { video: { facingMode: { ideal: 'environment' } } },
      { video: { facingMode: 'user' } },
      { video: true },
    ];

    try {
      let mediaStream = null;
      let lastError = null;
      for (const constraint of constraints) {
        try {
          mediaStream = await navigator.mediaDevices.getUserMedia(constraint);
          break;
        } catch (err) {
          lastError = err;
        }
      }

      if (!mediaStream) {
        throw lastError || new Error('Unable to initialize camera stream');
      }

      stopTracks(streamRef.current);
      streamRef.current = mediaStream;
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
  }, []);

  const captureImage = useCallback(() => {
    if (!videoRef.current || !isStreaming) return null;

    if (!videoRef.current.videoWidth || !videoRef.current.videoHeight) {
      return null;
    }

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
      videoRef.current.onloadedmetadata = () => {
        videoRef.current?.play().catch((e) => console.error('Video play failed:', e));
      };
    }
  }, [stream]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState !== 'visible') {
        stopStream();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [stopStream]);

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
