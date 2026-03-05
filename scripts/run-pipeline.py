#!/usr/bin/env python3
"""
OpenClaw SGP Business Pipeline - CLI Entry Point
Research brands and extract Singapore legal entity information
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root (parent of scripts/) to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orchestrator import OpenClawOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw SGP Business Pipeline - Research and extract Singapore entity information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run-pipeline.py "Grab Technologies"
  python3 run-pipeline.py --input "https://grab.com" --agent sgp-entity-finder
  python3 run-pipeline.py --config ~/.openclaw/config.json "Uber Singapore"
        """
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Brand name, website URL, or Facebook page to research"
    )
    parser.add_argument(
        "--agent",
        default="sgp-entity-finder",
        help="Agent to use (default: sgp-entity-finder)"
    )
    parser.add_argument(
        "--config",
        default=None,
        help="OpenClaw config directory (default: ~/.openclaw)"
    )
    parser.add_argument(
        "--output",
        "-o",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )

    args = parser.parse_args()

    # Validate input
    if not args.input:
        parser.print_help()
        print("\nError: input brand name is required")
        sys.exit(1)

    print("="*70)
    print("OpenClaw SGPBusiness Research Pipeline")
    print("="*70)
    print(f"Input: {args.input}")
    print(f"Agent: {args.agent}")
    print()

    try:
        # Initialize orchestrator
        config_dir = args.config if args.config else None
        if config_dir:
            orchestrator = OpenClawOrchestrator(config_dir)
        else:
            orchestrator = OpenClawOrchestrator()

        # Prepare input data
        input_data = {
            "brand": args.input,
            "perplexica_endpoint": orchestrator.config.get("perplexica_endpoint", "http://localhost:3000")
        }

        # Run the agent
        print(f"[Pipeline] Starting agent: {args.agent}\n")
        result = orchestrator.run_agent(args.agent, input_data)

        # Format and output results
        print("\n" + "="*70)
        print("PIPELINE RESULTS")
        print("="*70)

        if args.output == "json":
            indent = 2 if args.pretty else None
            print(json.dumps(result, indent=indent))
        else:
            # Text format
            print("\nStatus:", result.get("status", "unknown").upper())
            if result.get("status") == "success":
                print("\nExtracted Information:")
                for key, value in result.items():
                    if key not in ["status", "agent", "timestamp", "input", "results"]:
                        # Pretty print the key
                        display_key = key.replace("_", " ").title()
                        print(f"  {display_key}: {value}")
            else:
                print("\nError:", result.get("message", "Unknown error"))
                if result.get("results"):
                    print("\nDebug Info:")
                    for skill, data in result["results"].items():
                        print(f"  {skill}: {data}")

        print("\n" + "="*70)
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
