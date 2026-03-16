"""
Sync Manager
Git 同步管理
"""

import subprocess
import os
import re
from datetime import datetime
from typing import Dict, Any

from .models import SyncStatus


class SyncManager:
    """同步管理器"""
    
    def __init__(self, storage):
        self.storage = storage
        self.repo_dir = storage.memory_dir.parent  # 工作区根目录
    
    def sync(self) -> SyncStatus:
        """执行 Git 同步"""
        
        result = SyncStatus()
        result.last_sync = datetime.now().isoformat()
        
        try:
            # 1. Pull 远程更新
            pull_output = self._git_pull()
            result.pulled = self._count_new_entries(pull_output)
            
            # 2. 重新生成索引
            self._regenerate_index()
            
            # 3. 添加变更
            self._git_add()
            
            # 4. 提交
            if self._has_changes():
                self._git_commit()
                result.pushed = self._count_staged_changes()
                
                # 5. Push
                self._git_push()
            
        except Exception as e:
            result.error = str(e)
        
        return result
    
    def _git_pull(self) -> str:
        """拉取远程更新"""
        try:
            result = subprocess.run(
                ["git", "pull", "origin", "main", "--no-edit"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout + result.stderr
        except Exception as e:
            return f"Pull error: {e}"
    
    def _git_add(self):
        """添加变更"""
        try:
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.repo_dir,
                capture_output=True,
                timeout=10
            )
        except:
            pass
    
    def _has_changes(self) -> bool:
        """检查是否有变更需要提交"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=self.repo_dir,
                capture_output=True
            )
            return result.returncode != 0
        except:
            return False
    
    def _git_commit(self):
        """提交变更"""
        try:
            import socket
            hostname = socket.gethostname()
            message = f"sync: {hostname} @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_dir,
                capture_output=True,
                timeout=10
            )
        except:
            pass
    
    def _git_push(self):
        """推送到远程"""
        try:
            subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=self.repo_dir,
                capture_output=True,
                timeout=30
            )
        except:
            pass
    
    def _regenerate_index(self):
        """重新生成索引"""
        script_path = self.storage.memory_dir / "scripts" / "generate-index.sh"
        if script_path.exists():
            try:
                subprocess.run(
                    ["bash", str(script_path)],
                    capture_output=True,
                    timeout=30
                )
            except:
                pass
    
    def _count_new_entries(self, pull_output: str) -> int:
        """统计拉取的新条目数"""
        if "Already up to date" in pull_output or "Already up-to-date" in pull_output:
            return 0
        
        # 统计新增文件数
        new_files = re.findall(r'entries/.*\.md', pull_output)
        return len(new_files)
    
    def _count_staged_changes(self) -> int:
        """统计暂存的变更数"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.stdout.strip():
                return len(result.stdout.strip().split('\n'))
        except:
            pass
        return 0
    
    def get_status(self) -> SyncStatus:
        """获取同步状态"""
        status = SyncStatus()
        status.last_sync = datetime.now().isoformat()
        
        try:
            # 检查是否领先/落后远程
            status.ahead = self._get_commits_ahead()
            status.behind = self._get_commits_behind()
        except:
            pass
        
        return status
    
    def _get_commits_ahead(self) -> int:
        """获取领先远程的提交数"""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", "origin/main..HEAD"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            return int(result.stdout.strip())
        except:
            return 0
    
    def _get_commits_behind(self) -> int:
        """获取落后远程的提交数"""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..origin/main"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            return int(result.stdout.strip())
        except:
            return 0
    
    def init_repo(self, remote_url: str = None) -> bool:
        """初始化 Git 仓库"""
        try:
            # 初始化
            subprocess.run(
                ["git", "init"],
                cwd=self.repo_dir,
                capture_output=True,
                timeout=10
            )
            
            # 配置
            subprocess.run(
                ["git", "config", "user.email", "memory@twin.ai"],
                cwd=self.repo_dir,
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Twin Memory"],
                cwd=self.repo_dir,
                capture_output=True
            )
            
            # 添加远程
            if remote_url:
                # 检查是否已有 remote
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=self.repo_dir,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    subprocess.run(
                        ["git", "remote", "add", "origin", remote_url],
                        cwd=self.repo_dir,
                        capture_output=True
                    )
            
            return True
        except:
            return False
