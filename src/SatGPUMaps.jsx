import React, { useState, useEffect, useRef } from 'react';
import './SatGPUMaps.css';

const SatGPUMaps = () => {
  const [satelliteData, setSatelliteData] = useState([]);
  const [gpuStatus, setGpuStatus] = useState({});
  const [neuralNetworkStatus, setNeuralNetworkStatus] = useState('initializing');
  const [selectedSatellite, setSelectedSatellite] = useState(null);
  const [mapView, setMapView] = useState('global');
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  // Initialize satellite data
  useEffect(() => {
    initializeSatellites();
    initializeGPUStatus();
    startNeuralProcessing();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  const initializeSatellites = () => {
    const satellites = [
      {
        id: 'sat-001',
        name: 'Luna-Observer-1',
        position: { lat: 28.5, lng: -80.6 },
        altitude: 35786,
        status: 'active',
        gpu: 'NVIDIA A100',
        neuralVersion: '2.1.0',
        coverage: 'North America'
      },
      {
        id: 'sat-002',
        name: 'Luna-Observer-2',
        position: { lat: 51.5, lng: 0.1 },
        altitude: 35786,
        status: 'active',
        gpu: 'NVIDIA H100',
        neuralVersion: '2.1.0',
        coverage: 'Europe'
      },
      {
        id: 'sat-003',
        name: 'Luna-Observer-3',
        position: { lat: 35.7, lng: 139.7 },
        altitude: 35786,
        status: 'maintenance',
        gpu: 'AMD MI250',
        neuralVersion: '2.0.5',
        coverage: 'Asia-Pacific'
      },
      {
        id: 'sat-004',
        name: 'Luna-Observer-4',
        position: { lat: -33.9, lng: 151.2 },
        altitude: 35786,
        status: 'active',
        gpu: 'NVIDIA A100',
        neuralVersion: '2.1.0',
        coverage: 'Oceania'
      }
    ];

    setSatelliteData(satellites);
  };

  const initializeGPUStatus = () => {
    setGpuStatus({
      totalGPUs: 16,
      activeGPUs: 14,
      utilization: 87,
      memoryUsage: 92,
      temperature: 68,
      neuralNetworks: {
        objectDetection: 'v2.1.0',
        imageProcessing: 'v2.0.8',
        predictiveAnalytics: 'v2.1.2',
        anomalyDetection: 'v1.9.5'
      }
    });
  };

  const startNeuralProcessing = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let frameCount = 0;

    const animate = () => {
      frameCount++;
      drawSatelliteMap(ctx, canvas.width, canvas.height, frameCount);
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();
  };

  const drawSatelliteMap = (ctx, width, height, frameCount) => {
    // Clear canvas
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, width, height);

    // Draw Earth
    drawEarth(ctx, width, height);

    // Draw satellite orbits
    drawSatelliteOrbits(ctx, width, height, frameCount);

    // Draw satellites
    drawSatellites(ctx, width, height);

    // Draw neural network connections
    drawNeuralConnections(ctx, width, height, frameCount);

    // Draw GPU status overlay
    drawGPUStatus(ctx, width, height);
  };

  const drawEarth = (ctx, width, height) => {
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.25;

    // Earth gradient
    const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius);
    gradient.addColorStop(0, '#4a90e2');
    gradient.addColorStop(0.7, '#2e5c8a');
    gradient.addColorStop(1, '#1a252f');

    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.fill();

    // Continents (simplified)
    ctx.fillStyle = '#2d5a27';
    // North America
    ctx.beginPath();
    ctx.arc(centerX - radius * 0.3, centerY - radius * 0.2, radius * 0.15, 0, Math.PI * 2);
    ctx.fill();
    // Europe/Asia
    ctx.beginPath();
    ctx.arc(centerX + radius * 0.2, centerY - radius * 0.1, radius * 0.12, 0, Math.PI * 2);
    ctx.fill();
  };

  const drawSatelliteOrbits = (ctx, width, height, frameCount) => {
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.25;

    // Orbital paths
    const orbits = [1.2, 1.4, 1.6, 1.8];

    orbits.forEach((multiplier, index) => {
      const orbitRadius = radius * multiplier;

      // Orbit line
      ctx.strokeStyle = `rgba(100, 200, 255, ${0.3 - index * 0.05})`;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(centerX, centerY, orbitRadius, 0, Math.PI * 2);
      ctx.stroke();

      // Orbital markers
      for (let i = 0; i < 8; i++) {
        const angle = (frameCount * 0.01 + i * Math.PI / 4) % (Math.PI * 2);
        const x = centerX + Math.cos(angle) * orbitRadius;
        const y = centerY + Math.sin(angle) * orbitRadius;

        ctx.fillStyle = `rgba(100, 200, 255, ${0.6 - index * 0.1})`;
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fill();
      }
    });
  };

  const drawSatellites = (ctx, width, height) => {
    const centerX = width / 2;
    const centerY = height / 2;
    const earthRadius = Math.min(width, height) * 0.25;

    satelliteData.forEach((satellite, index) => {
      const orbitRadius = earthRadius * (1.2 + index * 0.2);
      const angle = (Date.now() * 0.0001 + index * Math.PI / 2) % (Math.PI * 2);

      const x = centerX + Math.cos(angle) * orbitRadius;
      const y = centerY + Math.sin(angle) * orbitRadius;

      // Satellite body
      ctx.fillStyle = satellite.status === 'active' ? '#00ff88' : '#ff4444';
      ctx.beginPath();
      ctx.arc(x, y, 8, 0, Math.PI * 2);
      ctx.fill();

      // Satellite trail
      ctx.strokeStyle = satellite.status === 'active' ? 'rgba(0, 255, 136, 0.5)' : 'rgba(255, 68, 68, 0.5)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, y, 12, 0, Math.PI * 2);
      ctx.stroke();

      // GPU indicator
      if (satellite.gpu) {
        ctx.fillStyle = '#ffff00';
        ctx.font = '10px Arial';
        ctx.fillText('GPU', x - 10, y - 15);
      }
    });
  };

  const drawNeuralConnections = (ctx, width, height, frameCount) => {
    const centerX = width / 2;
    const centerY = height / 2;
    const earthRadius = Math.min(width, height) * 0.25;

    // Neural network connections between satellites
    satelliteData.forEach((sat1, i) => {
      satelliteData.forEach((sat2, j) => {
        if (i !== j) {
          const orbit1 = earthRadius * (1.2 + i * 0.2);
          const orbit2 = earthRadius * (1.2 + j * 0.2);
          const angle1 = (frameCount * 0.005 + i * Math.PI / 2) % (Math.PI * 2);
          const angle2 = (frameCount * 0.005 + j * Math.PI / 2) % (Math.PI * 2);

          const x1 = centerX + Math.cos(angle1) * orbit1;
          const y1 = centerY + Math.sin(angle1) * orbit1;
          const x2 = centerX + Math.cos(angle2) * orbit2;
          const y2 = centerY + Math.sin(angle2) * orbit2;

          // Neural connection line
          const gradient = ctx.createLinearGradient(x1, y1, x2, y2);
          gradient.addColorStop(0, 'rgba(255, 100, 255, 0.3)');
          gradient.addColorStop(1, 'rgba(100, 255, 255, 0.3)');

          ctx.strokeStyle = gradient;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.stroke();
        }
      });
    });
  };

  const drawGPUStatus = (ctx, width, height) => {
    // GPU Status overlay
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(10, 10, 250, 120);

    ctx.fillStyle = '#00ff88';
    ctx.font = '14px Arial';
    ctx.fillText('GPU CLUSTER STATUS', 20, 30);

    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Arial';
    ctx.fillText(`Total GPUs: ${gpuStatus.totalGPUs}`, 20, 50);
    ctx.fillText(`Active GPUs: ${gpuStatus.activeGPUs}`, 20, 65);
    ctx.fillText(`Utilization: ${gpuStatus.utilization}%`, 20, 80);
    ctx.fillText(`Memory: ${gpuStatus.memoryUsage}%`, 20, 95);
    ctx.fillText(`Temperature: ${gpuStatus.temperature}°C`, 20, 110);

    // Neural Network Status
    ctx.fillStyle = '#00ff88';
    ctx.fillText('NEURAL NETWORKS', 20, 135);

    let yPos = 150;
    Object.entries(gpuStatus.neuralNetworks || {}).forEach(([network, version]) => {
      ctx.fillStyle = '#ffff00';
      ctx.font = '10px Arial';
      ctx.fillText(`${network}: ${version}`, 20, yPos);
      yPos += 15;
    });
  };

  const upgradeNeuralNetwork = async () => {
    setNeuralNetworkStatus('upgrading');
    try {
      const response = await fetch('/api/satellite/neural-upgrade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ targetVersion: '2.2.0' })
      });

      if (response.ok) {
        const data = await response.json();
        setNeuralNetworkStatus('upgraded');
        setGpuStatus(prev => ({
          ...prev,
          neuralNetworks: data.updatedNetworks
        }));

        setTimeout(() => setNeuralNetworkStatus('active'), 3000);
      }
    } catch (error) {
      console.error('Neural network upgrade failed:', error);
      setNeuralNetworkStatus('error');
    }
  };

  const restoreSatellite = async (satelliteId) => {
    try {
      const response = await fetch('/api/satellite/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ satelliteId })
      });

      if (response.ok) {
        setSatelliteData(prev =>
          prev.map(sat =>
            sat.id === satelliteId
              ? { ...sat, status: 'active' }
              : sat
          )
        );
      }
    } catch (error) {
      console.error('Satellite restore failed:', error);
    }
  };

  return (
    <div className="sat-gpu-maps">
      <div className="map-header">
        <h2>🛰️ Satellite GPU Neural Network Map</h2>
        <div className="map-controls">
          <select value={mapView} onChange={(e) => setMapView(e.target.value)}>
            <option value="global">Global View</option>
            <option value="regional">Regional View</option>
            <option value="satellite">Satellite Focus</option>
          </select>

          <button
            className={`btn upgrade ${neuralNetworkStatus}`}
            onClick={upgradeNeuralNetwork}
            disabled={neuralNetworkStatus === 'upgrading'}
          >
            {neuralNetworkStatus === 'upgrading' ? '⏳ Upgrading...' : '🧠 Upgrade NN'}
          </button>
        </div>
      </div>

      <div className="map-container">
        <canvas
          ref={canvasRef}
          width="800"
          height="600"
          className="satellite-canvas"
        />
      </div>

      <div className="satellite-list">
        <h3>Active Satellites</h3>
        <div className="satellite-grid">
          {satelliteData.map(satellite => (
            <div
              key={satellite.id}
              className={`satellite-card ${satellite.status}`}
              onClick={() => setSelectedSatellite(satellite)}
            >
              <div className="satellite-header">
                <h4>{satellite.name}</h4>
                <span className={`status ${satellite.status}`}>
                  {satellite.status}
                </span>
              </div>

              <div className="satellite-info">
                <p><strong>GPU:</strong> {satellite.gpu}</p>
                <p><strong>Neural Net:</strong> v{satellite.neuralVersion}</p>
                <p><strong>Coverage:</strong> {satellite.coverage}</p>
                <p><strong>Altitude:</strong> {satellite.altitude.toLocaleString()} km</p>
              </div>

              {satellite.status === 'maintenance' && (
                <button
                  className="btn restore"
                  onClick={(e) => {
                    e.stopPropagation();
                    restoreSatellite(satellite.id);
                  }}
                >
                  🔧 Restore
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {selectedSatellite && (
        <div className="satellite-details">
          <h3>Details: {selectedSatellite.name}</h3>
          <div className="details-grid">
            <div><strong>ID:</strong> {selectedSatellite.id}</div>
            <div><strong>Position:</strong> {selectedSatellite.position.lat}°, {selectedSatellite.position.lng}°</div>
            <div><strong>GPU:</strong> {selectedSatellite.gpu}</div>
            <div><strong>Neural Version:</strong> {selectedSatellite.neuralVersion}</div>
            <div><strong>Coverage Area:</strong> {selectedSatellite.coverage}</div>
          </div>
          <button className="btn close" onClick={() => setSelectedSatellite(null)}>
            Close
          </button>
        </div>
      )}
    </div>
  );
};

export default SatGPUMaps;