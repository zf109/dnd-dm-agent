"""Interactive D&D REPL using ClaudeSDKClient."""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock
from .claude_agent import get_options, process_message
from .logging_config import logger


async def repl():
    """Interactive session with automatic conversation history."""
    print("🎲 D&D Dungeon Master (type 'exit' to quit)\n")
    logger.info("Starting interactive REPL session")

    async with ClaudeSDKClient(options=get_options()) as client:
        turn_count = 0
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['exit', 'quit']:
                    break

                turn_count += 1
                logger.info(f"[Turn {turn_count}] User input: {user_input[:100]}...")

                # Send message and collect response
                await client.query(user_input)

                response_parts = []
                async for message in client.receive_response():
                    # Apply logging to each message (same as CLI)
                    process_message(message)

                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                response_parts.append(block.text)

                response = "\n".join(response_parts)
                print(f"\nDM: {response}\n")
                logger.info(f"[Turn {turn_count}] Response completed")

            except (EOFError, KeyboardInterrupt):
                logger.info("REPL interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in REPL: {e}", exc_info=True)
                print(f"\n❌ Error: {e}\n")

    logger.info(f"REPL session ended after {turn_count} turns")
    print("\n👋 Thanks for playing!")


def main():
    """Entry point."""
    asyncio.run(repl())


if __name__ == "__main__":
    main()
