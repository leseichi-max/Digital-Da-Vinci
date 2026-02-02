"""
D-CNS (Digital Central Nervous System) API Server
FastAPI 기반의 고성능 신경망 인터페이스
"""

import sys
import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from pydantic import BaseModel

# 프로젝트 루트 경로 설정
sys.path.append(os.getcwd())

from fastapi import FastAPI, HTTPException, BackgroundTasks
from projects.ddc.brain.brain_core.chat_engine import ChatEngine, get_chat_engine
from projects.ddc.brain.neuronet.circadian_rhythm import CircadianRhythm
from projects.ddc.brain.brain_core.brainstem.advanced_watchdog import AdvancedWatchdog
from projects.ddc.brain.brain_core.brainstem.multi_level_recovery import MultiLevelRecoverySystem
import asyncio

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("D-CNS-API")

# 전역 엔진 인스턴스
engine: Optional[ChatEngine] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    서버 생명주기 관리:
    시작 시: 뇌(Brain)를 메모리에 로드 (Cold Start 제거)
    종료 시: 리소스 정리
    """
    global engine
    logger.info("🧠 D-CNS Booting up... (Pre-loading Neuro-synapses)")
    
    try:
        # 1. 엔진 인스턴스화
        engine = get_chat_engine() 
        
        # 2. 비동기 초기화 (API Discovery) 수행
        # 이 과정에서 실시간으로 가용 모델을 발굴하고 후보군을 빌드합니다.
        await engine.initialize()
        
        logger.info("✅ D-CNS Online & Ready!")
        
        # 3. [v6.0] 즉시 신경가소성 학습 (Circadian Rhythm) 트리거
        circadian = CircadianRhythm(engine)
        # 먼저 한 번 학습(테스트)을 수행하고 백그라운드 스케줄링 시작
        asyncio.create_task(circadian.run_full_diagnostic()) 
        asyncio.create_task(circadian.start_clock(interval_seconds=86400))
        
        # 4. [v6.1] Advanced Watchdog 시작 (1초 주기 모니터링)
        watchdog = AdvancedWatchdog(check_interval=1.0)
        asyncio.create_task(watchdog.start())
        logger.info("🐕 Advanced Watchdog started (1s interval)")
        
        # 5. [v6.1] Multi-Level Recovery System 초기화
        recovery_system = MultiLevelRecoverySystem()
        logger.info("🔧 Multi-Level Recovery System initialized")
        
    except Exception as e:
        logger.error(f"❌ Brain Initialization Failed: {e}")
        raise e
        
    yield
    
    logger.info("💤 D-CNS Shutting down...")
    # 필요 시 정리 로직 (DB 커넥션 종료 등)

app = FastAPI(
    title="Digital Da Vinci API",
    version="5.5.0",
    description="Digital Central Nervous System Interface",
    lifespan=lifespan
)

# --- 요청/응답 모델 ---
class ChatRequest(BaseModel):
    user_id: int
    text: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    provider: str
    latency_ms: float
    status: str

# --- 엔드포인트 ---

@app.get("/health")
async def health_check():
    """시스템 상태 확인"""
    if engine:
        return {"status": "healthy", "brain": "online", "version": "5.5.0"}
    return {"status": "degraded", "brain": "offline"}

@app.post("/v1/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    핵심 채팅 인터페이스
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Brain is not ready yet.")
    
    try:
        # 실제 추론 실행
        # (ChatEngine 내부에서 Neuroplasticity, Routing, API Call 모두 수행)
        # get_response는 비동기 함수여야 함 (이미 async def로 구현됨)
        import time
        start = time.time()
        
        response_text = await engine.get_response(req.user_id, req.text)
        
        duration = (time.time() - start) * 1000
        
        # 메타데이터 추출 (단순화를 위해 여기서는 텍스트 파싱, 추후 구조화 가능)
        provider = "Unknown"
        if "Groq" in response_text: provider = "Groq"
        elif "Gemini" in response_text: provider = "Gemini"
        elif "Claude" in response_text: provider = "Claude"
        
        return ChatResponse(
            response=response_text,
            provider=provider,
            latency_ms=round(duration, 2),
            status="success"
        )
        
    except Exception as e:
        logger.error(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # 로컬 개발용 실행
    uvicorn.run("projects.ddc.api.app:app", host="0.0.0.0", port=8000, reload=True)
