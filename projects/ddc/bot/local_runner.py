"""
로컬 실행 제어 모듈
작업 중에만 로컬에서 봇을 실행하고, Git 연동 후에는 자동 종료
"""

import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path


class LocalBotRunner:
    """
    로컬에서 봇을 실행하는 워크플로우 관리자
    
    워크플로우:
    1. Git 상태 확인 (uncommitted changes 여부)
    2. 작업 중이면 봇 실행 + 모니터링
    3. Git push 완료되면 자동 종료
    4. 서버에서 봇이 자동으로 시작됨
    """
    
    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path) if repo_path else Path(__file__).parent.parent.parent
        self.git_state_file = self.repo_path / ".bot_local_state"
        
    def get_git_status(self) -> dict:
        """
        현재 Git 상태 확인
        
        Returns:
            {
                "is_clean": bool,           # 변경사항 없음
                "uncommitted_files": list,   # 커밋되지 않은 파일 목록
                "unpushed_commits": int,     # push되지 않은 커밋 수
                "last_commit_hash": str,     # 마지막 커밋 해시
                "last_commit_time": str,     # 마지막 커밋 시간
            }
        """
        try:
            # 변경사항 확인
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            uncommitted_files = [
                line.strip() for line in status_result.stdout.strip().split("\n")
                if line.strip()
            ]
            
            # unpushed 커밋 확인
            unpushed_result = subprocess.run(
                ["git", "log", "@{u}..", "--oneline"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            unpushed_commits = len([
                line for line in unpushed_result.stdout.strip().split("\n")
                if line.strip()
            ])
            
            # 마지막 커밋 정보
            last_commit_result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%ci"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            last_commit_parts = last_commit_result.stdout.strip().split("|")
            
            return {
                "is_clean": len(uncommitted_files) == 0,
                "uncommitted_files": uncommitted_files,
                "unpushed_commits": unpushed_commits,
                "last_commit_hash": last_commit_parts[0] if last_commit_parts else "",
                "last_commit_time": last_commit_parts[1] if len(last_commit_parts) > 1 else "",
            }
        except Exception as e:
            print(f"⚠️  Git 상태 확인 실패: {e}")
            return {
                "is_clean": False,
                "uncommitted_files": [],
                "unpushed_commits": 0,
                "last_commit_hash": "",
                "last_commit_time": "",
            }
    
    def should_run_locally(self) -> tuple[bool, str]:
        """
        로컬에서 봇을 실행해야 하는지 결정
        
        Returns:
            (should_run: bool, reason: str)
        """
        git_status = self.get_git_status()
        
        # 변경사항이 있으면 → 작업 중 → 로컬 실행 허용
        if not git_status["is_clean"]:
            return True, f"작업 중 (변경사항 {len(git_status['uncommitted_files'])}개)"
        
        # unpushed 커밋이 있으면 → 아직 Git 연동 전 → 로컬 실행 허용
        if git_status["unpushed_commits"] > 0:
            return True, f"커밋 {git_status['unpushed_commits']}개 push 대기 중"
        
        # 모든 변경사항이 push됨 → Git 연동 완료 → 서버에서 실행
        return False, "Git 연동 완료 (서버에서 실행 중)"
    
    def save_local_state(self, commit_hash: str):
        """로컬 실행 상태 저장"""
        state = {
            "commit_hash": commit_hash,
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }
        with open(self.git_state_file, "w") as f:
            f.write(str(state))
    
    def check_should_stop(self) -> tuple[bool, str]:
        """
        봇을 종료해야 하는지 확인 (주기적으로 호출)
        
        Returns:
            (should_stop: bool, reason: str)
        """
        git_status = self.get_git_status()
        
        # 변경사항이 push됨 → 종료
        if git_status["is_clean"] and git_status["unpushed_commits"] == 0:
            return True, "Git push 완료 감지 → 로컬 봇 종료 (서버에서 실행됨)"
        
        return False, ""
    
    def print_workflow_guide(self):
        """워크플로우 가이드 출력"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                    🔄 로컬 개발 워크플로우                        ║
╠══════════════════════════════════════════════════════════════════╣
║  1. 코드 수정 → 로컬에서 봇 테스트                                ║
║  2. git add .                                                    ║
║  3. git commit -m "작업 내용"                                    ║
║  4. git push origin main  ← Push 후 자동으로 봇 종료됨           ║
║  5. 서버에서 봇 자동 실행 (GitHub Actions)                        ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    
    def validate_and_proceed(self) -> bool:
        """
        로컬 실행 유효성 검사 및 진행 결정
        
        Returns:
            True: 계속 진행
            False: 종료
        """
        should_run, reason = self.should_run_locally()
        git_status = self.get_git_status()
        
        print("=" * 70)
        print("🤖 로컬 봇 실행 검증")
        print("=" * 70)
        print(f"\n📊 Git 상태:")
        print(f"   - 변경사항: {len(git_status['uncommitted_files'])}개")
        print(f"   - Push 대기 커밋: {git_status['unpushed_commits']}개")
        print(f"   - 마지막 커밋: {git_status['last_commit_hash'][:8] if git_status['last_commit_hash'] else 'N/A'}")
        print()
        
        if not should_run:
            print(f"❌ {reason}")
            print("\n💡 해결 방법:")
            print("   • 코드 수정 후 커밋/푸시하기 전까지 로컬에서 실행 가능")
            print("   • 또는 .env에 WORK_MODE=DEVELOPMENT 추가")
            print("=" * 70)
            return False
        
        print(f"✅ {reason}")
        print("\n📝 참고: Git push 완료 후 자동으로 종료됩니다")
        print("=" * 70)
        
        self.print_workflow_guide()
        
        # 상태 저장
        self.save_local_state(git_status["last_commit_hash"])
        
        return True
    
    def monitor_and_stop(self, check_interval: int = 10):
        """
        Git 상태를 모니터링하고 push 완료 시 종료
        
        Args:
            check_interval: Git 상태 확인 간격 (초)
        """
        print(f"\n🔍 Git 상태 모니터링 시작 (체크 간격: {check_interval}초)")
        print("   Push 완료되면 자동으로 종료됩니다...")
        print("   (Ctrl+C로 수동 종료 가능)")
        print()
        
        try:
            while True:
                time.sleep(check_interval)
                
                should_stop, reason = self.check_should_stop()
                if should_stop:
                    print("\n" + "=" * 70)
                    print(f"🛑 {reason}")
                    print("=" * 70)
                    print("\n⏳ 3초 후 자동 종료...")
                    time.sleep(3)
                    sys.exit(0)
                    
        except KeyboardInterrupt:
            print("\n\n👤 사용자가 수동 종료했습니다.")
            sys.exit(0)


# 편의 함수
def check_local_run_permission() -> bool:
    """로컬 실행 권한 확인 (간편 함수)"""
    runner = LocalBotRunner()
    return runner.validate_and_proceed()


def start_git_monitor(check_interval: int = 10):
    """Git 모니터링 시작 (별도 스레드에서 실행)"""
    import threading
    runner = LocalBotRunner()
    monitor_thread = threading.Thread(
        target=runner.monitor_and_stop,
        args=(check_interval,),
        daemon=True
    )
    monitor_thread.start()
    return monitor_thread


if __name__ == "__main__":
    # 테스트
    runner = LocalBotRunner()
    runner.validate_and_proceed()
