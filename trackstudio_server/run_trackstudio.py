#!/usr/bin/env python3
"""
TrackStudio Server for Basketball POC
Launches TrackStudio with CPU-only configuration for basketball video tracking.
"""

import os
import sys
import logging
import torch
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_cpu_only_mode():
    """Configure PyTorch for CPU-only mode"""
    try:
        # Force CPU usage
        torch.set_default_device('cpu')
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
        os.environ['OMP_NUM_THREADS'] = '4'
        os.environ['OPENBLAS_NUM_THREADS'] = '4'
        os.environ['MKL_NUM_THREADS'] = '4'
        
        logger.info("✅ Configured for CPU-only mode")
        logger.info(f"PyTorch device: {torch.get_default_device()}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
        
    except Exception as e:
        logger.error(f"Error configuring CPU mode: {e}")

def launch_trackstudio_server():
    """Launch TrackStudio server for basketball tracking"""
    try:
        # Add TrackStudio to Python path
        trackstudio_path = Path(__file__).parent / "trackstudio"
        sys.path.insert(0, str(trackstudio_path))
        
        import trackstudio as ts
        
        logger.info("🚀 Launching TrackStudio server...")
        
        # Launch TrackStudio with basketball-optimized configuration
        app = ts.launch(
            # For now, we'll use test configuration
            # In real deployment, these would be your camera streams
            rtsp_streams=[
                "rtsp://localhost:8554/camera0",  # Left backboard camera
                "rtsp://localhost:8554/camera1",  # Right backboard camera
            ],
            camera_names=["Left Court", "Right Court"],
            tracker="rfdetr",  # RF-DETR for detection
            server_port=8000,  # API server port
            vision_fps=10.0,   # Optimized for CPU processing
            open_browser=False  # Don't auto-open browser
        )
        
        logger.info("🏀 TrackStudio server running on http://localhost:8000")
        logger.info("📹 Ready for basketball video processing!")
        logger.info("🔗 Access web interface at: http://localhost:8000")
        
        return app
        
    except ImportError as e:
        logger.error(f"❌ TrackStudio import error: {e}")
        logger.info("Trying to run with CLI method...")
        return launch_with_cli()
    except Exception as e:
        logger.error(f"❌ Failed to launch TrackStudio: {e}")
        sys.exit(1)

def launch_with_cli():
    """Alternative launch method using CLI"""
    try:
        logger.info("🚀 Launching TrackStudio via CLI...")
        
        # Use the CLI command
        import subprocess
        cmd = [
            sys.executable, "-m", "trackstudio", "run", 
            "-c", "test_config.json",
            "--vision-fps", "10"
        ]
        
        # Change to trackstudio directory
        cwd = Path(__file__).parent / "trackstudio"
        
        process = subprocess.Popen(
            cmd, 
            cwd=str(cwd),
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True
        )
        
        logger.info("🏀 TrackStudio process started!")
        logger.info("🔗 Access web interface at: http://localhost:8000")
        
        return process
        
    except Exception as e:
        logger.error(f"❌ CLI launch failed: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🏀 Basketball POC - TrackStudio Server")
    print("=" * 50)
    
    # Setup CPU-only mode
    setup_cpu_only_mode()
    
    # Launch TrackStudio
    app = launch_trackstudio_server()
    
    try:
        # Keep the server running
        print("\\n✅ TrackStudio server is running!")
        print("🔗 Web interface: http://localhost:8000")
        print("📡 API endpoint: http://localhost:8000/api")
        print("\\nPress Ctrl+C to stop the server...")
        
        # Keep running indefinitely
        import signal
        import time
        
        def signal_handler(sig, frame):
            print("\\n🛑 Shutting down TrackStudio server...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()