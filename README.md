# Claude Settings Manager

A Windows desktop application for managing Claude AI settings files in the `~/.claude` directory.

## Features

- **File Management**: Create, edit, and delete multiple settings profiles
- **Easy Activation**: Quickly switch between settings profiles via right-click menu
- **JSON Editor**: Built-in JSON editor with validation and formatting
- **Visual Indicators**: Clearly see which settings profile is currently active

## Installation

### Prerequisites

- Python 3.8 or higher

### Development Setup

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Building the Executable

To build a standalone `.exe` file:

```bash
python build.py
```

The executable will be created in the `dist/` directory as `ClaudeSettingsManager.exe`.

## Usage

### Running from Source

```bash
python main.py
```

### Running the Executable

Simply double-click `ClaudeSettingsManager.exe` from the `dist/` directory.

## How It Works

The application manages settings files in `~/.claude/settings/`:

- Each settings profile is stored as a separate `.json` file
- The active profile is linked via a symbolic link: `~/.claude/settings.json` → `~/.claude/settings/<active_profile>.json`
- Claude AI reads from `~/.claude/settings.json`, so switching profiles is as simple as updating the symlink

## Project Structure

```
claude-settings-manager/
├── main.py              # Main entry point
├── config.py            # Configuration constants
├── build.py             # PyInstaller build script
├── requirements.txt     # Python dependencies
├── ui/
│   └── main_window.py   # Main window UI implementation
└── manager/
    ├── file_manager.py  # File operations and symlink management
    └── json_manager.py  # JSON validation and formatting
```

## Features Detail

### Left Panel - File List

- **Add New**: Create a new settings profile
- **Delete**: Remove the selected profile (with confirmation)
- **Right-Click**: Activate or deactivate the selected profile
- **Active Status**: Shows `[Active]` label for the currently active profile

### Right Panel - JSON Editor

- **Edit**: Modify the JSON content of the selected profile
- **Save**: Save changes with automatic JSON validation
- **Format JSON**: Beautify the JSON with proper indentation
- **Validation**: Real-time JSON validation on save

## Troubleshooting

### Symlink Permissions

On Windows, creating symbolic links may require:
- Administrator privileges, OR
- Developer Mode enabled in Windows settings

If you encounter permission issues, try:
1. Running as Administrator, OR
2. Enabling Developer Mode in Settings → Update & Security → For developers

### JSON Validation Errors

The editor validates JSON before saving. Common issues:
- Missing commas between items
- Trailing commas (not allowed in strict JSON)
- Unquoted keys or values
- Comments (not allowed in standard JSON)

## License

MIT License
