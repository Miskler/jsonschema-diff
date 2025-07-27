"""
Command Line Interface for JSON Schema Diff.

This module provides a CLI for comparing JSON schemas from files or stdin.
"""

import json
import sys

import click

from .comparator import compare_schemas
from .config import Config


@click.command()
@click.argument("old_schema_file", type=click.Path(exists=True))
@click.argument("new_schema_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file (default: stdout)")
@click.option("--no-color", is_flag=True, help="Disable colored output")
def main(
    old_schema_file: str, new_schema_file: str, output: str, no_color: bool
) -> None:
    """
    Compare two JSON schema files and display the differences.

    OLD_SCHEMA_FILE: Path to the original schema file
    NEW_SCHEMA_FILE: Path to the new schema file
    """
    try:
        # Load schemas
        with open(old_schema_file, "r", encoding="utf-8") as f:
            old_schema = json.load(f)

        with open(new_schema_file, "r", encoding="utf-8") as f:
            new_schema = json.load(f)

        # Handle no-color option
        if no_color:
            Config.set_use_colors(False)

        # Compare schemas
        result = compare_schemas(old_schema, new_schema)

        # Output result
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(result)
            click.echo(f"Diff written to {output}")
        else:
            click.echo(result)

    except FileNotFoundError as e:
        click.echo(f"Error: File not found - {e}", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON - {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
