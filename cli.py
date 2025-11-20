#!/usr/bin/env python3
"""
Command-line interface for Microsoft Copilot Agent SDK

Usage:
    python cli.py                    # Start interactive chat
    python cli.py --message "Hello"  # Send a single message
    python cli.py --config           # Show configuration
    python cli.py --help             # Show help

Copyright 2025 AIHQ.ie
Licensed under the Apache License, Version 2.0
"""

import argparse
import sys
from pathlib import Path

# Add the parent directory to the path so we can import copilot_sdk
sys.path.insert(0, str(Path(__file__).parent))

from copilot_sdk import CopilotAgentClient, CopilotConfig


def main():
    """Main CLI entry point"""

    parser = argparse.ArgumentParser(
        description="Microsoft Copilot Agent CLI - Interact with your Copilot Studio agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start interactive chat session
  python cli.py

  # Send a single message
  python cli.py --message "What is the weather today?"

  # Send multiple messages
  python cli.py --message "Hello" --message "Tell me a joke"

  # Show configuration
  python cli.py --config

  # Use a different config file
  python cli.py --config-file /path/to/config.yaml
        """
    )

    parser.add_argument(
        '-m', '--message',
        action='append',
        help='Send a message to the agent. Can be specified multiple times.'
    )

    parser.add_argument(
        '--config',
        action='store_true',
        help='Display current configuration and exit'
    )

    parser.add_argument(
        '--config-file',
        help='Path to config.yaml file (default: ./config.yaml)'
    )


    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Start interactive chat mode (default if no other options specified)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    try:
        # Load configuration
        if args.verbose:
            print(f"Loading configuration from: {args.config_file or 'config.yaml'}")

        config = CopilotConfig(config_path=args.config_file)

        # Display configuration if requested
        if args.config:
            config.display()
            return 0

        # Initialize client
        client = CopilotAgentClient(config=config)

        # Send single/multiple messages
        if args.message:
            print(f"\nConnecting to {config.agent.name}...")

            if len(args.message) == 1:
                # Single message
                print(f"\nYou: {args.message[0]}")
                response = client.send_message(args.message[0])
                print(f"\n{config.agent.name}: {response}\n")
            else:
                # Multiple messages (with conversation context)
                print(f"\nSending {len(args.message)} messages...\n")
                responses = client.send_messages(args.message)
                for msg, resp in zip(args.message, responses):
                    print(f"You: {msg}")
                    print(f"{config.agent.name}: {resp}\n")

            return 0

        # Start interactive chat (default)
        client.chat_loop()
        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!\n")
        return 130

    except Exception as e:
        print(f"\nError: {e}\n", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
