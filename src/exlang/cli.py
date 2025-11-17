# ============================================================
# exlang.cli: command-line interface
# ============================================================

import sys
import json
from pathlib import Path

import click

from . import __version__
from .io_utils import compile_file, validate_file


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    EXLang: A concise language for Excel generation.
    
    Compile EXLANG markup to Excel workbooks with deterministic output.
    
    \b
    Examples:
      exlang compile report.xlang -o report.xlsx
      exlang validate schema.xlang
      exlang --version
    """
    pass


@cli.command()
@click.argument('input_file', type=click.Path(dir_okay=False))
@click.option('-o', '--output', default=None,
              type=click.Path(dir_okay=False),
              help='Output Excel file path (.xlsx)')
@click.option('-f', '--force', is_flag=True,
              help='Overwrite output file if it exists')
@click.option('-v', '--verbose', is_flag=True,
              help='Verbose output')
def compile(input_file, output, force, verbose):
    """
    Compile EXLANG file to Excel workbook.
    
    \b
    Examples:
      exlang compile data.xlang -o data.xlsx
      exlang compile report.xlang -o report.xlsx --force
      exlang compile input.xlang -o output.xlsx --verbose
    """
    # Generate default output path if not provided
    if output is None:
        input_path = Path(input_file)
        output = str(input_path.with_suffix('.xlsx'))
    
    output_path = Path(output)
    
    # Check if output exists
    if output_path.exists() and not force:
        click.secho(
            f"Error: Output file '{output}' already exists. Use --force to overwrite.",
            fg='red', err=True
        )
        sys.exit(2)
    
    # Compile
    try:
        if verbose:
            click.echo(f"Compiling: {input_file}")
        
        compile_file(input_file, output)
        
        if verbose:
            click.echo(f"Compiled: {output}")
            click.echo(f"Size: {output_path.stat().st_size} bytes")
        
        click.secho(f"✓ Successfully compiled to {output}", fg='green')
        
    except FileNotFoundError:
        click.secho(f"Error: Input file '{input_file}' not found.", fg='red', err=True)
        sys.exit(1)
    
    except ValueError as e:
        click.secho("Validation error:", fg='red', err=True)
        click.echo(str(e), err=True)
        sys.exit(3)
    
    except Exception as e:
        click.secho(f"Error: {type(e).__name__}: {e}", fg='red', err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('input_files', nargs=-1, required=True,
                type=click.Path(dir_okay=False))
@click.option('--format', 'output_format', 
              type=click.Choice(['text', 'json'], case_sensitive=False), 
              default='text', 
              help='Output format (text or json)')
@click.option('-v', '--verbose', is_flag=True, 
              help='Verbose output')
def validate(input_files, output_format, verbose):
    """
    Validate one or more EXLANG files.
    
    \b
    Examples:
      exlang validate file.xlang
      exlang validate file1.xlang file2.xlang file3.xlang
      exlang validate *.xlang --format json
    """
    all_valid = True
    file_not_found = False
    results = []
    
    for input_file in input_files:
        if verbose:
            click.echo(f"Validating: {input_file}")
        
        try:
            is_valid, errors = validate_file(input_file)
            
            if not is_valid:
                all_valid = False
            
            if output_format == 'json':
                results.append({
                    'file': str(input_file),
                    'valid': is_valid,
                    'errors': errors
                })
            else:
                # Text format
                if is_valid:
                    click.secho(f"✓ {input_file}: Valid", fg='green')
                else:
                    click.secho(f"✗ {input_file}: Invalid", fg='red')
                    for error in errors:
                        click.echo(f"  - {error}", err=True)
        
        except FileNotFoundError:
            if output_format == 'json':
                results.append({
                    'file': str(input_file),
                    'valid': False,
                    'errors': ['File not found']
                })
            else:
                click.secho(f"Error: {input_file}: File not found", fg='red', err=True)
            file_not_found = True
            all_valid = False
        
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            if output_format == 'json':
                results.append({
                    'file': str(input_file),
                    'valid': False,
                    'errors': [error_msg]
                })
            else:
                click.secho(f"✗ {input_file}: {error_msg}", fg='red', err=True)
            all_valid = False
    
    # Output JSON results if requested
    if output_format == 'json':
        click.echo(json.dumps({
            'results': results,
            'summary': {
                'total': len(input_files),
                'valid': sum(1 for r in results if r['valid']),
                'invalid': sum(1 for r in results if not r['valid'])
            }
        }, indent=2))
    
    # Exit with appropriate code
    if file_not_found:
        sys.exit(2)
    elif not all_valid:
        sys.exit(1)
    else:
        sys.exit(0)


def main():
    """Entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
