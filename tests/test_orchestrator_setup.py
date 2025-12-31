#!/usr/bin/env python3
"""Test script to reproduce the orchestrator error."""
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import traceback
from orchestrator import SalesOrchestrator

def test_create_prospect():
    """Test creating a prospect to reproduce the error."""
    print("Testing orchestrator initialization and prospect creation...")
    print("="*60)

    try:
        print("1. Creating orchestrator instance...")
        orchestrator = SalesOrchestrator()
        print("✓ Orchestrator created successfully")

        print("\n2. Creating test message...")
        test_message = """Bonjour, je suis Suan Tay de IAfluence.

Notre entreprise compte environ 20-249 employés dans le secteur Autre.
Je suis décideur sur ce type de projet.

Nos problématiques principales : Shadow AI, Gouvernance
Nos centres d'intérêt : automation
Notes additionnelles : Je suis le PDG d'une PME de 50 personnes. On utilise ChatGPT partout sans contrôle et j'ai besoin d'une stratégie IA rapidement. Budget de 5000€/mois disponible.
"""

        print("\n3. Running conversation...")
        session_id = "test-session-123"
        state = orchestrator.run_conversation(test_message, session_id)

        print("✓ Conversation completed successfully")
        print(f"\nFinal state:")
        print(f"  - Lead type: {state.get('lead_type')}")
        print(f"  - Lead score: {state.get('lead_score')}")
        print(f"  - Qualified: {state.get('qualified')}")
        print(f"  - Messages: {len(state.get('messages', []))}")

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        print("\nFull traceback:")
        print("="*60)
        traceback.print_exc()
        print("="*60)
        return False

    return True

if __name__ == "__main__":
    success = test_create_prospect()
    sys.exit(0 if success else 1)
