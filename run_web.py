#!/usr/bin/env python3
"""Run the IAfluence Agent Monitor web interface."""
import uvicorn
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Start the web server."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     🤖 IAfluence Agent Monitor                            ║
    ║                                                           ║
    ║     Interface de monitoring et configuration              ║
    ║     du système d'agents commerciaux                       ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    print("🚀 Démarrage du serveur sur http://localhost:8000")
    print("📊 Dashboard: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nAppuyez sur Ctrl+C pour arrêter le serveur\n")

    uvicorn.run(
        "web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
