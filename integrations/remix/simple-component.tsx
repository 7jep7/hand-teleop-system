import React, { useState, useRef, useCallback, useEffect } from 'react';

interface HandTrackingResult {
  success: boolean;
  message: string;
  hand_detected: boolean;
  overlay_image?: string;
  processing_time_ms?: number;
}

export default function WiLoRHandTracking() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<HandTrackingResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 } }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraActive(true);
        setError(null);
      }
    } catch (err) {
      setError('Could not access camera. Please check permissions.');
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  }, []);

  const captureAndProcess = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || isProcessing) return;

    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      if (!context) throw new Error('Could not get canvas context');

      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      context.drawImage(videoRef.current, 0, 0);

      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);

      const isLocalDev = window.location.hostname === 'localhost';
      const apiEndpoint = isLocalDev
        ? 'http://localhost:8000/api/track'
        : 'https://hand-teleop-api.onrender.com/api/track';
        
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_data: imageDataUrl,
          robot_type: 'so101',
          tracking_mode: 'wilor'
        }),
      });

      const data: HandTrackingResult = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Processing failed');
      }

      setResult(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  }, [isProcessing]);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">WiLoR Hand Tracking</h2>
        <p className="text-gray-600">Real-time hand pose estimation</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Camera</h3>

          <div className="bg-gray-900 rounded-lg overflow-hidden mb-4">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-64 object-cover"
              style={{ display: cameraActive ? 'block' : 'none' }}
            />
            {!cameraActive && (
              <div className="w-full h-64 flex items-center justify-center text-gray-400">
                Camera not active
              </div>
            )}
            <canvas ref={canvasRef} className="hidden" />
          </div>

          <div className="space-y-3">
            {!cameraActive ? (
              <button
                onClick={startCamera}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg"
              >
                Start Camera
              </button>
            ) : (
              <div className="space-y-2">
                <button
                  onClick={captureAndProcess}
                  disabled={isProcessing}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg"
                >
                  {isProcessing ? 'Processing...' : 'Capture & Process'}
                </button>
                <button
                  onClick={stopCamera}
                  className="w-full bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-6 rounded-lg"
                >
                  Stop Camera
                </button>
              </div>
            )}
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Results</h3>

          {isProcessing && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-blue-600">Processing with WiLoR...</p>
            </div>
          )}

          {result && !isProcessing && (
            <div className="space-y-4">
              {result.hand_detected && result.overlay_image ? (
                <div>
                  <img
                    src={result.overlay_image}
                    alt="Hand tracking result"
                    className="w-full rounded-lg"
                  />
                  <div className="bg-gray-50 rounded-lg p-4 mt-4">
                    <p className="text-green-600 font-semibold">Hand detected successfully!</p>
                    {result.processing_time_ms && (
                      <p className="text-sm text-gray-600">Processing time: {result.processing_time_ms}ms</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-red-600">{result.message}</p>
                </div>
              )}
            </div>
          )}

          {!result && !isProcessing && (
            <div className="text-center py-8">
              <p className="text-gray-600">Capture an image to see results</p>
              <div className="bg-blue-50 rounded-lg p-4 mt-4">
                <p className="text-blue-800 font-semibold">Instructions:</p>
                <ul className="text-blue-700 text-sm mt-2 space-y-1">
                  <li>• Position your RIGHT hand in camera view</li>
                  <li>• Click "Capture & Process" button</li>
                  <li>• Wait for processing to complete</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
