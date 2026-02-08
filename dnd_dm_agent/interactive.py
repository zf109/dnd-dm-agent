"""Interactive D&D REPL using ClaudeSDKClient."""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock
from .claude_agent import get_options


async def repl():
    """Interactive session with automatic conversation history."""
    print("🎲 D&D Dungeon Master (type 'exit' to quit)\n")

    async with ClaudeSDKClient(options=get_options()) as client:
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['exit', 'quit']:
                    break

                # Send message and collect response
                await client.query(user_input)

                response_parts = []
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                response_parts.append(block.text)

                response = "\n".join(response_parts)
                print(f"\nDM: {response}\n")

            except (EOFError, KeyboardInterrupt):
                break

    print("\n👋 Thanks for playing!")


def main():
    """Entry point."""
    asyncio.run(repl())


if __name__ == "__main__":
    main()
