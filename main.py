"""Main entry point for the Agentic Seller POC."""
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
        print(f"\n👤 PROSPECT: {content}")
    elif role == "assistant":
        agent = metadata.get("agent", "unknown")
        agent_emoji = {
            "classifier": "🔍",
            "seller": "💼",
            "negotiator": "🤝",
            "supervisor": "👨‍💼",
            "crm": "📊",
        }.get(agent, "🤖")
        print(f"\n{agent_emoji} {agent.upper()}: {content}")


def run_interactive_demo():
    """Run an interactive demo of the sales agent."""
    print("="*70)
    print("🚀 AGENTIC SELLER POC - Interactive Demo")
    print("="*70)
    print("\nThis is a multi-agent sales system powered by LangGraph.")
    print("Type your messages as a prospect, and the AI agents will respond.")
    print("Type 'quit' or 'exit' to end the session.\n")

    # Initialize orchestrator
    orchestrator = SalesOrchestrator()

    # Get initial message
    print("Enter your first message as a prospect:")
    initial_message = input("👤 You: ").strip()

    if not initial_message:
        print("❌ No message entered. Exiting.")
        return

    # Start conversation
    print("\n⚙️  Processing your message through the agent network...\n")
    state = orchestrator.run_conversation(initial_message)
    session_id = state["session_id"]

    # Display conversation
    for message in state["messages"]:
        print_message(message)

    # Continue conversation loop
    while not state.get("closed", False):
        print("\n" + "-"*70)
        user_input = input("👤 You: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("\n👋 Ending conversation...")
            break

        if not user_input:
            continue

        # Process message
        print("\n⚙️  Processing...\n")
        state = orchestrator.continue_conversation(session_id, user_input)

        # Display new messages (only the ones added in this round)
        recent_messages = state["messages"][-2:]  # Show last 2 messages
        for message in recent_messages:
            if message.get("role") != "user" or message.get("content") != user_input:
                print_message(message)

    # Show final summary
    print("\n" + "="*70)
    print("📊 CONVERSATION SUMMARY")
    print("="*70)
    print(f"Session ID: {session_id}")
    print(f"Lead Type: {state.get('lead_type', 'Unknown')}")
    print(f"Lead Score: {state.get('lead_score', 0)}/100")
    print(f"Qualified: {'✅ Yes' if state.get('qualified') else '❌ No'}")
    print(f"Converted: {'✅ Yes' if state.get('converted') else '❌ No'}")
    print(f"Escalated: {'⬆️ Yes' if state.get('escalated') else '❌ No'}")
    print(f"Messages Exchanged: {len(state.get('messages', []))}")
    print(f"Offers Made: {len(state.get('offers_made', []))}")
    print(f"Negotiation Rounds: {state.get('negotiation_count', 0)}")
    print("="*70)

    if state.get("key_insights"):
        print("\n💡 KEY INSIGHTS:")
        for i, insight in enumerate(state.get("key_insights", []), 1):
            print(f"{i}. {insight}")


def run_example_scenario(scenario_name: str = "hot_lead"):
    """Run a predefined example scenario."""
    from examples import SCENARIOS

    if scenario_name not in SCENARIOS:
        print(f"❌ Scenario '{scenario_name}' not found.")
        print(f"Available scenarios: {', '.join(SCENARIOS.keys())}")
        return

    scenario = SCENARIOS[scenario_name]
    print("="*70)
    print(f"🎬 RUNNING SCENARIO: {scenario['name']}")
    print("="*70)
    print(f"Description: {scenario['description']}\n")

    # Initialize orchestrator
    orchestrator = SalesOrchestrator()

    # Run conversation
    state = None
    session_id = None

    for i, message in enumerate(scenario["messages"]):
        print(f"\n{'='*70}")
        print(f"TURN {i+1}")
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
    print("📊 SCENARIO COMPLETE")
    print("="*70)
    print(f"Converted: {'✅ Yes' if state.get('converted') else '❌ No'}")
    print(f"Escalated: {'⬆️ Yes' if state.get('escalated') else '❌ No'}")
    print(f"Final Lead Score: {state.get('lead_score', 0)}/100")
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
            scenario_name = sys.argv[2] if len(sys.argv) > 2 else "hot_lead"
            run_example_scenario(scenario_name)
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python main.py demo              - Run interactive demo")
            print("  python main.py scenario <name>   - Run example scenario")
    else:
        # Default to interactive demo
        run_interactive_demo()


if __name__ == "__main__":
    main()
