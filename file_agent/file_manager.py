"""
File management module for the File Agent.
"""

import os
import shutil
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FileManager:
    """文件管理器类，提供文件和目录的基本操作功能。"""
    
    def __init__(self, workspace: str = "./workspace", backup_enabled: bool = True):
        """
        初始化文件管理器。
        
        Args:
            workspace: 工作目录路径
            backup_enabled: 是否启用备份功能
        """
        self.workspace = Path(workspace).resolve()
        self.backup_enabled = backup_enabled
        self.backup_dir = Path("./backups").resolve()
        
        # 确保工作目录和备份目录存在
        self.workspace.mkdir(parents=True, exist_ok=True)
        if self.backup_enabled:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_full_path(self, path: Union[str, Path]) -> Path:
        """获取相对于工作目录的完整路径。"""
        path = Path(path)
        if path.is_absolute():
            return path
        return self.workspace / path
    
    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """为文件创建备份。"""
        if not self.backup_enabled or not file_path.exists():
            return None

        # 确保备份目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name

        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return None
    
    def create_file(self, path: str, content: str = "", encoding: str = "utf-8") -> Dict[str, Any]:
        """
        创建文件。
        
        Args:
            path: 文件路径
            content: 文件内容
            encoding: 文件编码
            
        Returns:
            操作结果字典
        """
        try:
            file_path = self._get_full_path(path)
            
            # 确保父目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 如果文件已存在，创建备份
            if file_path.exists():
                self._create_backup(file_path)
            
            # 写入文件
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.info(f"Created file: {file_path}")
            return {
                "success": True,
                "message": f"File created successfully: {path}",
                "path": str(file_path),
                "size": file_path.stat().st_size
            }
        except Exception as e:
            logger.error(f"Failed to create file {path}: {e}")
            return {
                "success": False,
                "message": f"Failed to create file: {str(e)}",
                "path": path
            }
    
    def read_file(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        读取文件内容。
        
        Args:
            path: 文件路径
            encoding: 文件编码
            
        Returns:
            操作结果字典，包含文件内容
        """
        try:
            file_path = self._get_full_path(path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {path}",
                    "path": path
                }
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            logger.info(f"Read file: {file_path}")
            return {
                "success": True,
                "message": f"File read successfully: {path}",
                "path": str(file_path),
                "content": content,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to read file {path}: {e}")
            return {
                "success": False,
                "message": f"Failed to read file: {str(e)}",
                "path": path
            }

    def write_file(self, path: str, content: str, encoding: str = "utf-8", append: bool = False) -> Dict[str, Any]:
        """
        写入文件内容。

        Args:
            path: 文件路径
            content: 要写入的内容
            encoding: 文件编码
            append: 是否追加模式

        Returns:
            操作结果字典
        """
        try:
            file_path = self._get_full_path(path)

            # 确保父目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 如果文件已存在且不是追加模式，创建备份
            if file_path.exists() and not append:
                self._create_backup(file_path)

            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)

            action = "appended to" if append else "written to"
            logger.info(f"Content {action} file: {file_path}")
            return {
                "success": True,
                "message": f"Content {action} file successfully: {path}",
                "path": str(file_path),
                "size": file_path.stat().st_size
            }
        except Exception as e:
            logger.error(f"Failed to write to file {path}: {e}")
            return {
                "success": False,
                "message": f"Failed to write to file: {str(e)}",
                "path": path
            }

    def delete_file(self, path: str) -> Dict[str, Any]:
        """
        删除文件。

        Args:
            path: 文件路径

        Returns:
            操作结果字典
        """
        try:
            file_path = self._get_full_path(path)

            if not file_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {path}",
                    "path": path
                }

            # 创建备份
            backup_path = self._create_backup(file_path)

            # 删除文件
            file_path.unlink()

            logger.info(f"Deleted file: {file_path}")
            result = {
                "success": True,
                "message": f"File deleted successfully: {path}",
                "path": str(file_path)
            }

            if backup_path:
                result["backup"] = str(backup_path)

            return result
        except Exception as e:
            logger.error(f"Failed to delete file {path}: {e}")
            return {
                "success": False,
                "message": f"Failed to delete file: {str(e)}",
                "path": path
            }

    def move_file(self, src_path: str, dst_path: str) -> Dict[str, Any]:
        """
        移动或重命名文件。

        Args:
            src_path: 源文件路径
            dst_path: 目标文件路径

        Returns:
            操作结果字典
        """
        try:
            src_file = self._get_full_path(src_path)
            dst_file = self._get_full_path(dst_path)

            if not src_file.exists():
                return {
                    "success": False,
                    "message": f"Source file not found: {src_path}",
                    "src_path": src_path
                }

            # 确保目标目录存在
            dst_file.parent.mkdir(parents=True, exist_ok=True)

            # 如果目标文件已存在，创建备份
            if dst_file.exists():
                self._create_backup(dst_file)

            # 移动文件
            shutil.move(str(src_file), str(dst_file))

            logger.info(f"Moved file from {src_file} to {dst_file}")
            return {
                "success": True,
                "message": f"File moved successfully from {src_path} to {dst_path}",
                "src_path": str(src_file),
                "dst_path": str(dst_file)
            }
        except Exception as e:
            logger.error(f"Failed to move file from {src_path} to {dst_path}: {e}")
            return {
                "success": False,
                "message": f"Failed to move file: {str(e)}",
                "src_path": src_path,
                "dst_path": dst_path
            }

    def copy_file(self, src_path: str, dst_path: str) -> Dict[str, Any]:
        """
        复制文件。

        Args:
            src_path: 源文件路径
            dst_path: 目标文件路径

        Returns:
            操作结果字典
        """
        try:
            src_file = self._get_full_path(src_path)
            dst_file = self._get_full_path(dst_path)

            if not src_file.exists():
                return {
                    "success": False,
                    "message": f"Source file not found: {src_path}",
                    "src_path": src_path
                }

            # 确保目标目录存在
            dst_file.parent.mkdir(parents=True, exist_ok=True)

            # 如果目标文件已存在，创建备份
            if dst_file.exists():
                self._create_backup(dst_file)

            # 复制文件
            shutil.copy2(str(src_file), str(dst_file))

            logger.info(f"Copied file from {src_file} to {dst_file}")
            return {
                "success": True,
                "message": f"File copied successfully from {src_path} to {dst_path}",
                "src_path": str(src_file),
                "dst_path": str(dst_file),
                "size": dst_file.stat().st_size
            }
        except Exception as e:
            logger.error(f"Failed to copy file from {src_path} to {dst_path}: {e}")
            return {
                "success": False,
                "message": f"Failed to copy file: {str(e)}",
                "src_path": src_path,
                "dst_path": dst_path
            }

    def create_directory(self, path: str) -> Dict[str, Any]:
        """
        创建目录。

        Args:
            path: 目录路径

        Returns:
            操作结果字典
        """
        try:
            dir_path = self._get_full_path(path)
            dir_path.mkdir(parents=True, exist_ok=True)

            logger.info(f"Created directory: {dir_path}")
            return {
                "success": True,
                "message": f"Directory created successfully: {path}",
                "path": str(dir_path)
            }
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return {
                "success": False,
                "message": f"Failed to create directory: {str(e)}",
                "path": path
            }

    def list_files(self, path: str = ".", pattern: str = "*", recursive: bool = False) -> Dict[str, Any]:
        """
        列出目录中的文件和子目录。

        Args:
            path: 目录路径
            pattern: 文件名模式（支持通配符）
            recursive: 是否递归列出子目录

        Returns:
            操作结果字典，包含文件列表
        """
        try:
            dir_path = self._get_full_path(path)

            if not dir_path.exists():
                return {
                    "success": False,
                    "message": f"Directory not found: {path}",
                    "path": path
                }

            if not dir_path.is_dir():
                return {
                    "success": False,
                    "message": f"Path is not a directory: {path}",
                    "path": path
                }

            files = []
            directories = []

            if recursive:
                items = dir_path.rglob(pattern)
            else:
                items = dir_path.glob(pattern)

            for item in items:
                relative_path = item.relative_to(self.workspace)
                item_info = {
                    "name": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                    "is_file": item.is_file(),
                    "is_directory": item.is_dir()
                }

                if item.is_file():
                    files.append(item_info)
                elif item.is_dir():
                    directories.append(item_info)

            logger.info(f"Listed {len(files)} files and {len(directories)} directories in {dir_path}")
            return {
                "success": True,
                "message": f"Directory listing for: {path}",
                "path": str(dir_path),
                "files": files,
                "directories": directories,
                "total_files": len(files),
                "total_directories": len(directories)
            }
        except Exception as e:
            logger.error(f"Failed to list directory {path}: {e}")
            return {
                "success": False,
                "message": f"Failed to list directory: {str(e)}",
                "path": path
            }
