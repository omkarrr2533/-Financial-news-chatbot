#!/usr/bin/env python3
"""
Financial News Impact Analyzer - Main Entry Point
Run this file to start the application
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app, socketio, init_app, Config
import logging

logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    try:
        # Initialize application
        init_app()
        
        # Print startup information
        print("\n" + "="*60)
        print("  FINANCIAL NEWS IMPACT ANALYZER")
        print("="*60)
        print(f"\n🚀 Server starting...")
        print(f"📍 URL: http://{Config.HOST}:{Config.PORT}")
        print(f"🔧 Environment: {Config.FLASK_ENV}")
        print(f"🐛 Debug Mode: {Config.DEBUG}")
        print(f"\n⏰ Auto-refresh interval: {Config.NEWS_REFRESH_INTERVAL} seconds")
        print(f"\n💡 Open your browser and navigate to: http://localhost:{Config.PORT}")
        print("\n" + "="*60 + "\n")
        
        # Start server
        socketio.run(
            app, 
            host=Config.HOST, 
            port=Config.PORT, 
            debug=Config.DEBUG,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        logger.info("Application stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()