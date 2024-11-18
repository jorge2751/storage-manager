# Storage Manager CLI

A command-line tool to help manage system storage by cleaning up unnecessary files and directories.

## Features

- **Node Modules Cleanup**: Find and remove unnecessary `node_modules` directories
  - Visual size distribution
  - Interactive deletion
  - Progress tracking
- **Screenshots Cleanup**: Manage old screenshots on your Desktop
  - Find screenshots older than specified days
  - Detailed information about each file
  - Safe deletion with confirmation
- **Large Files Finder**: Find and manage large files consuming disk space
  - Smart file type categorization (Video, Image, Document, etc.)
  - Live storage usage visualization by file type
  - Detailed file information (size, type, modified date)
  - Interactive deletion with confirmation

## Installation

This project uses Poetry for dependency management. To install:

```bash
# Clone the repository
git clone https://github.com/yourusername/storage-manager.git
cd storage-manager

# Install dependencies with Poetry
poetry install

# Activate the virtual environment
poetry shell
```

## Usage

### Clean Node Modules

```bash
# Scan home directory for node_modules
storage-manager clean-node-modules

# Scan specific directory with deletion option
storage-manager clean-node-modules /path/to/directory --delete
```

### Clean Old Screenshots

```bash
# Find screenshots older than 30 days (default)
storage-manager clean-screenshots

# Find screenshots older than 60 days
storage-manager clean-screenshots 60

# Find and delete screenshots older than 30 days
storage-manager clean-screenshots --delete
```

### Find Large Files

```bash
# Find files larger than 100MB (default) in home directory
storage-manager find-large

# Find files larger than 500MB in a specific directory
storage-manager find-large /path/to/dir --min-size 500

# Find and optionally delete large video files
storage-manager find-large --type Video --delete

# Find large files in current directory
storage-manager find-large .
```

## Development

To add a new command:

1. Create a new file in `storage_manager/commands/`
2. Define your command using Click decorators
3. Register it in `storage_manager/cli.py`

Example:
```python
# storage_manager/commands/your_command.py
import click

@click.command()
def your_command():
    """Your command description."""
    pass

# storage_manager/cli.py
from storage_manager.commands.your_command import your_command
cli.add_command(your_command)
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
