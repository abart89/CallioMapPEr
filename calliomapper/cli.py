"""
Command Line Interface for CallioMapper.

Embodies the "Single-Click" and "Graceful Degradation" philosophy.
"""

import argparse
import sys
from pathlib import Path
from calliomapper.translator import Translator

def main():
    parser = argparse.ArgumentParser(description="CallioMapper: Semantic Energy Model Translation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # `translate` command
    parser_translate = subparsers.add_parser("translate", help="Translate a Calliope solved instance directory to an N-Quads knowledge graph (Core).")
    parser_translate.add_argument("results_directory", type=str, help="Path to the Calliope solve outputs.")
    parser_translate.add_argument("--extension", type=str, help="Path to PROV-O epistemic extension YAML (optional).")
    parser_translate.add_argument("--out", type=str, required=True, help="Output .nq file path.")

    # `init-extension` command
    parser_init = subparsers.add_parser("init-extension", help="Generate a blank epistemic extension template in the current directory.")

    # `query` command
    parser_query = subparsers.add_parser("query", help="Execute a canned SPARQL query against an N-Quads file and export to CSV.")
    parser_query.add_argument("graph_file", type=str, help="Path to the .nq graph file.")
    parser_query.add_argument("--preset", type=str, choices=["installed_capacity", "system_costs"], required=True, help="The canned query to run.")
    parser_query.add_argument("--out", type=str, help="Output CSV path. Defaults to stdout.")

    args = parser.parse_args()

    if args.command == "translate":
        print(f"Translating {args.results_directory}...")
        try:
            t = Translator(model_dir=args.results_directory, extension=args.extension)
            t.save(args.out)
            print(f"Graph successfully written to {args.out}")
        except Exception as e:
            print(f"Translation failed: {e}")
            sys.exit(1)
            
    elif args.command == "init-extension":
        # Placeholder for writing the template
        print("Generated 'epistemic_extension_template.yaml' in the current directory.")
        
    elif args.command == "query":
        print(f"Running '{args.preset}' query against {args.graph_file}...")
        # Placeholder for dispatching to calliomapper.queries
        print(f"Done.")

if __name__ == "__main__":
    main()
