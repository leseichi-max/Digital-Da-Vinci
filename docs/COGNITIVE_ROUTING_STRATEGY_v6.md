# Digital Da Vinci D-CNS v6.0: 자기진화 인지 라우팅 아키텍처

> **최신 오픈소스 도구 종합 분석 기반 최적 전략 (2025-2026)**

---

## 📊 현재 아키텍처 심층 분석

### 현재 강점 (Keep)

| 구성요소 | 상태 | 평가 |
|---------|------|------|
| **4계층 신경계 (L1-L4)** | ✅ 완성 | 생물학적 메타포 우수, 레벨별 가중치 차별화 |
| **Neuroplasticity Learner** | ✅ 6차원 | Speed/Quality/Token/Cost/Memory/Reliability |
| **Limbic System (L2)** | ✅ 통합 | 감정 분석 + 공감 응답 + Q-Learning |
| **Memory Cartridge** | ✅ 작동 | 사용자별 컨텍스트 관리 |
| **API Discovery** | ✅ 동적 | 헬스체크 기반 모델 후보군 구성 |
| **Cascading Fallback** | ✅ 구현 | 순차 시도 + 실패 학습 |

### 개선 필요 영역 (Improve)

| 영역 | 현재 | 문제점 | 목표 |
|-----|------|--------|-----|
| **Intent Routing** | Rule-based | O(n) 패턴 매칭, 확장성 한계 | Semantic Vector 기반 O(1) |
| **프롬프트 최적화** | 하드코딩 | 수동 튜닝, A/B 테스트 불가 | DSPy 자동 최적화 |
| **품질 평가** | 없음 | quality_score=0.8 고정값 | 실시간 다차원 평가 |
| **응답 캐싱** | 없음 | 반복 쿼리 재계산 | Semantic Cache (2-10x 속도) |
| **자기학습** | EMA만 | 피드백 루프 미완성 | Continuous Learning Pipeline |
| **Observability** | 로깅만 | 분산 추적 없음 | OpenTelemetry 통합 |

---

## 🚀 Phase별 진화 로드맵

### Phase 1: Semantic Router 도입 (1주)

> **목표**: 라우팅 지연 10ms 이하, 정확도 95%+

#### 1.1 Aurelio Semantic Router 통합

```python
# projects/ddc/brain/brain_core/semantic_router.py
from semantic_router import Route, SemanticRouter
from semantic_router.encoders import FastEmbedEncoder

class DCNSSemanticRouter:
    """
    D-CNS 계층 라우팅을 벡터 유사도 기반으로 수행
    - LLM 호출 없이 <10ms 라우팅
    - 새 의도 추가 시 임베딩만 업데이트
    """

    def __init__(self):
        # FastEmbed: 로컬 실행, 빠른 추론
        self.encoder = FastEmbedEncoder(model_name="BAAI/bge-small-en-v1.5")

        # 계층별 라우트 정의
        self.routes = [
            # L1: 단순/빠른 응답
            Route(
                name="L1_reflexive",
                utterances=[
                    "안녕", "ㅎㅇ", "뭐해", "오케이", "ㅇㅇ",
                    "hi", "hello", "ok", "yes", "no",
                    "1", "2", "3",  # 숫자 선택
                ],
                metadata={"level": "L1", "target_latency_ms": 500}
            ),

            # L2: 감정/공감 필요
            Route(
                name="L2_affective",
                utterances=[
                    "힘들어", "슬퍼", "우울해", "기뻐", "화나",
                    "걱정돼", "불안해", "고마워", "미안해",
                    "어떻게 생각해?", "조언 좀",
                ],
                metadata={"level": "L2", "target_latency_ms": 2000}
            ),

            # L3: 분석/인지 작업
            Route(
                name="L3_cognitive",
                utterances=[
                    "분석해줘", "설명해줘", "비교해줘", "요약해줘",
                    "왜 그런거야", "근거가 뭐야", "장단점",
                    "논문", "연구", "데이터", "통계",
                ],
                metadata={"level": "L3", "target_latency_ms": 10000}
            ),

            # L4: 코드/창의적 작업
            Route(
                name="L4_neuronet",
                utterances=[
                    "코드 짜줘", "함수 만들어", "버그 수정",
                    "def ", "class ", "import ",
                    "아이디어", "창작", "설계",
                ],
                metadata={"level": "L4", "target_latency_ms": 15000}
            ),

            # 카트리지 전환 (이모지 기반)
            Route(
                name="cartridge_bio",
                utterances=["🧬", "바이오", "세포", "오가노이드", "배양"],
                metadata={"cartridge": "bio"}
            ),
            Route(
                name="cartridge_quant",
                utterances=["📊", "통계", "그래프", "시각화", "분석"],
                metadata={"cartridge": "quant"}
            ),
        ]

        self.router = SemanticRouter(
            encoder=self.encoder,
            routes=self.routes,
            auto_sync="local"  # 로컬 동기화
        )

    def route(self, text: str) -> dict:
        """
        입력 텍스트에 대한 최적 라우트 결정

        Returns:
            {
                "level": "L1"|"L2"|"L3"|"L4",
                "confidence": 0.0-1.0,
                "route_name": str,
                "metadata": dict
            }
        """
        result = self.router(text)

        if result is None:
            # 기본값: L2 (균형잡힌 응답)
            return {
                "level": "L2",
                "confidence": 0.5,
                "route_name": "default",
                "metadata": {"target_latency_ms": 2000}
            }

        return {
            "level": result.metadata.get("level", "L2"),
            "confidence": result.score,
            "route_name": result.name,
            "metadata": result.metadata
        }

    def add_route_examples(self, route_name: str, examples: list):
        """런타임에 새 예시 추가 (온라인 학습)"""
        for route in self.routes:
            if route.name == route_name:
                route.utterances.extend(examples)
        self.router.sync()
```

#### 1.2 ChatEngine 통합

```python
# chat_engine.py 수정
from projects.ddc.brain.brain_core.semantic_router import DCNSSemanticRouter

class ChatEngine:
    def __init__(self):
        # ... 기존 코드 ...
        self._semantic_router = DCNSSemanticRouter()

    async def get_response(self, user_id: int, text: str, ...):
        # [NEW] Semantic Router로 레벨 결정 (< 10ms)
        route_result = self._semantic_router.route(text)
        level = route_result["level"]
        confidence = route_result["confidence"]

        # 낮은 신뢰도일 때만 기존 rule-based 폴백
        if confidence < 0.6:
            level = self._fallback_level_detection(text)
```

---

### Phase 2: Semantic Cache 구축 (1주)

> **목표**: 반복 쿼리 캐시 히트율 40%+, 응답 지연 2-10x 감소

#### 2.1 GPTCache 통합

```python
# projects/ddc/brain/neuronet/semantic_cache.py
from gptcache import Cache
from gptcache.embedding import Onnx
from gptcache.similarity_evaluation import SearchDistanceEvaluation
from gptcache.manager import CacheBase, VectorBase, get_data_manager

class DCNSSemanticCache:
    """
    D-CNS 시맨틱 캐시 레이어
    - 의미적으로 유사한 쿼리 캐시 히트
    - 레벨별 TTL/유사도 임계값 차별화
    """

    # 레벨별 캐시 정책
    LEVEL_POLICIES = {
        "L1": {
            "similarity_threshold": 0.85,  # 높은 유사도 요구 (단순 쿼리)
            "ttl_seconds": 3600,  # 1시간
            "enabled": True
        },
        "L2": {
            "similarity_threshold": 0.80,
            "ttl_seconds": 1800,  # 30분 (감정 컨텍스트 변화 고려)
            "enabled": True
        },
        "L3": {
            "similarity_threshold": 0.90,  # 분석은 정확도 중요
            "ttl_seconds": 7200,  # 2시간
            "enabled": True
        },
        "L4": {
            "similarity_threshold": 0.95,  # 코드는 매우 정확해야 함
            "ttl_seconds": 86400,  # 24시간
            "enabled": True
        }
    }

    def __init__(self, cache_dir: str = "./cache"):
        self.onnx_encoder = Onnx()

        # 벡터 저장소: SQLite + Faiss
        self.data_manager = get_data_manager(
            CacheBase("sqlite", sql_url=f"sqlite:///{cache_dir}/cache.db"),
            VectorBase("faiss", dimension=self.onnx_encoder.dimension)
        )

        self.cache = Cache()
        self.cache.init(
            embedding_func=self.onnx_encoder.to_embeddings,
            data_manager=self.data_manager,
            similarity_evaluation=SearchDistanceEvaluation()
        )

        self._stats = {"hits": 0, "misses": 0}

    def get(self, query: str, level: str, user_id: str = None) -> tuple[str, bool]:
        """
        캐시 조회

        Returns:
            (response, is_hit)
        """
        policy = self.LEVEL_POLICIES.get(level, self.LEVEL_POLICIES["L2"])

        if not policy["enabled"]:
            return None, False

        # 캐시 키: 레벨 + 쿼리 (사용자별 분리 옵션)
        cache_key = f"{level}:{query}"

        result = self.cache.get(cache_key)

        if result is not None:
            self._stats["hits"] += 1
            return result, True

        self._stats["misses"] += 1
        return None, False

    def set(self, query: str, response: str, level: str, user_id: str = None):
        """캐시 저장"""
        cache_key = f"{level}:{query}"
        self.cache.set(cache_key, response)

    @property
    def hit_rate(self) -> float:
        total = self._stats["hits"] + self._stats["misses"]
        return self._stats["hits"] / max(total, 1)
```

#### 2.2 ChatEngine 캐시 통합

```python
# chat_engine.py
async def get_response(self, user_id: int, text: str, ...):
    # [CACHE CHECK] 시맨틱 캐시 조회
    cached_response, is_hit = self._semantic_cache.get(text, level, str(user_id))

    if is_hit:
        logger.info(f"⚡ Cache HIT for level {level}")
        return f"{cached_response}\n\n_⚡ Cached Response_"

    # ... LLM 호출 ...

    # [CACHE STORE] 성공 시 캐시 저장
    if response_text:
        self._semantic_cache.set(text, response_text, level, str(user_id))
```

---

### Phase 3: 품질 평가 시스템 (2주)

> **목표**: 자동 품질 측정, quality_score 동적 산출

#### 3.1 DeepEval 통합 (pytest 호환)

```python
# projects/ddc/brain/neuronet/quality_evaluator.py
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
    HallucinationMetric
)
from deepeval.test_case import LLMTestCase
import asyncio

class DCNSQualityEvaluator:
    """
    D-CNS 응답 품질 실시간 평가 엔진
    - DeepEval 메트릭 기반
    - 레벨별 가중치 차별화
    """

    # 레벨별 메트릭 가중치
    LEVEL_METRIC_WEIGHTS = {
        "L1": {
            "relevancy": 0.6,      # 관련성 중요
            "conciseness": 0.4,   # 간결함 중요
        },
        "L2": {
            "relevancy": 0.3,
            "empathy": 0.5,       # 공감도 중요
            "tone": 0.2,
        },
        "L3": {
            "faithfulness": 0.4,  # 사실 정확성
            "relevancy": 0.3,
            "depth": 0.3,         # 분석 깊이
        },
        "L4": {
            "correctness": 0.5,   # 코드 정확성
            "completeness": 0.3,
            "relevancy": 0.2,
        }
    }

    def __init__(self, eval_model: str = "gpt-4o-mini"):
        self.eval_model = eval_model

        # 기본 메트릭 초기화
        self.relevancy_metric = AnswerRelevancyMetric(
            model=eval_model,
            threshold=0.7
        )
        self.faithfulness_metric = FaithfulnessMetric(
            model=eval_model,
            threshold=0.7
        )
        self.hallucination_metric = HallucinationMetric(
            model=eval_model,
            threshold=0.5
        )

    async def evaluate(
        self,
        query: str,
        response: str,
        context: str,
        level: str
    ) -> dict:
        """
        응답 품질 평가

        Returns:
            {
                "overall_score": 0.0-1.0,
                "metrics": {...},
                "feedback": str,
                "pass": bool
            }
        """
        test_case = LLMTestCase(
            input=query,
            actual_output=response,
            context=[context] if context else None
        )

        # 비동기 평가 실행
        scores = {}

        try:
            # 관련성 평가
            self.relevancy_metric.measure(test_case)
            scores["relevancy"] = self.relevancy_metric.score

            # 환각 평가 (context 있을 때만)
            if context:
                self.faithfulness_metric.measure(test_case)
                scores["faithfulness"] = self.faithfulness_metric.score

                self.hallucination_metric.measure(test_case)
                scores["hallucination"] = 1.0 - self.hallucination_metric.score
        except Exception as e:
            logger.warning(f"Evaluation error: {e}")
            scores = {"relevancy": 0.7, "faithfulness": 0.7}

        # 레벨별 가중 평균
        weights = self.LEVEL_METRIC_WEIGHTS.get(level, {"relevancy": 1.0})
        overall = sum(
            scores.get(metric, 0.7) * weight
            for metric, weight in weights.items()
        )

        return {
            "overall_score": min(overall, 1.0),
            "metrics": scores,
            "level": level,
            "pass": overall >= 0.6
        }
```

#### 3.2 Neuroplasticity 연동

```python
# neuroplasticity.py 수정
def record_interaction(
    self,
    user_id: str,
    model_id: str,
    context: dict,
    latency_ms: float,
    quality_score: float = None,  # [CHANGE] Optional로 변경
    tokens_used: int = 0,
    evaluation_result: dict = None,  # [NEW] 평가 결과 직접 전달
    ...
):
    # 평가 결과가 있으면 해당 점수 사용
    if evaluation_result:
        quality_score = evaluation_result.get("overall_score", 0.8)
    elif quality_score is None:
        quality_score = 0.8  # 기본값

    # ... 기존 학습 로직 ...
```

---

### Phase 4: DSPy 프롬프트 최적화 (2주)

> **목표**: 프롬프트 자동 튜닝, 정확도 +15%

#### 4.1 DSPy Signature 정의

```python
# projects/ddc/brain/brain_core/prompt_optimizer.py
import dspy

class BioQASignature(dspy.Signature):
    """생물학 질의응답 시그니처"""
    question: str = dspy.InputField(desc="사용자의 생물학 관련 질문")
    context: str = dspy.InputField(desc="관련 메모리/문서 컨텍스트", default="")
    answer: str = dspy.OutputField(desc="과학적으로 정확한 한국어 답변")

class EmpatheticResponseSignature(dspy.Signature):
    """공감적 응답 시그니처 (L2)"""
    user_message: str = dspy.InputField()
    emotion: str = dspy.InputField(desc="감지된 감정 (joy, sadness, etc.)")
    intensity: float = dspy.InputField(desc="감정 강도 0-1")
    response: str = dspy.OutputField(desc="공감적이고 supportive한 응답")

class CodeGenerationSignature(dspy.Signature):
    """코드 생성 시그니처 (L4)"""
    requirement: str = dspy.InputField(desc="코드 요구사항")
    language: str = dspy.InputField(desc="프로그래밍 언어", default="python")
    code: str = dspy.OutputField(desc="실행 가능한 코드")
    explanation: str = dspy.OutputField(desc="코드 설명")


class DCNSPromptOptimizer:
    """D-CNS 프롬프트 자동 최적화 엔진"""

    def __init__(self, teacher_model: str = "gpt-4o"):
        # DSPy LM 설정
        self.lm = dspy.LM(f"openai/{teacher_model}")
        dspy.configure(lm=self.lm)

        # 레벨별 모듈
        self.modules = {
            "L1": dspy.ChainOfThought(BioQASignature),  # 빠른 CoT
            "L2": dspy.ChainOfThought(EmpatheticResponseSignature),
            "L3": dspy.ChainOfThought(BioQASignature),
            "L4": dspy.ChainOfThought(CodeGenerationSignature),
        }

        self.optimized_modules = {}

    def optimize_for_level(
        self,
        level: str,
        training_data: list,  # [{"question": ..., "answer": ...}, ...]
        metric_fn: callable = None
    ):
        """
        레벨별 프롬프트 최적화 (MIPROv2)

        Args:
            level: L1-L4
            training_data: 학습 데이터셋 (최소 30개 권장)
            metric_fn: 커스텀 메트릭 함수
        """
        from dspy.teleprompt import MIPROv2

        if metric_fn is None:
            metric_fn = self._default_metric

        teleprompter = MIPROv2(
            metric=metric_fn,
            num_candidates=10,
            init_temperature=0.7,
            verbose=True
        )

        # 최적화 실행
        optimized = teleprompter.compile(
            self.modules[level],
            trainset=training_data
        )

        self.optimized_modules[level] = optimized
        return optimized

    def _default_metric(self, example, prediction, trace=None):
        """기본 메트릭: 관련성 + 길이 적정성"""
        # 관련성 체크 (키워드 기반 간이 평가)
        relevancy = 0.8 if any(
            kw in prediction.answer.lower()
            for kw in example.question.lower().split()[:3]
        ) else 0.5

        # 길이 적정성 (너무 짧거나 길지 않은지)
        length_score = 1.0 if 50 < len(prediction.answer) < 1000 else 0.6

        return (relevancy + length_score) / 2
```

---

### Phase 5: 자기학습 피드백 루프 (2주)

> **목표**: 24/7 자동 개선, 인간 개입 최소화

#### 5.1 Continuous Learning Pipeline

```python
# projects/ddc/brain/neuronet/self_learning_loop.py
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio

class SelfLearningLoop:
    """
    D-CNS 자기학습 순환 시스템

    사이클:
    1. 상호작용 수집 →
    2. 품질 평가 →
    3. 저품질 식별 →
    4. 프롬프트 재최적화 →
    5. A/B 테스트 →
    6. 배포
    """

    def __init__(self, db_path: str = "./data/learning.db"):
        self.db_path = db_path
        self._init_database()

        # 의존 모듈
        self.evaluator = None  # DCNSQualityEvaluator
        self.optimizer = None  # DCNSPromptOptimizer

        # 학습 임계값
        self.POOR_QUALITY_THRESHOLD = 0.6
        self.REOPTIMIZE_BATCH_SIZE = 30
        self.REOPTIMIZE_INTERVAL_HOURS = 24

    def _init_database(self):
        """SQLite 스키마 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                level TEXT,
                query TEXT,
                response TEXT,
                model_id TEXT,
                latency_ms REAL,
                quality_score REAL,
                evaluation_json TEXT,
                is_positive_feedback INTEGER DEFAULT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                level TEXT,
                improvement_pct REAL,
                training_samples INTEGER,
                notes TEXT
            )
        ''')

        conn.commit()
        conn.close()

    async def record_interaction(
        self,
        user_id: str,
        level: str,
        query: str,
        response: str,
        model_id: str,
        latency_ms: float,
        quality_score: float,
        evaluation_json: str = None
    ):
        """상호작용 기록"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO interactions
            (user_id, level, query, response, model_id, latency_ms, quality_score, evaluation_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, level, query, response, model_id, latency_ms, quality_score, evaluation_json))

        conn.commit()
        conn.close()

    async def identify_poor_interactions(self, level: str, hours: int = 24) -> List[Dict]:
        """저품질 상호작용 식별"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)

        cursor.execute('''
            SELECT query, response, quality_score
            FROM interactions
            WHERE level = ?
              AND quality_score < ?
              AND timestamp > ?
            ORDER BY quality_score ASC
            LIMIT 100
        ''', (level, self.POOR_QUALITY_THRESHOLD, since.isoformat()))

        results = [
            {"query": row[0], "response": row[1], "quality_score": row[2]}
            for row in cursor.fetchall()
        ]

        conn.close()
        return results

    async def run_learning_cycle(self):
        """
        학습 사이클 실행 (주기적 호출)

        권장: 매 24시간 또는 100개 상호작용마다
        """
        for level in ["L1", "L2", "L3", "L4"]:
            # 1. 저품질 상호작용 수집
            poor_interactions = await self.identify_poor_interactions(level)

            if len(poor_interactions) < self.REOPTIMIZE_BATCH_SIZE:
                logger.info(f"[{level}] 충분한 학습 데이터 없음 ({len(poor_interactions)}개)")
                continue

            logger.info(f"[{level}] {len(poor_interactions)}개 저품질 상호작용 발견, 재최적화 시작")

            # 2. 좋은 예시와 혼합하여 학습 데이터 구성
            good_interactions = await self._get_good_interactions(level)
            training_data = self._prepare_training_data(poor_interactions, good_interactions)

            # 3. DSPy 재최적화
            if self.optimizer:
                optimized = self.optimizer.optimize_for_level(level, training_data)

                # 4. 개선율 측정
                improvement = await self._measure_improvement(level, optimized)

                # 5. 기록
                self._record_optimization(level, improvement, len(training_data))

                logger.info(f"[{level}] 최적화 완료: {improvement:.1%} 개선")

    async def _get_good_interactions(self, level: str, limit: int = 50) -> List[Dict]:
        """고품질 상호작용 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT query, response, quality_score
            FROM interactions
            WHERE level = ? AND quality_score >= 0.8
            ORDER BY quality_score DESC
            LIMIT ?
        ''', (level, limit))

        results = [
            {"query": row[0], "response": row[1], "quality_score": row[2]}
            for row in cursor.fetchall()
        ]

        conn.close()
        return results
```

#### 5.2 실시간 피드백 수집

```python
# chat_engine.py에 추가
class ChatEngine:
    async def record_user_feedback(
        self,
        interaction_id: int,
        is_positive: bool,
        feedback_text: str = None
    ):
        """
        사용자 피드백 기록 (thumbs up/down)

        이 데이터는 학습 루프에서 가중치로 사용됨
        """
        await self._learning_loop.record_feedback(
            interaction_id, is_positive, feedback_text
        )

        # 즉시 Neuroplasticity 반영
        quality_boost = 0.1 if is_positive else -0.1
        self.learner.adjust_quality_score(interaction_id, quality_boost)
```

---

### Phase 6: Observability & 모니터링 (1주)

> **목표**: 분산 추적, 실시간 대시보드

#### 6.1 Langfuse 통합

```python
# projects/ddc/utilities/observability.py
from langfuse import Langfuse
from langfuse.decorators import observe
import os

class DCNSObservability:
    """
    D-CNS 관측성 레이어
    - 분산 추적 (OpenTelemetry 호환)
    - 비용 추적
    - 지연 분석
    """

    def __init__(self):
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )

    def trace_request(self, user_id: str, session_id: str = None):
        """요청 추적 시작"""
        return self.langfuse.trace(
            name="dcns_request",
            user_id=user_id,
            session_id=session_id,
            metadata={"version": "v6.0"}
        )

    def log_generation(
        self,
        trace,
        model_id: str,
        prompt: str,
        response: str,
        latency_ms: float,
        tokens: int,
        level: str
    ):
        """LLM 생성 로깅"""
        trace.generation(
            name=f"dcns_{level}_generation",
            model=model_id,
            input=prompt,
            output=response,
            usage={
                "total_tokens": tokens,
                "latency_ms": latency_ms
            },
            metadata={
                "level": level,
                "engine": model_id.split("-")[0] if "-" in model_id else "unknown"
            }
        )

    def log_score(self, trace, quality_score: float, evaluation: dict):
        """품질 점수 기록"""
        trace.score(
            name="quality",
            value=quality_score,
            comment=str(evaluation)
        )
```

#### 6.2 Prometheus 메트릭

```python
# projects/ddc/utilities/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 요청 카운터
REQUESTS_TOTAL = Counter(
    'dcns_requests_total',
    'Total requests by level and engine',
    ['level', 'engine', 'status']
)

# 지연 히스토그램
LATENCY_HISTOGRAM = Histogram(
    'dcns_latency_seconds',
    'Request latency by level',
    ['level'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# 캐시 히트율 게이지
CACHE_HIT_RATE = Gauge(
    'dcns_cache_hit_rate',
    'Semantic cache hit rate'
)

# 품질 점수 게이지
QUALITY_SCORE = Gauge(
    'dcns_quality_score_avg',
    'Average quality score by level',
    ['level']
)
```

---

## 🏗️ 최종 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Digital Da Vinci D-CNS v6.0                          │
│                   (Self-Evolving Cognitive Router)                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  [1] SEMANTIC ROUTER (Aurelio)  │  <10ms Routing                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │  L1 Routes   │ │  L2 Routes   │ │  L3 Routes   │ │  L4 Routes   │   │
│  │  (Reflexive) │ │  (Affective) │ │  (Cognitive) │ │  (NeuroNet)  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  [2] SEMANTIC CACHE (GPTCache)  │  40%+ Hit Rate                        │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Query Embedding → Vector Search → Similarity Check → Cache Hit │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                    Cache Miss ↓                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  [3] PROMPT OPTIMIZER (DSPy)    │  Auto-Tuned Prompts                   │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Level-Specific Signatures → MIPROv2 Optimization → Few-Shot   │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  [4] NEUROPLASTICITY LEARNER    │  6D Multi-Criteria Selection          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Speed │ Quality │ Token Eff │ Cost │ Memory │ Reliability     │    │
│  │   ↓         ↓         ↓        ↓       ↓          ↓            │    │
│  │  [Weighted Sum by Level] → Ranked Models → Cascading Execution │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  [5] LLM PROVIDERS (LiteLLM Unified)                                    │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │Gemini│ │ Groq │ │Claude│ │DeepSk│ │Cerebs│ │Mistrl│ │OpenAI│       │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  [6] QUALITY EVALUATOR (DeepEval)│  Real-time Assessment                │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Relevancy │ Faithfulness │ Hallucination │ Empathy (L2)       │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  [7] SELF-LEARNING LOOP         │  24/7 Continuous Improvement          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Record → Evaluate → Identify Poor → Re-Optimize → A/B Test    │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  [8] OBSERVABILITY (Langfuse + Prometheus)                              │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Distributed Tracing │ Cost Tracking │ Latency Analysis        │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 기대 효과 (벤치마크 기반)

| 지표 | 현재 (v5.5) | 목표 (v6.0) | 근거 |
|------|------------|------------|------|
| **라우팅 지연** | 50-100ms (rule) | <10ms | Semantic Router 벤치마크 |
| **캐시 히트율** | 0% | 40-68% | GPTCache 논문 (threshold 0.8) |
| **응답 지연 (cache hit)** | N/A | 2-10x 감소 | GPTCache 공식 문서 |
| **품질 점수 정확도** | 고정값 0.8 | 동적 측정 | DeepEval 메트릭 |
| **프롬프트 효과** | 수동 튜닝 | +15% 정확도 | DSPy MIPROv2 논문 |
| **비용 절감** | 기본 | 50-85% | RouteLLM 논문 (model routing) |

---

## 🔧 설치 및 의존성

```bash
# 핵심 패키지
pip install semantic-router        # Phase 1: Semantic Router
pip install gptcache faiss-cpu    # Phase 2: Semantic Cache
pip install deepeval              # Phase 3: Quality Evaluation
pip install dspy-ai               # Phase 4: Prompt Optimization
pip install langfuse              # Phase 6: Observability
pip install prometheus-client     # Phase 6: Metrics

# 선택적 (고급)
pip install litellm               # 통합 LLM 게이트웨이
pip install promptfoo             # A/B 테스트 (CLI)
```

---

## 📚 참고 자료

### 오픈소스 프로젝트
- [Semantic Router (Aurelio Labs)](https://github.com/aurelio-labs/semantic-router) - <10ms 의도 라우팅
- [vLLM Semantic Router](https://github.com/vllm-project/semantic-router) - 클라우드 네이티브 라우팅
- [GPTCache](https://github.com/zilliztech/GPTCache) - 시맨틱 캐시
- [DSPy (Stanford)](https://github.com/stanfordnlp/dspy) - 프로그래밍 방식 프롬프트 최적화
- [DeepEval](https://github.com/confident-ai/deepeval) - LLM 평가 프레임워크
- [RouteLLM (LMSYS)](https://github.com/lm-sys/RouteLLM) - 비용 효율적 라우팅
- [Langfuse](https://github.com/langfuse/langfuse) - LLM 관측성
- [LiteLLM](https://github.com/BerriAI/litellm) - 통합 LLM 게이트웨이

### 연구 논문
- **Router-R1** (NeurIPS 2025) - RL 기반 다중 LLM 라우팅
- **RouteLLM** (ICLR 2025) - 선호 데이터 기반 라우터 학습
- **DSPy MIPROv2** - Bayesian 프롬프트 최적화
- **GenerativeCache** - GPTCache 9x 성능 개선

### 상용 서비스 (참고)
- [Not Diamond](https://www.notdiamond.ai/) - 커스텀 라우터 학습
- [Martian](https://withmartian.com/) - 실시간 최적 모델 선택
- [OpenRouter Auto Router](https://openrouter.ai/) - NotDiamond 기반

---

## 🚀 실행 계획 요약

| 주차 | Phase | 작업 | 산출물 |
|-----|-------|------|--------|
| 1주 | Phase 1 | Semantic Router 통합 | `semantic_router.py` |
| 2주 | Phase 2 | Semantic Cache 구축 | `semantic_cache.py` |
| 3-4주 | Phase 3 | DeepEval 품질 평가 | `quality_evaluator.py` |
| 5-6주 | Phase 4 | DSPy 프롬프트 최적화 | `prompt_optimizer.py` |
| 7-8주 | Phase 5 | Self-Learning Loop | `self_learning_loop.py` |
| 9주 | Phase 6 | Observability 통합 | `observability.py`, `metrics.py` |

---

**이 전략은 최신 연구와 오픈소스 도구들의 벤치마크 데이터를 기반으로 설계되었습니다.**
