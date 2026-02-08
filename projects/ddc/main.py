"""
SHawn-BOT Main Entry Point
Initializes and runs the complete system
"""

import os
import sys
import threading
import uvicorn
import time
from ddc.brain import Brainstem
from ddc.bot import TelegramBot
from ddc.web.backend.main import app as dashboard_app

# 🛡️ 서버 환경 검증 (로컬 실행 경고)
def validate_server_environment():
    """
    서버 환경을 검증하고, 로컬 실행 시 경고를 표시합니다.
    사용자 확인 후 계속 진행하거나 중단할 수 있습니다.
    """
    run_mode = os.getenv("RUN_MODE", "")
    
    if run_mode != "PRODUCTION":
        print("=" * 70)
        print("⚠️  [경고] 로컬 환경에서 봇 실행을 시도하고 있습니다.")
        print("=" * 70)
        print()
        print("📌 이 봇은 서버에서 실행 중일 수 있습니다.")
        print("   동시에 두 곳에서 실행되면 'Conflict' 에러가 발생합니다.")
        print()
        print("🔍 현재 환경:")
        print(f"   - RUN_MODE: '{run_mode or '미설정'}'")
        print(f"   - 호스트: {os.uname().nodename}")
        print()
        print("💡 선택지:")
        print("   [Y] 예, 로컬에서 실행합니다 (주의: 서버와 충돌 가능)")
        print("   [N] 아니오, 실행을 취소합니다")
        print("   [?] 도움말 보기")
        print("=" * 70)
        
        try:
            response = input("\n선택하세요 (Y/N/?): ").strip().upper()
            
            if response == '?':
                print("\n📖 도움말:")
                print("   • 서버에서만 실행하려면 .env에 RUN_MODE=PRODUCTION 추가")
                print("   • 로컬 테스트 시 서버 봇을 먼저 중지하세요")
                print("   • 충돌 방지를 위해 한 곳에서만 실행하세요")
                print()
                response = input("계속하시겠습니까? (Y/N): ").strip().upper()
            
            if response != 'Y':
                print("\n🛑 실행이 취소되었습니다.")
                sys.exit(0)
            
            print("\n⚠️  로컬 실행을 계속합니다. 서버와 충돌에 주의하세요!")
            print("=" * 70)
            time.sleep(1)  # 사용자가 메시지를 읽을 시간 제공
            
        except KeyboardInterrupt:
            print("\n\n🛑 사용자가 취소했습니다.")
            sys.exit(0)
    else:
        print("✅ [PRODUCTION] 서버 환경 확인됨")
    
    return True

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
    # 🛡️ 서버 환경 검증 (로컬 실행 차단)
    validate_server_environment()
    
    print("🚀 SHawn-BOT v5.3.0 시작 (Integration Mode)...")
    
    # 🧠 신경계 시스템 상태
    if NEURAL_SYSTEM_AVAILABLE:
        print("✅ D-CNS 신경계 시스템 활성화")
    else:
        print("⚠️  D-CNS 신경계 시스템 미로드 (systems/neural 확인 필요)")
    
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
    
    # Start
    bot.run()

if __name__ == "__main__":
    main()
