import React, { useEffect, useRef, useState, useCallback } from "react";

// Three.js globals - ensure these are loaded in your HTML
declare global {
  interface Window {
    THREE: any;
    STLLoader: any;
  }
}

// Environment configuration for cross-server deployment
const API_CONFIG = {
  // Auto-detect backend URL based on current environment
  BACKEND_URL: (typeof window !== 'undefined' && window.location.hostname === 'localhost') 
                ? 'http://localhost:8000' 
                : 'https://hand-teleop-system.onrender.com',
  WS_URL: (typeof window !== 'undefined' && window.location.hostname === 'localhost')
           ? 'ws://localhost:8000'
           : 'wss://hand-teleop-system.onrender.com',
  RECONNECT_INTERVAL: 3000,
  PING_INTERVAL: 30000,
  REQUEST_TIMEOUT: 10000
};

const JOINT_NAMES = [
  "base_link",
  "shoulder_pan", 
  "shoulder_lift",
  "elbow_flex",
  "wrist_flex",
  "gripper",
];

const ROBOTS = [
  { id: 'so101', name: 'SO-101 Humanoid Hand', dof: 6, description: 'Dexterous robotic hand' },
  { id: 'ur5e', name: 'UR5e', dof: 6, description: 'Universal Robots collaborative arm' },
  { id: 'simulation', name: 'Simulation Mode', dof: 6, description: 'Virtual robot for testing' }
];

export default function SO101Demo() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const pingIntervalRef = useRef<number | null>(null);
  
  // State
  const [jointPositions, setJointPositions] = useState<number[]>([0, 0, 0, 0, 0, 0]);
  const [selectedRobot, setSelectedRobot] = useState('so101');
  const [isConnected, setIsConnected] = useState(false);
  const [isTracking, setIsTracking] = useState(false);
  const [fps, setFps] = useState(0);
  const [latency, setLatency] = useState(0);
  const [messageCount, setMessageCount] = useState(0);
  const [wsStatus, setWsStatus] = useState("Disconnected");
  const [showAnalytics, setShowAnalytics] = useState(true);
  const [consoleLogs, setConsoleLogs] = useState<string[]>([
    "SO-101 Demo initialized",
    "Ready for robot connection"
  ]);

  // Helper to add console logs
  const addToConsole = useCallback((message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setConsoleLogs(prev => [`[${timestamp}] ${message}`, ...prev].slice(0, 20));
  }, []);

  // WebSocket Management
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      addToConsole("Already connected to WebSocket");
      return;
    }

    try {
      const wsUrl = `${API_CONFIG.WS_URL}/api/robot/so101/simulation`;
      addToConsole(`Connecting to WebSocket: ${wsUrl}`);
      
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        setIsConnected(true);
        setWsStatus("Connected");
        addToConsole("WebSocket connected successfully");
        
        // Start ping/pong
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = setInterval(() => {
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            const pingTime = Date.now();
            wsRef.current.send(JSON.stringify({
              type: "ping",
              timestamp: pingTime
            }));
          }
        }, API_CONFIG.PING_INTERVAL);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setMessageCount(prev => prev + 1);
          
          if (message.type === "pong") {
            const pongTime = Date.now();
            const pingTime = message.timestamp || pongTime;
            setLatency(pongTime - pingTime);
          } else if (message.type === "robot_state") {
            // Update robot visualization with backend state
            const joints = message.data?.joint_positions || [];
            if (joints.length === 6) {
              setJointPositions(joints);
            }
          } else if (message.type === "error") {
            addToConsole(`Backend error: ${message.message}`);
          }
        } catch (error) {
          addToConsole(`Failed to parse WebSocket message: ${error}`);
        }
      };

      wsRef.current.onclose = (event) => {
        setIsConnected(false);
        setWsStatus("Disconnected");
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        
        if (event.code !== 1000) {
          addToConsole(`WebSocket closed unexpectedly: ${event.reason || 'Unknown reason'}`);
          // Auto-reconnect unless manually disconnected
          if (event.code !== 1000) {
            reconnectTimeoutRef.current = setTimeout(() => {
              addToConsole("Attempting to reconnect...");
              connectWebSocket();
            }, API_CONFIG.RECONNECT_INTERVAL);
          }
        } else {
          addToConsole("WebSocket disconnected");
        }
      };

      wsRef.current.onerror = (error) => {
        addToConsole(`WebSocket error: ${error}`);
        setWsStatus("Error");
      };

    } catch (error) {
      addToConsole(`Failed to create WebSocket connection: ${error}`);
      setWsStatus("Failed");
    }
  }, [addToConsole]);

  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close(1000, "Manual disconnect");
      wsRef.current = null;
    }
    setIsConnected(false);
    setWsStatus("Disconnected");
    addToConsole("Disconnected from robot");
  }, [addToConsole]);

  const sendWebSocketMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      return true;
    } else {
      addToConsole("Cannot send message: WebSocket not connected");
      return false;
    }
  }, [addToConsole]);

  // Three.js simulation class
  useEffect(() => {
    let simulation: any = null;
    let running = true;

    class SO101Simulation {
      scene: any;
      camera: any;
      renderer: any;
      robot: any;
      websocket: any;
      animationId: any;
      jointObjects: any[] = [];
      frameCount = 0;
      lastTime = performance.now();

      constructor() {
        this.init();
      }

      async init() {
        await this.initThreeJS();
        await this.loadRobot();
        this.setupControls();
        this.startAnimation();
        addToConsole("SO-101 Simulation initialized successfully");
      }

      updateRobotVisualization(jointAngles: number[]) {
        for (let i = 0; i < Math.min(jointAngles.length, this.jointObjects.length); i++) {
          const jointObject = this.jointObjects[i];
          const angle = jointAngles[i];
          if (!jointObject) continue;
          jointObject.rotation.set(0, 0, 0);
          jointObject.scale.set(1, 1, 1);
          if (i > 0) jointObject.rotation.z = angle;
        }
      }

      async initThreeJS() {
        const THREE = window.THREE;
        if (!THREE) {
          addToConsole("THREE.js not found - please load Three.js library");
          return;
        }
        
        const canvas = canvasRef.current;
        const container = containerRef.current;
        if (!canvas || !container) return;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1e293b);
        
        this.camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.01, 1000);
        this.camera.position.set(0.6, 0.6, 0.6);
        this.camera.lookAt(0, 0.1, 0.1);
        
        this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
        
        // Lighting
        this.scene.add(new THREE.AmbientLight(0x808080, 0.8));
        const keyLight = new THREE.DirectionalLight(0xffffff, 1.5);
        keyLight.position.set(2, 3, 1);
        keyLight.castShadow = true;
        this.scene.add(keyLight);
        
        const fillLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
        fillLight1.position.set(-1, 1, 2);
        this.scene.add(fillLight1);
        
        const fillLight2 = new THREE.DirectionalLight(0xffffff, 0.6);
        fillLight2.position.set(-1, -0.5, -1);
        this.scene.add(fillLight2);
        
        // Ground
        const ground = new THREE.Mesh(
          new THREE.PlaneGeometry(2, 2),
          new THREE.MeshLambertMaterial({ color: 0x0f1419 })
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);
        
        this.setupCameraControls(canvas);
      }

      setupCameraControls(canvas: HTMLCanvasElement) {
        let isMouseDown = false, mouseX = 0, mouseY = 0;
        let cameraRadius = 1.0, cameraTheta = Math.PI / 4, cameraPhi = Math.PI / 4;
        
        const updateCameraPosition = () => {
          this.camera.position.x = cameraRadius * Math.sin(cameraPhi) * Math.cos(cameraTheta);
          this.camera.position.y = cameraRadius * Math.cos(cameraPhi);
          this.camera.position.z = cameraRadius * Math.sin(cameraPhi) * Math.sin(cameraTheta) + 0.2;
          this.camera.lookAt(0, 0, 0.2);
        };

        canvas.addEventListener("mousedown", (e: MouseEvent) => {
          isMouseDown = true;
          mouseX = e.clientX;
          mouseY = e.clientY;
        });
        
        canvas.addEventListener("mousemove", (e: MouseEvent) => {
          if (isMouseDown) {
            const deltaX = e.clientX - mouseX;
            const deltaY = e.clientY - mouseY;
            cameraTheta += deltaX * 0.01;
            cameraPhi = Math.max(0.1, Math.min(Math.PI - 0.1, cameraPhi + deltaY * 0.01));
            updateCameraPosition();
            mouseX = e.clientX;
            mouseY = e.clientY;
          }
        });
        
        canvas.addEventListener("mouseup", () => {
          isMouseDown = false;
        });
        
        canvas.addEventListener("wheel", (e: WheelEvent) => {
          cameraRadius = Math.max(0.1, cameraRadius + e.deltaY * 0.01);
          updateCameraPosition();
          e.preventDefault();
        });
        
        updateCameraPosition();
      }

      async loadRobot() {
        const THREE = window.THREE;
        const STLLoader = window.STLLoader;
        
        if (!THREE || !STLLoader) {
          addToConsole("Creating placeholder robot (STL loader not available)");
          this.createPlaceholderRobot();
          return;
        }

        try {
          addToConsole("Loading SO-101 robot with real STL meshes...");
          
          this.robot = new THREE.Group();
          this.robot.name = 'so101_real';
          
          const robotParts = [
            { file: "Base_SO101.stl", color: 0xE0E0E0, position: [0, 0, 0], rotation: [0, 0, 0], scale: 0.001, joint: "base_link", parent: null },
            { file: "sts3215_03a_v1.stl", color: 0xFFFFFF, position: [0, 0, 0.04], rotation: [0, 0, 0], scale: 0.001, joint: "shoulder_pan", parent: 0 },
            { file: "Upper_arm_SO101.stl", color: 0xE0E0E0, position: [0, 0, 0.03], rotation: [-Math.PI/2, 0, 0], scale: 0.001, joint: "shoulder_lift", parent: 1 },
            { file: "Under_arm_SO101.stl", color: 0xFFFFFF, position: [0, 0.10, 0], rotation: [0, 0, 0], scale: 0.001, joint: "elbow_flex", parent: 2 },
            { file: "Wrist_Roll_SO101.stl", color: 0xE0E0E0, position: [0, 0.08, 0], rotation: [0, 0, 0], scale: 0.001, joint: "wrist_flex", parent: 3 },
            { file: "Moving_Jaw_SO101.stl", color: 0xFFFFFF, position: [0, 0.05, 0], rotation: [0, 0, 0], scale: 0.001, joint: "gripper", parent: 4 },
          ];
          
          this.jointObjects = [];
          
          // Create joint groups
          for (let i = 0; i < robotParts.length; i++) {
            const jointGroup = new THREE.Group();
            jointGroup.name = robotParts[i].joint;
            this.jointObjects.push(jointGroup);
          }
          
          // Load meshes and build hierarchy
          for (let i = 0; i < robotParts.length; i++) {
            const part = robotParts[i];
            try {
              const geometry = await this.loadSTLFile(part.file);
              const material = new THREE.MeshStandardMaterial({ 
                color: part.color, 
                metalness: 0.8, 
                roughness: 0.3, 
                side: THREE.DoubleSide 
              });
              
              const mesh = new THREE.Mesh(geometry, material);
              mesh.castShadow = true;
              mesh.receiveShadow = true;
              mesh.name = part.file;
              mesh.scale.set(part.scale, part.scale, part.scale);
              mesh.rotation.set(...part.rotation);
              mesh.position.set(0, 0, 0);
              
              const jointGroup = this.jointObjects[i];
              jointGroup.add(mesh);
              
              if (part.parent !== null && part.parent < i) {
                this.jointObjects[part.parent].add(jointGroup);
                jointGroup.position.set(...part.position);
              } else {
                this.robot.add(jointGroup);
                jointGroup.position.set(...part.position);
              }
              
              addToConsole(`Loaded ${part.file}`);
            } catch (error) {
              addToConsole(`Failed to load ${part.file}`);
            }
          }
          
          this.scene.add(this.robot);
          addToConsole("SO-101 robot loaded successfully!");
          
        } catch (error) {
          addToConsole("Error loading robot - using placeholder");
          this.createPlaceholderRobot();
        }
      }

      async loadSTLFile(filename: string): Promise<any> {
        return new Promise((resolve, reject) => {
          const loader = new window.STLLoader();
          const url = `${API_CONFIG.BACKEND_URL}/api/assets/robot/so101/${filename}`;
          
          // Add timeout handling
          const timeoutId = setTimeout(() => {
            reject(new Error(`STL load timeout for ${filename}`));
          }, API_CONFIG.REQUEST_TIMEOUT);
          
          loader.load(
            url,
            (geometry: any) => {
              clearTimeout(timeoutId);
              resolve(geometry);
            },
            (progress: any) => {
              // Optional: track loading progress
            },
            (error: any) => {
              clearTimeout(timeoutId);
              addToConsole(`Failed to load STL ${filename}: ${error}`);
              reject(error);
            }
          );
        });
      }

      createPlaceholderRobot() {
        const THREE = window.THREE;
        if (!THREE) return;

        this.robot = new THREE.Group();
        this.robot.name = 'so101_placeholder';
        
        const robotParts = [
          { name: 'base_link', color: 0xE0E0E0, position: [0, 0, 0], size: [0.08, 0.08, 0.03] },
          { name: 'shoulder_pan', color: 0xFFFFFF, position: [0, 0, 0.04], size: [0.05, 0.05, 0.06] },
          { name: 'shoulder_lift', color: 0xE0E0E0, position: [0, 0, 0.03], size: [0.04, 0.10, 0.04] },
          { name: 'elbow_flex', color: 0xFFFFFF, position: [0, 0.10, 0], size: [0.04, 0.08, 0.04] },
          { name: 'wrist_flex', color: 0xE0E0E0, position: [0, 0.08, 0], size: [0.03, 0.05, 0.03] },
          { name: 'gripper', color: 0xFFFFFF, position: [0, 0.05, 0], size: [0.03, 0.04, 0.03] }
        ];
        
        this.jointObjects = [];
        
        // Create joint groups
        for (let i = 0; i < robotParts.length; i++) {
          const jointGroup = new THREE.Group();
          jointGroup.name = robotParts[i].name;
          this.jointObjects.push(jointGroup);
        }
        
        // Create meshes and build hierarchy
        for (let i = 0; i < robotParts.length; i++) {
          const part = robotParts[i];
          const geometry = new THREE.BoxGeometry(...part.size);
          const material = new THREE.MeshStandardMaterial({ 
            color: part.color,
            metalness: 0.8,
            roughness: 0.3
          });
          
          const mesh = new THREE.Mesh(geometry, material);
          mesh.castShadow = true;
          mesh.receiveShadow = true;
          mesh.name = part.name;
          
          const jointGroup = this.jointObjects[i];
          jointGroup.add(mesh);
          
          if (i > 0) {
            this.jointObjects[i - 1].add(jointGroup);
            jointGroup.position.set(...part.position);
          } else {
            this.robot.add(jointGroup);
            jointGroup.position.set(...part.position);
          }
        }
        
        this.scene.add(this.robot);
        addToConsole("Placeholder robot created");
      }

      setupControls() {
        // Controls will be handled by React sliders
      }

      startAnimation() {
        const animate = () => {
          if (!running) return;
          this.animationId = requestAnimationFrame(animate);
          
          this.frameCount++;
          const currentTime = performance.now();
          if (currentTime - this.lastTime >= 1000) {
            setFps(Math.round((this.frameCount * 1000) / (currentTime - this.lastTime)));
            this.frameCount = 0;
            this.lastTime = currentTime;
          }
          
          this.renderer.render(this.scene, this.camera);
        };
        animate();
      }

      updateJoints(joints: number[]) {
        this.updateRobotVisualization(joints);
      }

      destroy() {
        running = false;
        if (this.animationId) {
          cancelAnimationFrame(this.animationId);
        }
      }
    }

    // Initialize simulation
    simulation = new SO101Simulation();

    // Update robot when joint positions change
    const updateJoints = () => {
      if (simulation) {
        simulation.updateJoints(jointPositions);
      }
    };
    updateJoints();

    return () => {
      running = false;
      if (simulation) {
        simulation.destroy();
      }
    };
  }, [jointPositions, addToConsole]);

  // Event handlers
  const handleSlider = (i: number, value: number) => {
    const newJoints = [...jointPositions];
    newJoints[i] = value;
    setJointPositions(newJoints);
    
    // Send joint update to backend via WebSocket
    const success = sendWebSocketMessage({
      type: "set_joints",
      positions: newJoints,
      smooth: true
    });
    
    if (success) {
      addToConsole(`Joint ${i + 1} moved to ${value.toFixed(2)} rad`);
    } else {
      addToConsole(`Failed to send joint update (not connected)`);
    }
  };

  const connectToRobot = () => {
    if (isConnected) {
      disconnectWebSocket();
    } else {
      connectWebSocket();
    }
  };

  const toggleTracking = () => {
    if (!isConnected) {
      addToConsole("Cannot start tracking: robot not connected");
      return;
    }
    
    const newTracking = !isTracking;
    setIsTracking(newTracking);
    
    // Send tracking command to backend
    sendWebSocketMessage({
      type: "set_tracking",
      enabled: newTracking
    });
    
    addToConsole(newTracking ? "Hand tracking started" : "Hand tracking stopped");
  };

  const resetRobot = () => {
    const homePosition = [0, 0, 0, 0, 0, 0];
    setJointPositions(homePosition);
    
    if (isConnected) {
      sendWebSocketMessage({
        type: "set_joints",
        positions: homePosition,
        smooth: true
      });
      addToConsole("Robot reset to home position (sent to backend)");
    } else {
      addToConsole("Robot reset to home position (local only)");
    }
  };

  const clearConsole = () => {
    setConsoleLogs([]);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, [disconnectWebSocket]);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Navigation Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-gray-800/70 backdrop-blur-md border-b border-gray-700/50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center">
              <span className="text-white font-bold text-lg">JP</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Hand Teleop System</h1>
              <p className="text-sm text-gray-400">SO-101 Interactive Demo</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-xs text-gray-300">
              <div>FPS: <span className="text-orange-400 font-mono">{fps}</span></div>
              <div>Status: <span className={
                wsStatus === "Connected" ? "text-green-400" : 
                wsStatus === "Connecting" ? "text-yellow-400" : 
                wsStatus === "Error" ? "text-red-400" : "text-gray-400"
              }>{wsStatus}</span></div>
              <div>Backend: <span className="text-blue-400 font-mono text-xs">
                {API_CONFIG.BACKEND_URL.replace(/^https?:\/\//, '')}
              </span></div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="pt-20 px-6 max-w-6xl mx-auto">
        
        {/* Robot Rendering Area - Large, Full Width */}
        <div className="mb-8">
          <div className="bg-gray-800 rounded-lg border-2 border-orange-500/30 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 bg-orange-500 rounded"></div>
                <h2 className="text-xl font-semibold text-white">Robot Embodiment</h2>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  isConnected ? "bg-green-500/20 text-green-400" : "bg-gray-600/20 text-gray-400"
                }`}>
                  {isConnected ? "Connected" : "Disconnected"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <select 
                  value={selectedRobot}
                  onChange={(e) => setSelectedRobot(e.target.value)}
                  className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm text-white"
                >
                  {ROBOTS.map(robot => (
                    <option key={robot.id} value={robot.id}>
                      {robot.name} ({robot.dof} DOF)
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            {/* 3D Robot Visualization */}
            <div 
              ref={containerRef}
              className="w-full h-96 bg-gray-900 rounded-lg border border-gray-700 relative overflow-hidden"
            >
              <canvas ref={canvasRef} className="w-full h-full" />
              <div className="absolute top-2 left-2 bg-gray-900/80 px-2 py-1 rounded text-xs text-orange-400 font-mono">
                Rendering: {fps} FPS | Msgs: {messageCount}
              </div>
            </div>

            {/* Robot Actions */}
            <div className="flex gap-3 mt-4">
              <button 
                onClick={connectToRobot}
                className={`px-4 py-2 rounded transition ${
                  isConnected 
                    ? "bg-red-600 hover:bg-red-700 text-white" 
                    : "bg-orange-500 hover:bg-orange-600 text-white"
                }`}
              >
                {isConnected ? "Disconnect" : "Connect Robot"}
              </button>
              <button 
                onClick={toggleTracking}
                disabled={!isConnected}
                className={`px-4 py-2 rounded transition ${
                  isTracking
                    ? "bg-yellow-600 hover:bg-yellow-700 text-white"
                    : "bg-green-600 hover:bg-green-700 text-white disabled:bg-gray-600 disabled:text-gray-400"
                }`}
              >
                {isTracking ? "Stop Tracking" : "Start Tracking"}
              </button>
              <button 
                onClick={resetRobot}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded transition"
              >
                Reset Position
              </button>
            </div>
          </div>
        </div>

        {/* Joint Controls */}
        <div className="mb-8">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h2 className="text-lg font-semibold mb-4 text-orange-400 flex items-center gap-2">
              <div className="w-4 h-4 bg-orange-500 rounded"></div>
              Joint Controls
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {JOINT_NAMES.map((name, i) => (
                <div key={name} className="flex flex-col">
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm text-gray-300 font-medium">
                      {name.replace('_', ' ').toUpperCase()}
                    </label>
                    <span className="text-xs text-orange-400 font-mono bg-gray-900 px-2 py-1 rounded">
                      {jointPositions[i].toFixed(2)} rad
                    </span>
                  </div>
                  <input
                    type="range"
                    min={-3.14}
                    max={3.14}
                    step={0.01}
                    value={jointPositions[i]}
                    onChange={e => handleSlider(i, parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider-orange"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>-π</span>
                    <span>0</span>
                    <span>π</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Analytics & Debug Panel */}
        <div className="mb-8">
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <button
              onClick={() => setShowAnalytics(!showAnalytics)}
              className="w-full p-4 text-left flex items-center justify-between hover:bg-gray-700/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 bg-orange-500 rounded"></div>
                <h2 className="text-lg font-semibold text-white">Analytics & Debug Info</h2>
              </div>
              <span className="text-orange-400 text-lg">
                {showAnalytics ? "▲" : "▼"}
              </span>
            </button>

            {showAnalytics && (
              <div className="border-t border-gray-700 p-6">
                <div className="grid md:grid-cols-2 gap-6">
                  
                  {/* Camera Feed Placeholder */}
                  <div>
                    <h3 className="font-medium mb-3 text-orange-400 flex items-center gap-2">
                      <div className="w-3 h-3 bg-orange-500 rounded"></div>
                      Camera Feed
                    </h3>
                    <div className="bg-gray-900 rounded-lg border border-gray-600 h-48 flex items-center justify-center">
                      <div className="text-center text-gray-400">
                        <div className="text-4xl mb-2">📷</div>
                        <p className="text-sm">Camera feed will appear here</p>
                        <p className="text-xs text-gray-500">Grant camera access to start</p>
                      </div>
                    </div>
                  </div>

                  {/* System Stats */}
                  <div>
                    <h3 className="font-medium mb-3 text-orange-400 flex items-center gap-2">
                      <div className="w-3 h-3 bg-orange-500 rounded"></div>
                      System Stats
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-300">Rendering FPS:</span>
                        <span className="text-orange-400 font-mono">{fps}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">WebSocket:</span>
                        <span className={isConnected ? "text-green-400" : "text-red-400"}>
                          {wsStatus}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Messages:</span>
                        <span className="text-blue-400 font-mono">{messageCount}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Latency:</span>
                        <span className="text-yellow-400 font-mono">{latency}ms</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Output Console */}
                <div className="mt-6">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-orange-400 flex items-center gap-2">
                      <div className="w-3 h-3 bg-orange-500 rounded"></div>
                      Output Console
                    </h3>
                    <button 
                      onClick={clearConsole}
                      className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded transition"
                    >
                      Clear
                    </button>
                  </div>
                  <div className="bg-gray-900 border border-gray-600 rounded-lg p-3 h-32 overflow-y-auto">
                    {consoleLogs.length === 0 ? (
                      <div className="text-gray-500 text-xs">Console output will appear here...</div>
                    ) : (
                      <div className="text-xs font-mono space-y-1">
                        {consoleLogs.map((log, index) => (
                          <div key={index} className="text-gray-300">{log}</div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-6 flex gap-3">
                  <button 
                    onClick={() => window.open(`${API_CONFIG.BACKEND_URL}/docs`, '_blank')}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition"
                  >
                    API Documentation
                  </button>
                  <button 
                    onClick={() => window.open('https://github.com/7jep7/hand-teleop-system', '_blank')}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded transition"
                  >
                    GitHub Repository
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Custom CSS for slider styling */}
      <style jsx>{`
        .slider-orange::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #f97316;
          cursor: pointer;
        }
        .slider-orange::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #f97316;
          cursor: pointer;
          border: none;
        }
      `}</style>
    </div>
  );
}
