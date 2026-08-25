import argparse

def register_subcommand(subparsers):
    parser = subparsers.add_parser("hello", help="Hello custom command plugin test")
    parser.add_argument("--name", default="World", help="Name to greet")
    parser.set_defaults(func=run_hello)

def run_hello(args):
    print(f"Hello, {args.name}! This custom command is running from a dynamic plugin file.")
    return 0
