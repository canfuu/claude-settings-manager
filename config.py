"""
Configuration constants for Claude Settings Manager
"""
import os
import json
from pathlib import Path

# Config file location (stores user preferences)
CONFIG_DIR = Path.home() / ".claude-settings-manager"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default settings
DEFAULT_CLAUDE_DIR = ""  # Empty means use ~/.claude

# Default configuration
DEFAULT_CONFIG = {
    "claude_dir": DEFAULT_CLAUDE_DIR
}

# Claude settings directory (will be loaded from config)
_claude_dir = None
_settings_file = None
_settings_file_prefix = "settings-"


def load_config() -> dict:
    """Load configuration from config file"""
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            # Ensure all default keys exist
            for key, value in DEFAULT_CONFIG.items():
                if key not in config_data:
                    config_data[key] = value
            return config_data
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()


def save_config(config_data: dict) -> bool:
    """Save configuration to config file"""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False


def get_claude_dir() -> Path:
    """Get the Claude directory from config or default"""
    global _claude_dir, _settings_file

    if _claude_dir is None:
        config_data = load_config()
        claude_dir = config_data.get("claude_dir", "")
        if claude_dir and claude_dir.strip():
            _claude_dir = Path(claude_dir).expanduser().resolve()
        else:
            _claude_dir = Path.home() / ".claude"
        _settings_file = _claude_dir / "settings.json"

    return _claude_dir


def set_claude_dir(claude_dir: str) -> bool:
    """Set the Claude directory and save to config"""
    global _claude_dir, _settings_file

    config_data = load_config()
    config_data["claude_dir"] = claude_dir

    if save_config(config_data):
        # Update the cached paths
        if claude_dir and claude_dir.strip():
            _claude_dir = Path(claude_dir).expanduser().resolve()
        else:
            _claude_dir = Path.home() / ".claude"
        _settings_file = _claude_dir / "settings.json"
        return True
    return False


def get_settings_file() -> Path:
    """Get the settings file path"""
    global _settings_file
    if _settings_file is None:
        get_claude_dir()  # This will initialize _settings_file
    return _settings_file


# Initialize paths on module load
CLAUDE_DIR = get_claude_dir()
SETTINGS_FILE = get_settings_file()
SETTINGS_FILE_PREFIX = _settings_file_prefix

# Ensure directories exist
CLAUDE_DIR.mkdir(exist_ok=True)

# UI Constants
WINDOW_TITLE = "Claude 配置管理器"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 500

# Colors (Minimalist theme)
BG_COLOR = "#f5f5f5"          # Light gray background
FG_COLOR = "#333333"          # Dark gray text
TREE_BG_COLOR = "#ffffff"     # White tree background
TREE_SELECT_COLOR = "#e8f4f8" # Light blue selection
ACTIVE_COLOR = "#4a90e2"      # Blue for active indicator
BUTTON_COLOR = "#666666"      # Gray buttons
SUCCESS_COLOR = "#27ae60"     # Green for success
ERROR_COLOR = "#e74c3c"       # Red for errors

# Treeview columns
TREE_COLUMNS = ("filename", "active")
TREE_HEADING_FILENAME = "配置名称"
TREE_HEADING_ACTIVE = "状态"
TREE_COLUMN_WIDTH_FILENAME = 350
TREE_COLUMN_WIDTH_ACTIVE = 80

# Active label
ACTIVE_LABEL = "✓ 激活"
INACTIVE_LABEL = ""

# JSON Editor
JSON_FONT_FAMILY = "Consolas"
JSON_FONT_SIZE = 10
