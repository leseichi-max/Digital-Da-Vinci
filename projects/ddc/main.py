"""
SHawn-BOT Main Entry Point
Initializes and runs the complete system

🔄 개발 워크플로우:
  1. 로컬에서 작업 중: 봇 실행 가능 (Git 상태 확인)
  2. Git push 완료: 로컬 봇 자동 종료 → 서버에서 실행
"""

import os
import sys
import threading
import uvicorn
import time
from pathlib import Path

# 📁 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 🛡️ 로컬 실행 제어 모듈 임포트
try:
    from ddc.bot.local_runner import LocalBotRunner, check_local_run_permission, start_git_monitor
    LOCAL_RUNNER_AVAILABLE = True
except ImportError:
    LOCAL_RUNNER_AVAILABLE = False
    print("⚠️  local_runner 모듈을 찾을 수 없습니다. 기본 검증을 사용합니다.")

from ddc.brain import Brainstem
from ddc.bot import TelegramBot
from ddc.web.backend.main import app as dashboard_app


def validate_environment():
    """
    실행 환경을 검증합니다.
    
    우선순위:
    1. RUN_MODE=PRODUCTION → 서버 환경 (즉시 실행)
    2. Git 상태 확인 → 작업 중이면 로컬 실행
    3. WORK_MODE=DEVELOPMENT → 개발 모드 (무조건 실행)
    """
    run_mode = os.getenv("RUN_MODE", "")
    work_mode = os.getenv("WORK_MODE", "")
    
    # 1. 서버 환경 확인
    if run_mode == "PRODUCTION":
        print("✅ [PRODUCTION] 서버 환경 확인됨")
        return True
    
    # 2. 강제 개발 모드
    if work_mode == "DEVELOPMENT":
        print("⚠️  [DEVELOPMENT] 개발 모드로 실행합니다")
        print("   Git push 후에도 자동 종료되지 않습니다")
        return True
    
    # 3. Git 기반 로컬 실행 검증
    if LOCAL_RUNNER_AVAILABLE:
        runner = LocalBotRunner()
        return runner.validate_and_proceed()
    else:
        # 기본 경고
        print("=" * 70)
        print("⚠️  [경고] 로컬 환경에서 실행을 시도하고 있습니다.")
        print("=" * 70)
        print()
        print("📌 선택지:")
        print("   [Y] 예, 로컬에서 실행합니다")
        print("   [N] 아니오, 실행을 취소합니다")
        print("=" * 70)
        
        try:
            response = input("\n선택하세요 (Y/N): ").strip().upper()
            if response != 'Y':
                print("\n🛑 실행이 취소되었습니다.")
                sys.exit(0)
            return True
        except KeyboardInterrupt:
            print("\n\n🛑 사용자가 취소했습니다.")
            sys.exit(0)


def start_git_monitor_if_needed():
    """
    Git 상태 모니터링 시작 (로컬 실행 시)
    Push 완료되면 자동 종료
    """
    run_mode = os.getenv("RUN_MODE", "")
    work_mode = os.getenv("WORK_MODE", "")
    
    # 서버 환경이거나 개발 모드면 모니터링 불필요
    if run_mode == "PRODUCTION" or work_mode == "DEVELOPMENT":
        return None
    
    if not LOCAL_RUNNER_AVAILABLE:
        return None
    
    # Git 모니터링 시작 (백그라운드 스레드)
    print("\n🔄 Git push 모니터링 활성화 (push 완료 시 자동 종료)")
    monitor_thread = start_git_monitor(check_interval=10)
    return monitor_thread


# 🧠 신경계 시스템 초기화
try:
    from systems.neural.work_tracker import WorkTracker
    neural_tracker = WorkTracker()
    NEURAL_SYSTEM_AVAILABLE = True
except ImportError:
    NEURAL_SYSTEM_AVAILABLE = False
    neural_tracker = None


def run_dashboard():
    """Run dashboard in specific thread"""
    print("📊 Dashboard Server Starting on port 8000...")
    uvicorn.run(dashboard_app, host="0.0.0.0", port=8000, log_level="error")


def main():
    """Main entry point"""
    # 🛡️ 환경 검증
    if not validate_environment():
        sys.exit(0)
    
    print("🚀 SHawn-BOT v5.3.0 시작 (Integration Mode)...")
    
    # 🧠 신경계 시스템 상태
    if NEURAL_SYSTEM_AVAILABLE:
        print("✅ D-CNS 신경계 시스템 활성화")
    else:
        print("⚠️  D-CNS 신경계 시스템 미로드 (systems/neural 확인 필요)")
    
    # 🔄 Git 모니터링 시작 (로컬 실행 시 자동 종료용)
    git_monitor = start_git_monitor_if_needed()
    
    # 1. Start Dashboard Server (Background)
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    
    # Wait a moment for server to warm up
    time.sleep(1)
    print("✅ Dashboard Active at http://localhost:8000")

    print("📊 D-CNS 신경계 초기화...")
    
    # Initialize brain
    brain = Brainstem()
    print("✅ 뇌간 (Brainstem) 활성화")
    
    # Initialize bot
    bot = TelegramBot(brain=brain)
    print("✅ Telegram 봇 활성화")
    
    print("\n" + "=" * 70)
    print("🤖 봇이 실행 중입니다...")
    
    if git_monitor:
        print("💡 Git push 완료 시 자동으로 종료됩니다")
    
    print("   (Ctrl+C로 수동 종료)")
    print("=" * 70 + "\n")
    
    # Start
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n\n🛑 사용자가 종료했습니다.")
        sys.exit(0)


if __name__ == "__main__":
    main()
