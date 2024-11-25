"""Main CLI entry point for the storage manager."""

import click

from storage_manager.commands.node_modules import clean_node_modules
from storage_manager.commands.screenshots import clean_screenshots
from storage_manager.commands.large_files import find_large

@click.group()
def cli():
    """Storage Manager CLI - Helps you manage your storage space efficiently."""
    pass

# Register commands
cli.add_command(clean_node_modules)
cli.add_command(clean_screenshots)
cli.add_command(find_large)

if __name__ == '__main__':
    cli()
