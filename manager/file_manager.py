"""
File Manager for Claude Settings Manager
Handles file operations, symlink creation/deletion, and settings management
"""
import os
import json
from pathlib import Path
from typing import List, Tuple, Optional
import config


class FileManager:
    """Manages Claude settings files and symlinks"""

    @staticmethod
    def get_settings_files() -> List[str]:
        """
        Get list of all settings files with settings-*.json pattern in ~/.claude directory

        Returns:
            List of configuration names (the xxx part from settings-xxx.json)
        """
        claude_dir = config.get_claude_dir()
        if not claude_dir.exists():
            return []

        files = []
        for file_path in claude_dir.glob(f"{config.SETTINGS_FILE_PREFIX}*.json"):
            if file_path.is_file() and not file_path.is_symlink():
                # Extract the name after "settings-" prefix
                name = file_path.stem[len(config.SETTINGS_FILE_PREFIX):]
                files.append(name)
        return sorted(files)

    @staticmethod
    def get_active_settings() -> Optional[str]:
        """
        Get the currently active settings name

        Returns:
            Configuration name of active settings (the xxx part from settings-xxx.json),
            or None if no active settings
        """
        settings_file = config.get_settings_file()
        claude_dir = config.get_claude_dir()

        if not settings_file.exists():
            return None

        # Check if it's a symlink
        if not settings_file.is_symlink():
            return None

        # Get the target of the symlink
        target = Path(os.readlink(settings_file))

        # Resolve relative paths
        if not target.is_absolute():
            target = (settings_file.parent / target).resolve()

        # Check if it points to a settings-*.json file in the .claude directory
        try:
            if target.is_relative_to(claude_dir) and target.stem.startswith(config.SETTINGS_FILE_PREFIX):
                # Extract the name after "settings-" prefix
                return target.stem[len(config.SETTINGS_FILE_PREFIX):]
        except (ValueError, AttributeError):
            pass

        return None

    @staticmethod
    def read_settings_file(name: str) -> Optional[dict]:
        """
        Read and parse a settings file

        Args:
            name: Configuration name (the xxx part from settings-xxx.json)

        Returns:
            Dictionary containing settings, or None if file doesn't exist or is invalid
        """
        claude_dir = config.get_claude_dir()
        file_path = claude_dir / f"{config.SETTINGS_FILE_PREFIX}{name}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    @staticmethod
    def write_settings_file(name: str, settings: dict) -> Tuple[bool, Optional[str]]:
        """
        Write settings to a file

        Args:
            name: Configuration name (the xxx part from settings-xxx.json)
            settings: Dictionary containing settings

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        claude_dir = config.get_claude_dir()
        file_path = claude_dir / f"{config.SETTINGS_FILE_PREFIX}{name}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True, None
        except (IOError, TypeError) as e:
            return False, str(e)

    @staticmethod
    def create_settings_file(name: str) -> Tuple[bool, Optional[str]]:
        """
        Create a new empty settings file

        Args:
            name: Configuration name (the xxx part from settings-xxx.json)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not name or not name.strip():
            return False, "配置名称不能为空"

        name = name.strip()
        # Validate name doesn't contain invalid characters
        if '/' in name or '\\' in name or ':' in name:
            return False, "配置名称包含非法字符"

        claude_dir = config.get_claude_dir()
        claude_dir.mkdir(exist_ok=True)

        file_path = claude_dir / f"{config.SETTINGS_FILE_PREFIX}{name}.json"
        if file_path.exists():
            return False, f"配置 '{name}' 已存在"

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2)
            return True, None
        except IOError as e:
            return False, str(e)

    @staticmethod
    def delete_settings_file(name: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a settings file

        Args:
            name: Configuration name (the xxx part from settings-xxx.json)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        claude_dir = config.get_claude_dir()
        file_path = claude_dir / f"{config.SETTINGS_FILE_PREFIX}{name}.json"
        if not file_path.exists():
            return False, f"配置 '{name}' 不存在"

        # Check if this is the currently active settings
        active = FileManager.get_active_settings()
        if active == name:
            # Deactivate first
            FileManager.deactivate_settings()

        try:
            file_path.unlink()
            return True, None
        except IOError as e:
            return False, str(e)

    @staticmethod
    def activate_settings(name: str) -> Tuple[bool, Optional[str]]:
        """
        Activate a settings file by creating a symlink

        Args:
            name: Configuration name (the xxx part from settings-xxx.json)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        claude_dir = config.get_claude_dir()
        settings_file = config.get_settings_file()

        source_file = claude_dir / f"{config.SETTINGS_FILE_PREFIX}{name}.json"
        if not source_file.exists():
            return False, f"配置 '{name}' 不存在"

        # Remove existing settings.json if it exists
        if settings_file.exists():
            try:
                if settings_file.is_symlink():
                    settings_file.unlink()
                else:
                    settings_file.unlink()
            except IOError as e:
                return False, f"删除现有配置文件失败: {e}"

        # Create relative symlink
        try:
            relative_path = os.path.relpath(source_file, claude_dir)
            os.symlink(relative_path, settings_file, target_is_directory=False)
            return True, None
        except (OSError, IOError) as e:
            return False, f"创建符号链接失败: {e}"

    @staticmethod
    def deactivate_settings() -> Tuple[bool, Optional[str]]:
        """
        Deactivate current settings by removing the symlink

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        settings_file = config.get_settings_file()
        if not settings_file.exists():
            return True, None

        try:
            settings_file.unlink()
            return True, None
        except IOError as e:
            return False, f"取消激活失败: {e}"

    @staticmethod
    def get_settings_path(name: str) -> Path:
        """
        Get the full path to a settings file

        Args:
            name: Configuration name (the xxx part from settings-xxx.json)

        Returns:
            Path to the settings file
        """
        claude_dir = config.get_claude_dir()
        return claude_dir / f"{config.SETTINGS_FILE_PREFIX}{name}.json"
