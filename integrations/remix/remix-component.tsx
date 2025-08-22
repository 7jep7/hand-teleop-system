// WiLoR Hand Tracking Component for Remix + Tailwind
// Drop this into your Remix app/components/ directory

import { useState, useRef, useCallback } from 'react';

interface HandTrackingResult {
  success: boolean;
  message: string;
  hand_detected: boolean;
  overlay_image?: string;
  hand_data?: {
    bbox?: number[];
    keypoints_2d?: number[][];
  };
  keypoint_count?: number;
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
      console.error('Camera error:', err);
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
      // Capture frame from video
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      if (!context) throw new Error('Could not get canvas context');

      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      context.drawImage(videoRef.current, 0, 0);

      // Convert to blob
      const blob = await new Promise<Blob>((resolve) => {
        canvas.toBlob((blob) => resolve(blob!), 'image/jpeg', 0.8);
      });

      // Send to API
      const formData = new FormData();
      formData.append('file', blob, 'capture.jpg');

      const response = await fetch('http://localhost:8000/api/track', {
        method: 'POST',
        body: formData,
      });

      const data: HandTrackingResult = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Processing failed');
      }

      setResult(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('Processing error:', err);
    } finally {
      setIsProcessing(false);
    }
  }, [isProcessing]);

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          WiLoR Hand Tracking
        </h2>
        <p className="text-gray-600">
          Real-time hand pose estimation with your camera
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Camera Section */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Camera Feed
          </h3>

          {/* Video Display */}
          <div className="relative bg-gray-900 rounded-lg overflow-hidden mb-4">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-64 object-cover"
              style={{ display: cameraActive ? 'block' : 'none' }}
            />
            {!cameraActive && (
              <div className="w-full h-64 flex items-center justify-center">
                <div className="text-center text-gray-400">
                  <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <p>Camera not active</p>
                </div>
              </div>
            )}
            <canvas ref={canvasRef} className="hidden" />
          </div>

          {/* Controls */}
          <div className="space-y-3">
            {!cameraActive ? (
              <button
                onClick={startCamera}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
              >
                📹 Start Camera
              </button>
            ) : (
              <>
                <button
                  onClick={captureAndProcess}
                  disabled={isProcessing}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                >
                  {isProcessing ? '🔄 Processing...' : '📸 Capture & Process Hand'}
                </button>
                <button
                  onClick={stopCamera}
                  className="w-full bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
                >
                  Stop Camera
                </button>
              </>
            )}
          </div>

          {/* Status */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm">❌ {error}</p>
            </div>
          )}
        </div>

        {/* Results Section */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Results
          </h3>

          {/* Processing State */}
          {isProcessing && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-blue-600 font-medium">Processing with WiLoR...</p>
              <p className="text-gray-500 text-sm mt-2">This may take 20-30 seconds on first run</p>
            </div>
          )}

          {/* Results Display */}
          {result && !isProcessing && (
            <div className="space-y-4">
              {result.hand_detected && result.overlay_image ? (
                <>
                  <img
                    src={result.overlay_image}
                    alt="Hand tracking overlay"
                    className="w-full rounded-lg shadow-md"
                  />
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-800 mb-2">Detection Results:</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div>✅ Hand detected successfully</div>
                      <div>📍 Keypoints found: {result.keypoint_count}</div>
                      <div>📦 Bounding box: {result.hand_data?.bbox ? 'Yes' : 'No'}</div>
                      <div>🎯 Processing: Complete</div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-red-600 font-medium">{result.message}</p>
                </div>
              )}
            </div>
          )}

          {/* Instructions */}
          {!result && !isProcessing && (
            <div className="space-y-4">
              <div className="text-center py-8">
                <div className="w-16 h-16 mx-auto mb-4 bg-gray-200 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m-9 4h10m-10 0V7a2 2 0 012-2h6a2 2 0 012 2v1m-10 0v10a2 2 0 002 2h6a2 2 0 002-2V8" />
                  </svg>
                </div>
                <p className="text-gray-600">Capture an image to see hand tracking results</p>
              </div>

              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-semibold text-blue-800 mb-2">Instructions:</h4>
                <ul className="text-blue-700 text-sm space-y-1">
                  <li>• Position your <strong>RIGHT hand</strong> in the camera view</li>
                  <li>• Click "Capture & Process Hand" button</li>
                  <li>• Wait for WiLoR processing to complete</li>
                  <li>• View hand tracking overlay with keypoints</li>
                </ul>

                <h4 className="font-semibold text-blue-800 mt-4 mb-2">Overlay Legend:</h4>
                <ul className="text-blue-700 text-sm space-y-1">
                  <li>• <span className="inline-block w-3 h-3 bg-green-500 rounded mr-2"></span>Green box = Hand bounding box</li>
                  <li>• <span className="inline-block w-3 h-3 bg-yellow-400 rounded mr-2"></span>Yellow dots = Fingertips</li>
                  <li>• <span className="inline-block w-3 h-3 bg-blue-500 rounded mr-2"></span>Blue dots = Joint positions</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
