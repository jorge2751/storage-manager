"""Utilities for visualizing data in the terminal."""

import os
from rich.panel import Panel
from rich.align import Align

def create_size_chart(sizes_dict):
    """Create a bar chart visualization of directory sizes."""
    if not sizes_dict:
        return Panel(Align.center("[yellow]Processing...[/yellow]"))
    
    max_size = max(sizes_dict.values()) if sizes_dict else 1
    max_label_length = max(len(os.path.dirname(path)) for path in sizes_dict.keys()) if sizes_dict else 0
    
    chart = ""
    for path, size in sorted(sizes_dict.items(), key=lambda x: x[1], reverse=True):
        label = os.path.dirname(path)
        size_formatted = format_size(size)
        bar_width = int((size / max_size) * 40)  # 40 chars max width
        bar = "█" * bar_width + "░" * (40 - bar_width)
        chart += f"{label:<{max_label_length}} │ [green]{bar}[/green] {size_formatted}\n"
    
    return Panel(
        chart,
        title="[bold blue]Node Modules Size Distribution[/bold blue]",
        border_style="blue"
    )
