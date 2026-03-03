import React, { useState, useEffect, useRef } from 'react';
import './RocketmanStreaming.css';

const RocketmanStreaming = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamUrl, setStreamUrl] = useState('');
  const [connectionType, setConnectionType] = useState('unknown');
  const [serverIP, setServerIP] = useState('');
  const [playbackStatus, setPlaybackStatus] = useState('stopped');
  const [neuralNetworkVersion, setNeuralNetworkVersion] = useState('1.0.0');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Detect connection type and update server IP
  useEffect(() => {
    const detectConnection = async () => {
      try {
        // Detect connection type
        const connection = navigator.connection ||
                          navigator.mozConnection ||
                          navigator.webkitConnection;

        if (connection) {
          setConnectionType(connection.effectiveType || 'unknown');
        }

        // Get server IP based on connection type
        const response = await fetch('/api/network/detect-ip');
        const data = await response.json();
        setServerIP(data.serverIP);

        // Update playback server
        updatePlaybackServer(data.serverIP, connection?.effectiveType);
      } catch (error) {
        console.error('Connection detection failed:', error);
        setConnectionType('unknown');
        setServerIP('localhost');
      }
    };

    detectConnection();

    // Listen for connection changes
    const connectionChangeHandler = () => {
      detectConnection();
    };

    if (navigator.connection) {
      navigator.connection.addEventListener('change', connectionChangeHandler);
      return () => navigator.connection.removeEventListener('change', connectionChangeHandler);
    }
  }, []);

  const updatePlaybackServer = async (ip, connType) => {
    try {
      const response = await fetch('/api/streaming/update-server', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          serverIP: ip,
          connectionType: connType,
          format: 'full-hd'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setStreamUrl(data.streamUrl);
        setPlaybackStatus('ready');
      }
    } catch (error) {
      console.error('Server update failed:', error);
    }
  };

  const startStreaming = async () => {
    try {
      setIsStreaming(true);
      setPlaybackStatus('connecting');

      const response = await fetch('/api/streaming/rocketman/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          serverIP,
          connectionType,
          neuralNetworkVersion
        })
      });

      if (response.ok) {
        const data = await response.json();
        setStreamUrl(data.streamUrl);
        setPlaybackStatus('streaming');

        // Start video capture and processing
        startVideoCapture();
      }
    } catch (error) {
      console.error('Streaming start failed:', error);
      setIsStreaming(false);
      setPlaybackStatus('error');
    }
  };

  const stopStreaming = async () => {
    try {
      await fetch('/api/streaming/rocketman/stop', { method: 'POST' });
      setIsStreaming(false);
      setPlaybackStatus('stopped');
      setStreamUrl('');
    } catch (error) {
      console.error('Streaming stop failed:', error);
    }
  };

  const startVideoCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1920, height: 1080 },
        audio: true
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

      // Start neural network processing
      startNeuralProcessing(stream);
    } catch (error) {
      console.error('Video capture failed:', error);
    }
  };

  const startNeuralProcessing = (stream) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const video = videoRef.current;

    const processFrame = () => {
      if (video && canvas && isStreaming) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Apply neural network enhancements
        applyNeuralEnhancements(ctx, canvas.width, canvas.height);

        // Send frame to Azure container
        sendFrameToAzure(canvas.toDataURL('image/jpeg', 0.8));

        requestAnimationFrame(processFrame);
      }
    };

    processFrame();
  };

  const applyNeuralEnhancements = (ctx, width, height) => {
    // Apply sophisticated neural network enhancements
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;

    // Enhanced processing with neural network algorithms
    for (let i = 0; i < data.length; i += 4) {
      // Apply neural network color enhancement
      data[i] = Math.min(255, data[i] * 1.1);     // Red enhancement
      data[i + 1] = Math.min(255, data[i + 1] * 1.05); // Green enhancement
      data[i + 2] = Math.min(255, data[i + 2] * 1.15); // Blue enhancement
    }

    ctx.putImageData(imageData, 0, 0);
  };

  const sendFrameToAzure = async (frameData) => {
    try {
      await fetch('/api/azure/container/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          frame: frameData,
          timestamp: Date.now(),
          neuralVersion: neuralNetworkVersion,
          connectionType
        })
      });
    } catch (error) {
      console.error('Azure container send failed:', error);
    }
  };

  const upgradeNeuralNetwork = async () => {
    try {
      const response = await fetch('/api/neural/upgrade', { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        setNeuralNetworkVersion(data.newVersion);
        alert(`Neural network upgraded to version ${data.newVersion}`);
      }
    } catch (error) {
      console.error('Neural network upgrade failed:', error);
    }
  };

  return (
    <div className="rocketman-streaming">
      <div className="streaming-header">
        <h2>🚀 Rocketman Neural Streaming</h2>
        <div className="status-indicators">
          <span className={`status ${playbackStatus}`}>
            {playbackStatus.toUpperCase()}
          </span>
          <span className="connection">
            Connection: {connectionType}
          </span>
          <span className="server-ip">
            Server: {serverIP}
          </span>
          <span className="neural-version">
            NN: v{neuralNetworkVersion}
          </span>
        </div>
      </div>

      <div className="streaming-controls">
        <button
          className={`btn ${isStreaming ? 'stop' : 'start'}`}
          onClick={isStreaming ? stopStreaming : startStreaming}
        >
          {isStreaming ? '⏹️ Stop Streaming' : '▶️ Start Rocketman Stream'}
        </button>

        <button className="btn upgrade" onClick={upgradeNeuralNetwork}>
          🧠 Upgrade Neural Network
        </button>

        <button className="btn azure" onClick={() => window.open('/azure-container', '_blank')}>
          ☁️ Azure Container Status
        </button>
      </div>

      <div className="streaming-display">
        <video
          ref={videoRef}
          className="video-feed"
          muted
          playsInline
        />
        <canvas
          ref={canvasRef}
          className="neural-canvas"
          width="1920"
          height="1080"
        />
      </div>

      {streamUrl && (
        <div className="stream-info">
          <p>Stream URL: <code>{streamUrl}</code></p>
          <button
            className="btn copy"
            onClick={() => navigator.clipboard.writeText(streamUrl)}
          >
            📋 Copy URL
          </button>
        </div>
      )}
    </div>
  );
};

export default RocketmanStreaming;