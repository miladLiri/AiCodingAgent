from agent.core import Agent

def main():
    agent = Agent()
    print("AI Agent ready. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue

        response = agent.step(user_input)
        print(f"\nAgent: {response}\n")


if __name__ == "__main__":
    main()
