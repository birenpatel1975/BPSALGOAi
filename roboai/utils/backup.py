"""Backup utility for ROBOAi"""

import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Optional


class BackupManager:
    """Manages backups of configuration and data"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(
        self,
        files_to_backup: Optional[List[str]] = None,
        backup_name: Optional[str] = None
    ) -> Path:
        """
        Create a backup of specified files
        
        Args:
            files_to_backup: List of file paths to backup. If None, backs up default files.
            backup_name: Custom backup name. If None, generates timestamp-based name.
        
        Returns:
            Path to the created backup file
        """
        if files_to_backup is None:
            files_to_backup = [
                'config.yaml',
                'data/roboai.db',
                'logs/'
            ]
        
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"roboai_backup_{timestamp}"
        
        backup_path = self.backup_dir / f"{backup_name}.zip"
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_backup:
                path = Path(file_path)
                
                if not path.exists():
                    print(f"Warning: {file_path} does not exist, skipping...")
                    continue
                
                if path.is_file():
                    zipf.write(path, path.name)
                elif path.is_dir():
                    for item in path.rglob('*'):
                        if item.is_file():
                            zipf.write(item, item.relative_to(path.parent))
        
        print(f"Backup created: {backup_path}")
        return backup_path
    
    def restore_backup(self, backup_file: str, restore_dir: str = ".") -> None:
        """
        Restore from a backup file
        
        Args:
            backup_file: Path to the backup file
            restore_dir: Directory to restore to
        """
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        restore_path = Path(restore_dir)
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(restore_path)
        
        print(f"Backup restored from: {backup_path}")
    
    def list_backups(self) -> List[Path]:
        """List all available backups"""
        backups = sorted(
            self.backup_dir.glob('*.zip'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return backups
    
    def delete_old_backups(self, keep_count: int = 10) -> None:
        """
        Delete old backups, keeping only the most recent ones
        
        Args:
            keep_count: Number of recent backups to keep
        """
        backups = self.list_backups()
        
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                backup.unlink()
                print(f"Deleted old backup: {backup}")


def create_backup(backup_name: Optional[str] = None) -> Path:
    """Convenience function to create a backup"""
    manager = BackupManager()
    return manager.create_backup(backup_name=backup_name)


def restore_backup(backup_file: str) -> None:
    """Convenience function to restore a backup"""
    manager = BackupManager()
    manager.restore_backup(backup_file)
