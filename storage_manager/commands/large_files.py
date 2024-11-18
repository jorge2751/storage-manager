"""Command for finding and managing large files."""

import os
import mimetypes
from collections import defaultdict
from datetime import datetime
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from tqdm import tqdm

from storage_manager.utils.size_utils import format_size

console = Console()

def get_file_type(filepath):
    """Get the file type category based on mime type."""
    mime_type, _ = mimetypes.guess_type(filepath)
    if mime_type is None:
        return "Unknown"
    
    category = mime_type.split('/')[0]
    if category in ['video', 'audio', 'image', 'text']:
        return category.capitalize()
    elif 'application' in category:
        if 'pdf' in mime_type:
            return "Document"
        elif any(x in mime_type for x in ['zip', 'tar', 'gzip', 'x-7z', 'rar']):
            return "Archive"
        elif any(x in mime_type for x in ['javascript', 'json', 'xml', 'yaml']):
            return "Code"
    return "Other"

def create_type_chart(type_sizes):
    """Create a bar chart visualization of file types and their sizes."""
    if not type_sizes:
        return Panel(Align.center("[yellow]Processing...[/yellow]"))
    
    max_size = max(type_sizes.values()) if type_sizes else 1
    max_label_length = max(len(type_name) for type_name in type_sizes.keys()) if type_sizes else 0
    
    chart = ""
    for file_type, size in sorted(type_sizes.items(), key=lambda x: x[1], reverse=True):
        bar_width = int((size / max_size) * 40)  # 40 chars max width
        bar = "█" * bar_width + "░" * (40 - bar_width)
        chart += f"{file_type:<{max_label_length}} │ [green]{bar}[/green] {format_size(size)}\n"
    
    return Panel(
        chart,
        title="[bold blue]Storage Usage by File Type[/bold blue]",
        border_style="blue"
    )

def find_large_files(directory, min_size_mb, ignore_patterns=None):
    """Find files larger than the specified size."""
    min_size = min_size_mb * 1024 * 1024  # Convert MB to bytes
    large_files = []
    type_sizes = defaultdict(int)
    
    ignore_patterns = ignore_patterns or [
        'node_modules',
        '.git',
        '.venv',
        'venv',
        'env',
        '__pycache__'
    ]
    
    def should_ignore(path):
        return any(pattern in path for pattern in ignore_patterns)
    
    # First, count total files for progress bar
    total_files = sum(len(files) for _, _, files in os.walk(directory) if not should_ignore(_))
    
    with Live(create_type_chart(type_sizes), refresh_per_second=4) as live:
        with tqdm(total=total_files, desc="Scanning files", unit="files") as pbar:
            for root, _, files in os.walk(directory):
                if should_ignore(root):
                    continue
                    
                for filename in files:
                    pbar.update(1)
                    filepath = os.path.join(root, filename)
                    
                    try:
                        size = os.path.getsize(filepath)
                        if size >= min_size:
                            file_type = get_file_type(filepath)
                            type_sizes[file_type] += size
                            large_files.append((
                                filepath,
                                size,
                                file_type,
                                datetime.fromtimestamp(os.path.getmtime(filepath))
                            ))
                            live.update(create_type_chart(type_sizes))
                    except (OSError, FileNotFoundError):
                        continue
    
    return large_files, type_sizes

@click.command()
@click.argument('directory', type=click.Path(exists=True), default=os.path.expanduser('~'))
@click.option('--min-size', '-s', type=int, default=100, help='Minimum file size in MB (default: 100)')
@click.option('--delete', is_flag=True, help='Enable deletion of selected files')
@click.option('--type', '-t', help='Filter by file type (e.g., Video, Image, Document)')
def find_large(directory, min_size, delete, type):
    """Find files larger than specified size (in MB) in the given directory."""
    console.print(f"\n[bold blue]Scanning for files larger than {min_size}MB in: {directory}[/bold blue]\n")
    
    large_files, type_sizes = find_large_files(directory, min_size)
    
    if not large_files:
        console.print("[yellow]No large files found.[/yellow]")
        return
    
    # Filter by type if specified
    if type:
        large_files = [f for f in large_files if f[2].lower() == type.lower()]
        if not large_files:
            console.print(f"[yellow]No {type} files found.[/yellow]")
            return
    
    # Create a table to display results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File", style="dim")
    table.add_column("Size", justify="right")
    table.add_column("Type", justify="center")
    table.add_column("Modified Date", justify="right")
    
    total_size = 0
    for filepath, size, file_type, modified_time in sorted(large_files, key=lambda x: x[1], reverse=True):
        total_size += size
        table.add_row(
            os.path.relpath(filepath, directory),
            format_size(size),
            file_type,
            modified_time.strftime("%Y-%m-%d %H:%M")
        )
    
    console.print(table)
    console.print(f"\n[bold green]Total space used by large files: {format_size(total_size)}[/bold green]")
    
    if delete:
        files_to_delete = []
        for filepath, size, _, _ in large_files:
            if click.confirm(f'\nDelete {filepath} ({format_size(size)})?'):
                files_to_delete.append(filepath)
        
        if files_to_delete:
            with tqdm(total=len(files_to_delete), desc="Deleting files", unit="files") as pbar:
                for filepath in files_to_delete:
                    try:
                        os.remove(filepath)
                        pbar.update(1)
                    except Exception as e:
                        console.print(f"[red]✗[/red] Failed to delete {filepath}: {str(e)}")
            
            console.print("\n[bold green]Cleanup completed![/bold green]")
