"""
Tests for the FileManager class.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from file_agent.file_manager import FileManager


class TestFileManager:
    """FileManager测试类。"""
    
    def setup_method(self):
        """每个测试方法前的设置。"""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir) / "workspace"
        self.backup_dir = Path(self.temp_dir) / "backups"
        
        self.file_manager = FileManager(
            workspace=str(self.workspace),
            backup_enabled=True
        )
        self.file_manager.backup_dir = self.backup_dir
    
    def teardown_method(self):
        """每个测试方法后的清理。"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_file(self):
        """测试文件创建。"""
        result = self.file_manager.create_file("test.txt", "Hello, World!")
        
        assert result["success"] is True
        assert "test.txt" in result["message"]
        
        # 验证文件确实被创建
        file_path = self.workspace / "test.txt"
        assert file_path.exists()
        assert file_path.read_text() == "Hello, World!"
    
    def test_read_file(self):
        """测试文件读取。"""
        # 先创建一个文件
        test_content = "Test content for reading"
        self.file_manager.create_file("read_test.txt", test_content)
        
        # 读取文件
        result = self.file_manager.read_file("read_test.txt")
        
        assert result["success"] is True
        assert result["content"] == test_content
        assert "size" in result
        assert "modified" in result
    
    def test_read_nonexistent_file(self):
        """测试读取不存在的文件。"""
        result = self.file_manager.read_file("nonexistent.txt")
        
        assert result["success"] is False
        assert "not found" in result["message"].lower()
    
    def test_write_file(self):
        """测试文件写入。"""
        content = "New content"
        result = self.file_manager.write_file("write_test.txt", content)
        
        assert result["success"] is True
        
        # 验证内容
        read_result = self.file_manager.read_file("write_test.txt")
        assert read_result["content"] == content
    
    def test_append_file(self):
        """测试文件追加。"""
        # 先创建文件
        self.file_manager.create_file("append_test.txt", "Initial content")
        
        # 追加内容
        result = self.file_manager.write_file("append_test.txt", "\nAppended content", append=True)
        
        assert result["success"] is True
        
        # 验证内容
        read_result = self.file_manager.read_file("append_test.txt")
        assert "Initial content" in read_result["content"]
        assert "Appended content" in read_result["content"]
    
    def test_delete_file(self):
        """测试文件删除。"""
        # 先创建文件
        self.file_manager.create_file("delete_test.txt", "To be deleted")
        
        # 删除文件
        result = self.file_manager.delete_file("delete_test.txt")
        
        assert result["success"] is True
        assert "backup" in result  # 应该有备份信息
        
        # 验证文件被删除
        file_path = self.workspace / "delete_test.txt"
        assert not file_path.exists()
    
    def test_move_file(self):
        """测试文件移动。"""
        # 先创建文件
        content = "Content to move"
        self.file_manager.create_file("source.txt", content)
        
        # 移动文件
        result = self.file_manager.move_file("source.txt", "destination.txt")
        
        assert result["success"] is True
        
        # 验证源文件不存在，目标文件存在
        source_path = self.workspace / "source.txt"
        dest_path = self.workspace / "destination.txt"
        
        assert not source_path.exists()
        assert dest_path.exists()
        assert dest_path.read_text() == content
    
    def test_copy_file(self):
        """测试文件复制。"""
        # 先创建文件
        content = "Content to copy"
        self.file_manager.create_file("original.txt", content)
        
        # 复制文件
        result = self.file_manager.copy_file("original.txt", "copy.txt")
        
        assert result["success"] is True
        
        # 验证两个文件都存在且内容相同
        original_path = self.workspace / "original.txt"
        copy_path = self.workspace / "copy.txt"
        
        assert original_path.exists()
        assert copy_path.exists()
        assert original_path.read_text() == copy_path.read_text() == content
    
    def test_create_directory(self):
        """测试目录创建。"""
        result = self.file_manager.create_directory("test_dir")
        
        assert result["success"] is True
        
        # 验证目录被创建
        dir_path = self.workspace / "test_dir"
        assert dir_path.exists()
        assert dir_path.is_dir()
    
    def test_list_files(self):
        """测试文件列表。"""
        # 创建一些测试文件和目录
        self.file_manager.create_file("file1.txt", "content1")
        self.file_manager.create_file("file2.py", "content2")
        self.file_manager.create_directory("subdir")
        
        # 列出文件
        result = self.file_manager.list_files()
        
        assert result["success"] is True
        assert result["total_files"] == 2
        assert result["total_directories"] == 1
        
        # 检查文件名
        file_names = [f["name"] for f in result["files"]]
        assert "file1.txt" in file_names
        assert "file2.py" in file_names
        
        # 检查目录名
        dir_names = [d["name"] for d in result["directories"]]
        assert "subdir" in dir_names
    
    def test_list_files_with_pattern(self):
        """测试带模式的文件列表。"""
        # 创建不同类型的文件
        self.file_manager.create_file("test1.txt", "content")
        self.file_manager.create_file("test2.py", "content")
        self.file_manager.create_file("readme.md", "content")
        
        # 只列出.txt文件
        result = self.file_manager.list_files(pattern="*.txt")
        
        assert result["success"] is True
        assert result["total_files"] == 1
        assert result["files"][0]["name"] == "test1.txt"
