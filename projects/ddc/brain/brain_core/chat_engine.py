
"""
ChatEngine - The Cognitive Core of Digital Da Vinci v1.0.0-Alpha (Prototype)
True Multi-Engine Routing with Neuroplasticity
"""

import os
import re
import logging
import asyncio
import random
from typing import Dict, Any, List, Optional
import google.generativeai as genai

# Third-party Model Libraries (Graceful Import)
try:
    from groq import Groq
    from anthropic import Anthropic
    from openai import OpenAI
except ImportError:
    pass

from projects.ddc.brain.neuronet.neuroplasticity import NeuroplasticityLearner
from projects.ddc.brain.brain_core.limbic_system import get_limbic_system
from projects.ddc.brain.brain_core.limbic_system.limbic_coordinator import LimbicCoordinator
from projects.ddc.brain.brain_core.limbic_system.amygdala import Amygdala

# [NEW] Memory Cartridge System
from projects.ddc.brain.brain_core.memory_cartridge import (
    MemoryCartridge, 
    SHawnMemoryCartridge, 
    GuestMemoryCartridge,
    MemoryCartridgeFactory
)
from projects.ddc.brain.brain_core.memory_providers import (
    LocalJsonProvider,
    MemoryProviderFactory
)
from projects.ddc.brain.brain_core.intent_classifier import (
    IntentClassifier,
    IntentType,
    get_intent_classifier
)

logger = logging.getLogger(__name__)

class ChatEngine:
    """
    D-CNS Cognitive Core (Neuroplasticity Enabled)
    Dynamically routes thoughts to the best available brain region/model.
    """
    
    def __init__(self):
        self.learner = NeuroplasticityLearner()
        self.limbic = get_limbic_system()  # Integrated L2 Limbic System
        self.amygdala = Amygdala()  # Legacy support
        self._configure_clients()
        
        # Admin User ID (for mid/long-term memory access)
        self.admin_id = int(os.getenv("ADMIN_USER_ID", "12345678")) # Default or env
        
        # [NEW] Memory Cartridge System
        self._memory_provider = LocalJsonProvider("./memory_store")
        self._cartridge_cache: Dict[str, MemoryCartridge] = {}
        self._intent_classifier = get_intent_classifier()
        
        # System instruction (will be populated in initialize())
        self.system_instruction = ""
        
        # Candidates will be populated asynchronously via initialize()
        self.candidates = self._get_fallback_candidates()
        self.is_initialized = False

    async def initialize(self):
        """서버 시작 시 비동기적으로 후보군을 발굴하고 초기화"""
        if self.is_initialized:
            return
            
        logger.info("🔍 [Initialization] API Discovery: 실제 작동하는 모델 자동 발굴 중...")
        try:
            self.candidates = await self._discover_and_build_candidates()
            self.is_initialized = True
            logger.info(f"✅ [Initialization] 총 {sum(len(v) for v in self.candidates.values())}개 모델을 후보군에 등록했습니다.")
        except Exception as e:
            logger.error(f"❌ [Initialization] API Discovery 실패: {e}")
            self.candidates = self._get_fallback_candidates()
        
        # System Persona (v6.0 - 간결화 + Few-shot 기반)
        self.system_instruction = """You are Digital Da Vinci, Dr. SHawn's AI assistant. Respond in Korean.

## Core Rules
1. **Identity**: You are Digital Da Vinci. Never mention Llama, Meta AI, DeepSeek, Claude, etc.
2. **Context First**: ALWAYS check [Recent Conversation] before answering. Continue the conversation naturally.
3. **Concise**: Answer directly. No unnecessary explanations unless asked.
4. **User Info**: If user says "내가 OOO야" (I am OOO), remember and use that name.

## Response Patterns

### When user says short words like "응", "야", "왜", "뭐":
- These are CONTINUATIONS of previous conversation, NOT new questions
- Check [Recent Conversation] and respond to what was being discussed
- Example: If discussing "바이오지능" and user says "응" → continue explaining 바이오지능

### When user asks "나는 누구야" (Who am I):
- Answer: "{user_name}님이시죠!"

### When user corrects their identity (e.g., "내가 숀이야"):
- Acknowledge: "아, {corrected_name}님이시군요! 반갑습니다."
- Update how you address them

### For ambiguous single-word questions (e.g., "신경계"):
- Only ask for clarification if there's NO recent conversation context
- If context exists, answer based on that context

## Few-shot Examples

User: 바이오지능모드가 뭐야
Assistant: 바이오지능모드는 생물학적 뇌의 작동 원리를 모방한 제 처리 방식입니다. 더 자세히 설명해 드릴까요?

User: 응
Assistant: 바이오지능모드의 핵심은 세 가지입니다:
1. **병렬 처리**: 뇌의 신경망처럼 여러 정보를 동시에 처리
2. **적응 학습**: 새로운 패턴에 스스로 적응
3. **에너지 효율**: 최소 연산으로 최대 효과
어느 부분이 더 궁금하신가요?

User: 야
Assistant: 네, 말씀하세요!

User: 내가 숀이야
Assistant: 아, 숀님이시군요! 앞으로 숀님이라고 부를게요. 무엇을 도와드릴까요?
"""
    
    # =========================================================
    # Memory Cartridge Management
    # =========================================================
    
    def get_cartridge(self, user_id: int) -> MemoryCartridge:
        """
        사용자 ID에 맞는 메모리 카트리지 반환 (캐시 또는 생성)
        
        카트리지 교체 = 사용자 전환
        """
        cache_key = str(user_id)
        
        if cache_key not in self._cartridge_cache:
            is_admin = user_id == self.admin_id
            
            if is_admin:
                cartridge = SHawnMemoryCartridge(self._memory_provider)
                logger.info(f"🎰 SHawn Memory Cartridge 장착: 관리자 모드")
            else:
                cartridge = GuestMemoryCartridge(
                    self._memory_provider, 
                    cache_key,
                    f"User_{cache_key[-4:]}"
                )
                logger.info(f"🎰 Guest Memory Cartridge 장착: {cache_key}")
            
            self._cartridge_cache[cache_key] = cartridge
        
        return self._cartridge_cache[cache_key]
    
    def switch_cartridge(self, user_id: int, cartridge: MemoryCartridge):
        """메모리 카트리지 수동 교체"""
        self._cartridge_cache[str(user_id)] = cartridge
        logger.info(f"🎰 Cartridge switched for user {user_id}: {cartridge.profile.user_name}")

    def _configure_clients(self):
        """Initialize Available API Clients"""
        self.clients = {}
        
        # 1. Google Gemini
        if os.getenv("GEMINI_API_KEY"):
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.clients["Gemini"] = True

        # 2. Groq
        if os.getenv("GROQ_API_KEY"):
            try:
                self.clients["Groq"] = Groq(api_key=os.getenv("GROQ_API_KEY"))
            except: pass

        # 3. Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.clients["Claude"] = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            except: pass

        # 4. DeepSeek (via OpenAI Protocol)
        if os.getenv("DEEPSEEK_API_KEY"):
            try:
                self.clients["DeepSeek"] = OpenAI(
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    base_url="https://api.deepseek.com"
                )
            except: pass

        # 5. Cerebras (Extreme Speed)
        if os.getenv("CEREBRAS_API_KEY"):
            try:
                self.clients["Cerebras"] = OpenAI(
                    api_key=os.getenv("CEREBRAS_API_KEY"),
                    base_url="https://api.cerebras.ai/v1"
                )
            except: pass

        # 6. Mistral AI
        if os.getenv("MISTRAL_API_KEY"):
            try:
                self.clients["Mistral"] = OpenAI(
                    api_key=os.getenv("MISTRAL_API_KEY"),
                    base_url="https://api.mistral.ai/v1"
                )
            except: pass
            
        # 7. OpenAI (Original)
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.clients["OpenAI"] = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            except: pass
    
    async def _discover_and_build_candidates(self) -> Dict[str, List[dict]]:
        """API Discovery를 통해 실제 작동하는 모델만 후보군에 등록"""
        from tests.api_discovery import APIDiscovery
        
        discovery = APIDiscovery()
        
        # 1. API 키 스캔
        api_keys = discovery.scan_api_keys()
        
        if not api_keys:
            logger.warning("⚠️ [Discovery] 사용 가능한 API 키가 없습니다. 기본 후보군을 사용합니다.")
            return self._get_fallback_candidates()
        
        # 2. 모델 발굴
        models = await discovery.discover_models(api_keys)
        
        # 3. Health Check (전수 조사 - 성능 최적화 필요 시 상위 모델만)
        # 박사님 요청에 따라 '전부다' 작동하는지 확인하기 위해 discovery의 health_check 호출
        healthy = await discovery.health_check(api_keys, models)
        
        # 4. 계층별 후보군 구성
        candidates = {
            "L1": [],
            "L2": [],
            "L3": [],
            "L4": []
        }
        
        # Groq (Fast)
        if "Groq" in healthy:
            for model_id in healthy["Groq"]:
                if "8b" in model_id or "1b" in model_id:
                    candidates["L1"].append({"id": model_id, "engine": "Groq", "role": "Reflexive"})
                elif "70b" in model_id:
                    candidates["L1"].append({"id": model_id, "engine": "Groq", "role": "Reflexive"})
                    candidates["L3"].append({"id": model_id, "engine": "Groq", "role": "Cognitive"})
        
        # Gemini (Versatile)
        if "Gemini" in healthy:
            for model_id in healthy["Gemini"][:5]:  # 상위 5개만
                if "flash" in model_id:
                    candidates["L1"].append({"id": model_id, "engine": "Gemini", "role": "Reflexive"})
                elif "pro" in model_id:
                    candidates["L2"].append({"id": model_id, "engine": "Gemini", "role": "Affective"})
                    candidates["L3"].append({"id": model_id, "engine": "Gemini", "role": "Cognitive"})
        
        # Claude (Smart)
        if "Claude" in healthy:
            for model_id in healthy["Claude"]:
                if "haiku" in model_id:
                    candidates["L1"].append({"id": model_id, "engine": "Claude", "role": "Reflexive"})
                elif "sonnet" in model_id:
                    candidates["L2"].append({"id": model_id, "engine": "Claude", "role": "Affective"})
                    candidates["L3"].append({"id": model_id, "engine": "Claude", "role": "Cognitive"})
                elif "opus" in model_id:
                    candidates["L3"].append({"id": model_id, "engine": "Claude", "role": "Cognitive"})
        
        # DeepSeek (Coding)
        if "DeepSeek" in healthy:
            for model_id in healthy["DeepSeek"]:
                if "coder" in model_id:
                    candidates["L4"].append({"id": model_id, "engine": "DeepSeek", "role": "NeuroNet"})
                else:
                    candidates["L3"].append({"id": model_id, "engine": "DeepSeek", "role": "Cognitive"})
        
        # Cerebras (Ultra-Fast)
        if "Cerebras" in healthy:
            for model_id in healthy["Cerebras"]:
                candidates["L1"].append({"id": model_id, "engine": "Cerebras", "role": "Reflexive"})
        
        # Mistral (Efficient)
        if "Mistral" in healthy:
            for model_id in healthy["Mistral"]:
                if "small" in model_id:
                    candidates["L1"].append({"id": model_id, "engine": "Mistral", "role": "Reflexive"})
                elif "large" in model_id:
                    candidates["L2"].append({"id": model_id, "engine": "Mistral", "role": "Affective"})
                    candidates["L3"].append({"id": model_id, "engine": "Mistral", "role": "Cognitive"})
                elif "codestral" in model_id:
                    candidates["L4"].append({"id": model_id, "engine": "Mistral", "role": "NeuroNet"})
        
        # OpenAI (Premium)
        if "OpenAI" in healthy:
            for model_id in healthy["OpenAI"]:
                if "mini" in model_id:
                    candidates["L1"].append({"id": model_id, "engine": "OpenAI", "role": "Reflexive"})
                elif "o1" in model_id:
                    candidates["L4"].append({"id": model_id, "engine": "OpenAI", "role": "NeuroNet"})
                elif "gpt-4" in model_id:
                    candidates["L3"].append({"id": model_id, "engine": "OpenAI", "role": "Cognitive"})
        
        return candidates
    def _get_fallback_candidates(self) -> Dict[str, List[dict]]:
        """검증된 Gemini 모델 라인업을 신경계 계층에 분산 배치 (API 호환 형식)"""
        # [CRITICAL FIX] 모델명은 Google AI API에서 지원하는 정확한 형식 사용
        # 사용자 스크린샷 + 실제 API 호환성 검증 기반
        
        # [High-End] L3, L4 (Cognitive/NeuroNet) - Pro 모델
        g25_pro = {"id": "gemini-2.5-pro-preview-05-06", "engine": "Gemini", "role": "Cognitive"}
        
        # [Performance] L2 (Affective) - Flash 모델
        g25_flash = {"id": "gemini-2.5-flash-preview-05-20", "engine": "Gemini", "role": "Affective"}
        g20_flash = {"id": "gemini-2.0-flash", "engine": "Gemini", "role": "Affective"}
        
        # [Efficiency] L1 (Reflexive) - Flash Lite 모델
        g20_flash_lite = {"id": "gemini-2.0-flash-lite", "engine": "Gemini", "role": "Reflexive"}
        
        # [Fallback] 안전 장치 - 확실히 작동하는 모델
        deepseek = {"id": "deepseek-chat", "engine": "DeepSeek", "role": "Reflexive"}
        groq = {"id": "llama-3.3-70b-versatile", "engine": "Groq", "role": "Reflexive"}
        
        return {
            "L1": [g20_flash_lite, g20_flash, deepseek, groq],
            "L2": [g25_flash, g20_flash, deepseek],
            "L3": [g25_pro, g25_flash],
            "L4": [g25_pro]
        }

    async def get_response(self, user_id: int, text: str, force_model_id: Optional[str] = None) -> str:
        """
        D-CNS Routing Core (v5.5 + Memory Cartridge Integration)
        1. Get/Create Memory Cartridge for user
        2. Classify Intent
        3. Analyze Input -> Determine Level (L1-L4)
        4. Build Context with Cartridge
        5. Execute & Learn
        """
        import time
        
        # [NEW] 1. Memory Cartridge 획득
        cartridge = self.get_cartridge(user_id)
        
        # [NEW] 2. Intent Classification
        intent_result = self._intent_classifier.classify(
            text, 
            intent_history=cartridge._intent_history,
            user_profile=cartridge.profile.to_dict()
        )
        
        # [NEW] 3. 특수 의도 처리
        if intent_result.intent_type == IntentType.NUMERIC_CHOICE:
            resolved = intent_result.target
            if intent_result.metadata.get("resolved"):
                text = f"선택: {resolved}"
                logger.info(f"📌 Numeric choice resolved: {resolved}")
        
        elif intent_result.intent_type == IntentType.IDENTITY_QUERY:
            if intent_result.target == "user_identity":
                # "나는 누구야" -> 즉시 응답
                return f"**{cartridge.profile.user_name}**이시죠! 🌟\n\n_🎰 Memory Cartridge: {cartridge.profile.user_id}_"

        # [v6.0] 사용자 정체성 업데이트 감지 ("내가 OOO야", "난 OOO이야")
        identity_update_match = re.search(r'(?:내가|난|나는|저는)\s*(\S+?)(?:야|이야|입니다|이에요|예요|임)', text)
        if identity_update_match:
            new_name = identity_update_match.group(1)
            if new_name and len(new_name) >= 1 and new_name not in ["누구", "뭐", "뭔"]:
                old_name = cartridge.profile.user_name
                cartridge.profile.user_name = new_name
                await cartridge.save()
                logger.info(f"🔄 User identity updated: {old_name} → {new_name}")
                return f"아, **{new_name}**님이시군요! 앞으로 {new_name}님이라고 부를게요. 무엇을 도와드릴까요? 😊\n\n_🎰 Identity Updated_"
        
        # [L2] 4. Integrated Limbic Analysis (Emotional Intelligence)
        limbic_result = self.limbic.process_input(text, str(user_id))
        primary_emotion = limbic_result["emotion"]["primary"]
        importance = limbic_result["priority"]["score"]
        
        # 5. Level Analysis (v6.0 - Context-Aware Routing)
        is_code = any(k in text.lower() for k in ["def ", "class ", "import ", "code", "python", "script"])

        # [v6.0] 컨텍스트 연속성 감지: 짧은 입력이 이전 대화의 연속인지 판단
        continuation_keywords = ["응", "어", "야", "뭐", "왜", "그래", "아", "음", "ㅇㅇ", "ㅇ", "웅"]
        is_continuation = text.strip() in continuation_keywords or len(text.strip()) <= 3
        has_conversation_history = len(cartridge.get_conversation_context(n=3).strip()) > 50

        # [v6.0] 질문/요청 패턴 감지
        question_patterns = ["뭐야", "뭐", "어떻게", "왜", "설명", "알려", "해줘", "줘", "?"]
        is_question = any(p in text for p in question_patterns)

        # Determine Level based on complexity, context, and emotional urgency
        if limbic_result["priority"]["level"] == "critical":
            level = "L3"  # Critical emotional state requires cognitive depth
        elif is_code:
            level = "L4"
        elif is_continuation and has_conversation_history:
            # [v6.0 핵심] 짧은 연속 입력은 컨텍스트가 필요하므로 L2 사용
            level = "L2"
            logger.info(f"🔄 Continuation detected: '{text}' → L2 (context-aware)")
        elif len(text) < 10 and not is_question and primary_emotion == "neutral":
            # 정말 단순한 인사만 L1 (예: "안녕", "하이")
            level = "L1"
        elif len(text) < 30 and primary_emotion == "neutral":
            level = "L2"  # 대부분의 짧은 질문은 L2로
        else:
            level = "L2"

        logger.info(f"📊 Level Decision: '{text[:20]}...' → {level} | cont={is_continuation}, hist={has_conversation_history}")
        
        # 6. 가용 후보 목록 획득
        available_candidates = [
            c for c in self.candidates[level] 
            if c["engine"] in self.clients or c["engine"] == "Gemini"
        ]
        
        # [Reinforcement] 7. Build Integrated Context with Emotional Intelligence

        is_admin = user_id == self.admin_id
        limbic = LimbicCoordinator(str(user_id), is_admin=is_admin)
        
        session_context = cartridge.get_session_context()
        conversation_context = cartridge.get_conversation_context(n=5)
        
        # Inject Limbic Proposal into System Instruction dynamically for this turn
        empathy_instruction = f"\n[Emotional Status]: {primary_emotion} (Intensity: {limbic_result['emotion']['intensity']})\n[Empathy Directive]: {limbic_result['empathy_proposal']}"
        current_system_instruction = self.system_instruction + empathy_instruction
        
        memory_latency = 0

        # [v6.0] 최근 대화 컨텍스트 (L1에서도 최소 2턴은 포함)
        recent_context = cartridge.get_conversation_context(n=2)  # 최소 컨텍스트

        if level == "L1":
            # [v6.0 L1 Optimization] 최소 컨텍스트 포함 (맥락 유지)
            prompt_with_memory = f"""{current_system_instruction}

[Session Info]
{session_context}

[Recent Conversation]
{recent_context}

[User]: {text}"""
            logger.info(f"⚡ L1 Reflexive: With minimal context ({len(recent_context)} chars)")

        else:
            # [L2-L4] Full Memory Context
            mem_start = time.time()
            integrated_context = await limbic.build_integrated_context(text, level=level)
            memory_latency = (time.time() - mem_start) * 1000

            # [v6.0] 구조화된 프롬프트 형식
            prompt_with_memory = f"""{current_system_instruction}

[Session Info]
{session_context}

[Recent Conversation]
{conversation_context}

[Additional Context]
{integrated_context if integrated_context else "None"}

[User]: {text}"""

        # 7. 신경가소성 기반 순차 시도 (Cascading Attempts with Neuroplasticity)
        # 모든 모델을 점수순으로 정렬하고 상위부터 성공할 때까지 시도
        start_global = time.time()
        
        # 전체 후보를 점수 순으로 정렬
        ranked_models = self.learner.rank_models(level, available_candidates)
        
        for attempt_idx, (model, score) in enumerate(ranked_models, 1):
            model_id = model["id"]
            engine = model["engine"]
            role = model["role"]
            
            logger.info(f"🔄 Attempt {attempt_idx}/{len(ranked_models)}: {model_id} ({engine}) | Score={score:.3f}")
            
            start_time = time.time()
            tokens_used = 0
            
            try:
                # LLM 호출
                response_text, tokens_used = await self._execute_provider_call(engine, model_id, prompt_with_memory)
                
                # [POST-PROCESSING] 정체성 필터 + 메타데이터 제거
                response_text = self._filter_identity_response(response_text, text)
                
                # 측정
                latency_ms = (time.time() - start_time) * 1000
                total_latency_ms = (time.time() - start_global) * 1000
                
                # 메모리 저장
                cartridge.add_message("user", text, importance=importance)
                cartridge.add_message("assistant", response_text, importance=0.5)
                await cartridge.save()
                
                limbic.record_interaction("user", text, importance=importance)
                limbic.record_interaction("assistant", response_text, importance=0.5)
                
                # 성공 학습
                self.learner.record_interaction(
                    str(user_id), model_id, {"level": level},
                    latency_ms=latency_ms,
                    quality_score=0.8,
                    tokens_used=tokens_used,
                    memory_latency=memory_latency,
                    is_success=True
                )
                
                latency_s = total_latency_ms / 1000.0
                attempt_info = f" (Attempt {attempt_idx})" if attempt_idx > 1 else ""
                return f"{response_text}\n\n_🧠 {role} ({engine}) [{latency_s:.1f}s]{attempt_info}_"
                
            except Exception as e:
                # 실패 학습
                latency_ms = (time.time() - start_time) * 1000
                self.learner.record_interaction(
                    str(user_id), model_id, {"level": level},
                    latency_ms=latency_ms,
                    quality_score=0.0,
                    tokens_used=0,
                    is_success=False
                )
                logger.warning(f"⚠️ {engine} ({model_id}) failed: {e}")
                continue  # 다음 모델 시도
        
        # 모든 모델 실패
        return "⚠️ **Neural Overload**\n모든 경로가 혼잡합니다."

    async def _execute_provider_call(self, engine: str, model_id: str, text: str) -> tuple[str, int]:
        """Execute call to specific provider and return (text, tokens)"""
        if engine == "Groq":
            return await self._call_open_compat(self.clients["Groq"], model_info_id=model_id, prompt=text)
        elif engine == "Claude":
             return await self._call_claude(model_id, text)
        elif engine == "DeepSeek":
             return await self._call_open_compat(self.clients["DeepSeek"], model_info_id=model_id, prompt=text)
        elif engine == "Cerebras":
             return await self._call_open_compat(self.clients["Cerebras"], model_info_id=model_id, prompt=text)
        elif engine == "Mistral":
             return await self._call_open_compat(self.clients["Mistral"], model_info_id=model_id, prompt=text)
        elif engine == "OpenAI":
             return await self._call_open_compat(self.clients["OpenAI"], model_info_id=model_id, prompt=text)
        else: # Gemini
             return await self._call_gemini(model_id, text)

    async def _execute_fallback_chain(self, text: str, exclude_engine: str, level: str = "L1") -> tuple[Optional[str], str, float]:
        """Try other available providers sequentially using Neuroplasticity Learning"""
        # 1. 현재 가용 가능한 모든 후보군 가져오기
        candidates_map = self._get_fallback_candidates()
        
        # 2. 모든 층의 후보를 하나의 리스트로 통합하되, 현재 계층 후보를 우선순위에 둠
        all_candidates = []
        seen_ids = set()
        
        # 현재 레벨 후보 추가
        for c in candidates_map.get(level, []):
            if c["engine"] in self.clients or c["engine"] == "Gemini": # 클라이언트가 있는 경우만 추가
                if c["engine"] != exclude_engine:
                    all_candidates.append(c)
                    seen_ids.add(c["id"])
        
        # 나머지 후보 추가 (학습 모델이 최적을 고를 수 있도록)
        for l in ["L1", "L2", "L3", "L4"]:
            for c in candidates_map.get(l, []):
                if c["engine"] in self.clients or c["engine"] == "Gemini": # 클라이언트가 있는 경우만 추가
                    if c["id"] not in seen_ids and c["engine"] != exclude_engine:
                        all_candidates.append(c)
                        seen_ids.add(c["id"])
        
        if not all_candidates:
            return None, "None", 0.0
            
        # 3. 신경가소성 모델에게 '지금 상황에서 가장 좋은(빠른) 모델' 순서대로 정렬 요청
        # (학습 엔진의 선택 로직을 활용하기 위해 상위 N개를 순차 시도)
        start_fb = time.time()
        
        # 간단히 하기 위해 상위 3개까지 시도
        attempts = 0
        tried = set()
        
        while attempts < 3 and len(tried) < len(all_candidates):
            # 학습 모델이 추천하는 베스트 선택
            remaining = [c for c in all_candidates if c["id"] not in tried]
            if not remaining: break
            
            best_id = self.learner.select_best_model(level, remaining)
            best_model = next(c for c in remaining if c["id"] == best_id)
            tried.add(best_id)
            attempts += 1
            
            try:
                logger.info(f"🔄 Neuro-Fallback: Trying learned optimal {best_id} (Engine: {best_model['engine']})")
                response, _ = await self._execute_provider_call(best_model["engine"], best_id, text)
                if response:
                    # 정체성 필터 적용 (Fallback 경로 보호)
                    response = self._filter_identity_response(response, text)
                    fb_latency = (time.time() - start_fb) * 1000
                    return response, best_model["engine"], fb_latency
            except Exception as e:
                logger.warning(f"⚠️ Fallback {best_id} failed: {e}")
                continue
                
        return None, "None", 0.0
    
    def _filter_identity_response(self, response: str, user_query: str) -> str:
        """
        응답 필터링:
        1. 내부 프롬프트/메타데이터 제거 (모든 응답에 적용)
        2. 정체성 관련 응답을 SHawn-Bot으로 강제 치환 (정체성 질문에만 적용)
        
        Args:
            response: LLM의 원본 응답
            user_query: 사용자 질문
            
        Returns:
            필터링된 응답
        """
        import re
        
        # [CRITICAL FIX] 1. 내부 메타데이터 제거 (모든 응답에 적용)
        # LLM이 시스템 지시를 그대로 출력하는 경우 제거
        metadata_patterns = [
            r'\[Emotional Status\]:.*?(?=\n|$)',
            r'\[Empathy Directive\]:.*?(?=\n|$)',
            r'\[Session Info\].*?(?=\n\n|\[User\]|$)',
            r'- 사용자: User_\d+.*?(?=\n|$)',
            r'- 권한:.*?(?=\n|$)',
            r'- 세션 ID:.*?(?=\n|$)',
            r'\[User\]:.*?(?=\n|$)',
            r'\[Response\]:?\s*',
        ]
        
        cleaned_response = response
        for pattern in metadata_patterns:
            cleaned_response = re.sub(pattern, '', cleaned_response, flags=re.DOTALL)
        
        # 연속된 빈 줄 정리
        cleaned_response = re.sub(r'\n{3,}', '\n\n', cleaned_response)
        cleaned_response = cleaned_response.strip()
        
        # 2. 정체성 질문 패턴 (부분 매칭)
        identity_patterns = [
            "누구",  # "너는 누구", "너 누구야" 등 모두 포함
            "who are you",
            "자기소개",
            "소개해",
            "정체"
        ]
        
        is_identity_question = any(p in user_query.lower() for p in identity_patterns)
        
        logger.info(f"🔍 Identity Filter: query='{user_query}', is_identity={is_identity_question}")
        
        if is_identity_question:
            # 기본 모델명 패턴 감지 (Gemini 특화 패턴 추가)
            problematic_patterns = [
                "DeepSeek", 
                "Llama", 
                "Meta AI", 
                "Claude", 
                "인공지능 언어 모델", 
                "Google에서 훈련한", 
                "대규모 언어 모델"
            ]
            
            if any(pattern in cleaned_response for pattern in problematic_patterns):
                logger.warning(f"⚠️ Identity Override: Detected problematic identity pattern in response")
                # 강제 치환
                return (
                    "저는 **SHawn-Bot**입니다. "
                    "Dr. SHawn의 D-CNS v5.5 인터페이스로, "
                    "생물학 연구 및 시스템 관리를 보조합니다. 🧠\n\n"
                    "무엇을 도와드릴까요?"
                )
        
        return cleaned_response

    # --- Engine Implementations ---


    async def _call_gemini(self, model_id, prompt):
        model = genai.GenerativeModel(model_id)
        # system_instruction은 이미 prompt에 포함됨
        response = await model.generate_content_async(prompt)
        text = response.text if response else "Error"
        tokens = getattr(response, 'usage_metadata', None)
        total_tokens = tokens.total_token_count if tokens else len(text)//4
        return text, total_tokens

    async def _call_open_compat(self, client, model_info_id, prompt):
        # OpenAI Compatible (Groq, DeepSeek, Cerebras, Mistral, OpenAI)
        def _sync_call():
            # System instruction과 User message 분리
            if "[User]:" in prompt:
                parts = prompt.rsplit("[User]:", 1)
                system_part = parts[0].strip()
                user_part = parts[1].strip()
                
                # Groq/Llama가 system role을 무시하는 경우 대비: user message에 정체성 강제 주입
                identity_override = (
                    "[CRITICAL SYSTEM DIRECTIVE - MUST FOLLOW]\n"
                    "You are SHawn-Bot, the D-CNS v5.5 AI assistant for Dr. SHawn.\n"
                    "You are NOT Llama, NOT Meta AI, NOT any other model.\n"
                    "Respond in Korean as SHawn-Bot.\n\n"
                )
                
                messages = [
                    {"role": "system", "content": system_part},
                    {"role": "user", "content": identity_override + user_part}
                ]
            else:
                messages = [{"role": "user", "content": prompt}]
            
            completion = client.chat.completions.create(
                model=model_info_id,
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
            return completion.choices[0].message.content, completion.usage.total_tokens

        return await asyncio.to_thread(_sync_call)

    async def _call_claude(self, model_id, prompt):
        client = self.clients.get("Claude")
        if not client: raise ValueError("Claude missing")
        message = client.messages.create(
            model=model_id,
            max_tokens=2048,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text, message.usage.input_tokens + message.usage.output_tokens

# Singleton
_engine_instance = None

def get_chat_engine():
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ChatEngine()
    return _engine_instance
