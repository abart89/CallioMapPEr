"""Commands for saved-result translation, annotation templates and RDF queries."""
import argparse
import csv
from importlib.resources import files
from pathlib import Path
import sys
import yaml
from rdflib import Dataset
from calliomapper.translator import Translator, DEFAULT_GROUPS


def main(argv=None):
    parser = argparse.ArgumentParser(description="Represent a saved Calliope modelling exercise using OntoCal.")
    commands = parser.add_subparsers(dest="command", required=True)
    translate = commands.add_parser("translate", help="Read a solved CSV export without running Calliope.")
    translate.add_argument("results_directory", type=Path)
    translate.add_argument("--out", type=Path, required=True)
    translate.add_argument("--annotations", type=Path)
    translate.add_argument("--groups", nargs="+", choices=sorted(DEFAULT_GROUPS))
    translate.add_argument("--time-points", type=Path, help="YAML list selecting individual saved timestep values.")
    translate.add_argument("--namespace", help="An identifier namespace controlled by the graph producer.")
    translate.add_argument("--identity-file", type=Path, help="Reuse the namespace in this CallioMapper manifest.")
    template = commands.add_parser("init-annotations", help="Write an empty annotation template.")
    template.add_argument("--out", type=Path, default=Path("annotations.yaml"))
    query = commands.add_parser("query", help="Run a documented query and write its actual answers as CSV.")
    query.add_argument("graph_files", nargs="+", type=Path)
    query.add_argument("--preset", required=True)
    query.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "translate":
            selections = yaml.safe_load(args.time_points.read_text()) if args.time_points else None
            translator = Translator(args.results_directory, annotations=args.annotations, groups=args.groups,
                                    time_points=selections, namespace=args.namespace, identity_file=args.identity_file)
            translator.save(args.out)
            print(f"Wrote {args.out}; SHACL validation passed.")
            print(f"Details and omissions: {args.out}.report.json")
            if not translator.report["real_fixture_tested_version"]:
                print("This saved-file format has not yet been verified against a genuine saved acceptance example.", file=sys.stderr)
        elif args.command == "init-annotations":
            with args.out.open("x") as output:
                output.write(files("calliomapper").joinpath("templates/annotations.yaml").read_text())
            print(f"Wrote {args.out}")
        else:
            from calliomapper.queries import run_query, QUERY_REQUIREMENTS
            dataset = Dataset(default_union=True)
            for path in args.graph_files:
                dataset.parse(str(path), format="nquads")
            result = run_query(dataset, args.preset)
            stream = args.out.open("w", newline="") if args.out else sys.stdout
            try:
                writer = csv.writer(stream)
                writer.writerow(result.vars)
                count = 0
                for row in result:
                    writer.writerow([str(value) if value is not None else "" for value in row])
                    count += 1
            finally:
                if args.out:
                    stream.close()
            requirement = QUERY_REQUIREMENTS.get(args.preset.lower().replace("-", ""), "")
            print(f"{count} answer rows. {requirement}", file=sys.stderr)
        return 0
    except (ValueError, OSError, yaml.YAMLError) as error:
        print(f"CallioMapper: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
