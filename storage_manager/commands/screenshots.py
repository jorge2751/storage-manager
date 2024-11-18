"""Command for cleaning up old screenshots."""

import os
import re
from datetime import datetime
import click
from rich.console import Console
from rich.table import Table
from tqdm import tqdm

from storage_manager.utils.size_utils import format_size

console = Console()

def is_screenshot(filename):
    """Check if a file is a screenshot based on common screenshot naming patterns."""
    patterns = [
        r"Screenshot \d{4}-\d{2}-\d{2}.*\.png",  # macOS Ventura pattern
        r"Screen Shot \d{4}-\d{2}-\d{2}.*\.png",  # older macOS pattern
        r"Screenshot.*\.png",                      # generic screenshot pattern
        r"Screen Recording.*\.mov"                 # screen recordings
    ]
    return any(re.match(pattern, filename) for pattern in patterns)

def find_old_screenshots(directory, days_old):
    """Find screenshots older than specified days."""
    now = datetime.now()
    old_files = []
    total_size = 0
    
    with tqdm(total=len(os.listdir(directory)), desc="Scanning files", unit="files") as pbar:
        for filename in os.listdir(directory):
            pbar.update(1)
            filepath = os.path.join(directory, filename)
            
            if not os.path.isfile(filepath):
                continue
                
            if is_screenshot(filename):
                modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                age = now - modified_time
                
                if age.days > days_old:
                    size = os.path.getsize(filepath)
                    old_files.append((filepath, size, modified_time))
                    total_size += size
    
    return old_files, total_size

@click.command()
@click.argument('days', type=int, default=30)
@click.option('--delete', is_flag=True, help='Delete found screenshots')
def clean_screenshots(days, delete):
    """Find and optionally delete screenshots older than specified days."""
    desktop_path = os.path.expanduser("~/Desktop")
    console.print(f"\n[bold blue]Scanning for screenshots older than {days} days on Desktop[/bold blue]\n")
    
    old_files, total_size = find_old_screenshots(desktop_path, days)
    
    if not old_files:
        console.print("[yellow]No old screenshots found.[/yellow]")
        return
        
    # Create a table to display results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Screenshot", style="dim")
    table.add_column("Age (days)", justify="right")
    table.add_column("Size", justify="right")
    table.add_column("Modified Date", justify="right")
    
    now = datetime.now()
    for filepath, size, modified_time in sorted(old_files, key=lambda x: x[1], reverse=True):
        age = now - modified_time
        table.add_row(
            os.path.basename(filepath),
            str(age.days),
            format_size(size),
            modified_time.strftime("%Y-%m-%d %H:%M")
        )
    
    console.print(table)
    console.print(f"\n[bold green]Total space used by old screenshots: {format_size(total_size)}[/bold green]")
    
    if delete and old_files:
        if click.confirm('\nDo you want to delete these screenshots?'):
            with tqdm(total=len(old_files), desc="Deleting screenshots", unit="files") as pbar:
                for filepath, _, _ in old_files:
                    try:
                        os.remove(filepath)
                        pbar.update(1)
                    except Exception as e:
                        console.print(f"[red]✗[/red] Failed to delete {filepath}: {str(e)}")
            
            console.print("\n[bold green]Cleanup completed![/bold green]")
