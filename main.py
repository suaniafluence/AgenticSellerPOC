"""Point d'entrée principal pour l'assistant commercial IAfluence."""
import sys
from orchestrator import SalesOrchestrator
from memory import set_memory_store, InMemoryStore, JSONFileStore
from config import config


def print_message(message: dict):
    """Pretty print a message."""
    role = message.get("role", "unknown")
    content = message.get("content", "")
    metadata = message.get("metadata", {})

    if role == "user":
        print(f"\n👤 PROSPECT : {content}")
    elif role == "assistant":
        agent = metadata.get("agent", "unknown")
        agent_emoji = {
            "classifier": "🔍",
            "seller": "💼",
            "negotiator": "🤝",
            "supervisor": "👨‍💼",
            "crm": "📊",
        }.get(agent, "🤖")
        print(f"\n{agent_emoji} {agent.upper()} : {content}")


def run_interactive_demo():
    """Run an interactive demo of the IAfluence sales agent."""
    print("="*70)
    print("🚀 IAFLUENCE - Assistant Commercial IA")
    print("="*70)
    print("\nBienvenue dans l'assistant commercial IAfluence.")
    print("Système multi-agents propulsé par LangGraph.")
    print("\nIAfluence accompagne les PME et ETI dans leur transformation IA :")
    print("  • Stratégie IA & Gouvernance")
    print("  • Formation & Montée en compétences")
    print("  • Expertise technique & POC")
    print("\nTapez vos messages comme un prospect. Tapez 'quit' pour terminer.\n")

    # Initialize orchestrator
    orchestrator = SalesOrchestrator()

    # Get initial message
    print("Entrez votre premier message :")
    initial_message = input("👤 Vous : ").strip()

    if not initial_message:
        print("❌ Aucun message. Fin de session.")
        return

    # Start conversation
    print("\n⚙️  Traitement en cours...\n")
    state = orchestrator.run_conversation(initial_message)
    session_id = state["session_id"]

    # Display conversation
    for message in state["messages"]:
        print_message(message)

    # Continue conversation loop
    while not state.get("closed", False):
        print("\n" + "-"*70)
        user_input = input("👤 Vous : ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("\n👋 Fin de la conversation...")
            break

        if not user_input:
            continue

        # Process message
        print("\n⚙️  Traitement...\n")
        state = orchestrator.continue_conversation(session_id, user_input)

        # Display new messages (only the ones added in this round)
        recent_messages = state["messages"][-2:]  # Show last 2 messages
        for message in recent_messages:
            if message.get("role") != "user" or message.get("content") != user_input:
                print_message(message)

    # Show final summary
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DE LA CONVERSATION")
    print("="*70)
    print(f"Session ID : {session_id}")
    print(f"Type de lead : {state.get('lead_type', 'Inconnu')}")
    print(f"Score du lead : {state.get('lead_score', 0)}/100")
    print(f"Qualifié : {'✅ Oui' if state.get('qualified') else '❌ Non'}")
    print(f"Converti : {'✅ Oui' if state.get('converted') else '❌ Non'}")
    print(f"Escaladé : {'⬆️ Oui' if state.get('escalated') else '❌ Non'}")
    print(f"Messages échangés : {len(state.get('messages', []))}")
    print(f"Offres proposées : {len(state.get('offers_made', []))}")
    print(f"Tours de négociation : {state.get('negotiation_count', 0)}")
    print("="*70)

    if state.get("key_insights"):
        print("\n💡 INSIGHTS CLÉS :")
        for i, insight in enumerate(state.get("key_insights", []), 1):
            print(f"{i}. {insight}")


def run_example_scenario(scenario_name: str = "pme_shadow_ia"):
    """Run a predefined example scenario."""
    from examples import SCENARIOS

    if scenario_name not in SCENARIOS:
        print(f"❌ Scénario '{scenario_name}' non trouvé.")
        print(f"Scénarios disponibles : {', '.join(SCENARIOS.keys())}")
        return

    scenario = SCENARIOS[scenario_name]
    print("="*70)
    print(f"🎬 SCÉNARIO : {scenario['name']}")
    print("="*70)
    print(f"Description : {scenario['description']}\n")

    # Initialize orchestrator
    orchestrator = SalesOrchestrator()

    # Run conversation
    state = None
    session_id = None

    for i, message in enumerate(scenario["messages"]):
        print(f"\n{'='*70}")
        print(f"TOUR {i+1}")
        print('='*70)

        if i == 0:
            # First message
            state = orchestrator.run_conversation(message)
            session_id = state["session_id"]
        else:
            # Continue conversation
            state = orchestrator.continue_conversation(session_id, message)

        # Display conversation
        print_message({"role": "user", "content": message})

        # Show agent responses from this turn
        recent_messages = [msg for msg in state["messages"] if msg.get("role") == "assistant"]
        if recent_messages:
            print_message(recent_messages[-1])

    # Show final summary
    print("\n" + "="*70)
    print("📊 SCÉNARIO TERMINÉ")
    print("="*70)
    print(f"Converti : {'✅ Oui' if state.get('converted') else '❌ Non'}")
    print(f"Escaladé : {'⬆️ Oui' if state.get('escalated') else '❌ Non'}")
    print(f"Score final : {state.get('lead_score', 0)}/100")
    print("="*70)


def main():
    """Main entry point."""
    # Set up memory store
    # Use JSONFileStore for persistence, or InMemoryStore for testing
    # set_memory_store(JSONFileStore("./data"))
    set_memory_store(InMemoryStore())

    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "demo":
            run_interactive_demo()
        elif command == "scenario":
            scenario_name = sys.argv[2] if len(sys.argv) > 2 else "pme_shadow_ia"
            run_example_scenario(scenario_name)
        elif command == "list":
            from examples import list_scenarios
            list_scenarios()
        else:
            print(f"Commande inconnue : {command}")
            print("\nUtilisation :")
            print("  python main.py demo              - Démo interactive")
            print("  python main.py scenario <nom>    - Lancer un scénario")
            print("  python main.py list              - Lister les scénarios")
    else:
        # Default to interactive demo
        run_interactive_demo()


if __name__ == "__main__":
    main()
