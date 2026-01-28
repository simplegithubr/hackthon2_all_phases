#!/usr/bin/env python3
"""
Todo Application - Entry Point

This is the main entry point for the console-based todo application.
"""
import sys
from src.cli.cli_app import CLIApp


def main():
    """Main entry point for the todo application."""
    try:
        app = CLIApp()
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()