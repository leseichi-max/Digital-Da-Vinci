# HEARTBEAT.md - 주기적 체크 작업

## 🤖 기존 기능 체크 설정

### 매 세션 시작할 때 자동 체크

새로운 기능을 만들기 전에 **반드시** 이미 있는 기능을 확인하세요!

```bash
# 빠른 체크 방법
./scripts/before_development.sh "<기능명>"

# 예시
./scripts/before_development.sh "신경계 추적"
./scripts/before_development.sh "API 트래킹"
./scripts/before_development.sh "Q-Learning"
```

### Python에서 직접 검색

```python
from check_existing_features import FeatureChecker

checker = FeatureChecker()

# 기능 검색
results = checker.check_feature("신경계 추적", "신경계별 모델 효율 추적")

# 모든 기능 보기
checker.list_all_features()
```

---

## 📋 기존 기능 목록 (항상 확인!)

### 신경계 추적
- **neural_system_efficiency_analysis.py**: L1-L4 신경계 모델 할당 & 효율성 분석
  - L1 뇌간: Groq (9.6/10)
  - L2 변연계: Gemini (9.5/10)
  - L3 신피질: 4개 엽 (9.4/10)
  - L4 신경망: 신경신호 라우팅 (9.8/10)
  - 사용: `python3 projects/ddc/brain/neuronet/neural_system_efficiency_analysis.py`

### API 추적
- **api_tracker_unified.py**: 통합 API 추적 (10개 모델)
- **groq_usage_tracker.py**: Groq 특화 추적
- **model_usage_tracker.py**: 모델별 사용량

### 강화학습
- **shawn_bot_watchdog_v2.py**: Watchdog Q-Learning 신경학습
  - ProcessState, NeuralLearner, RewardCalculator, QualityScorer
  - 사용: `python3 systems/bot/shawn_bot_watchdog_v2.py`

### 신경라우팅
- **neural_router.py**: NeuralModelRouter 기반 라우팅
- **work_tracker.py**: 작업 효율 추적

### 신경계 시스템
- **adaptive_neural_system.py**: 적응형 신경계 시스템
- **neural_executor.py**: 신경계 기반 작업 실행

---

## ✅ 개발 전 체크리스트 (매번!)

새로운 기능을 만들기 전에:

- [ ] **Step 1**: 기능명을 명확히 정의
- [ ] **Step 2**: `./scripts/before_development.sh "<기능명>"` 실행
- [ ] **Step 3**: 검색 결과 확인
  - ✅ 이미 있고 충분하면 → **기존 코드 사용**
  - ⚠️ 있지만 부족하면 → **기존 코드 확장**
  - ❌ 없으면 → **새로 만들기**
- [ ] **Step 4**: 개발 시작
- [ ] **Step 5**: 완성 후 `check_existing_features.py`에 등록

---

## 🚀 매주 업데이트

매주 금요일마다:
- [ ] 새로운 기능들 DB에 등록
- [ ] 문서 업데이트
- [ ] 중복 기능 정리

---

## 💾 사용 예시

### 예시 1: 신경계 효율 추적 만들려면?

```bash
$ ./scripts/before_development.sh "신경계 효율 추적"

✅ 이미 있습니다!
📦 neural_system_efficiency_analysis.py
   사용: python3 projects/ddc/brain/neuronet/neural_system_efficiency_analysis.py
```

→ **이미 있으므로 이것을 사용!**

### 예시 2: API 트래킹 추가 기능?

```bash
$ ./scripts/before_development.sh "실시간 API 모니터링"

⚠️  유사한 기능들:
1. api_tracker_unified.py
2. groq_usage_tracker.py
3. model_usage_tracker.py
```

→ **이들을 먼저 확인하고 확장하기**

### 예시 3: 완전 새로운 기능?

```bash
$ ./scripts/before_development.sh "대시보드 시각화"

✨ 새로운 기능입니다!
```

→ **새로 만들어도 되지만, 한 번 더 확인하기!**

---

## 🎯 핵심

**"만들기 전에 체크하자!"**
- 5초의 검색 > 1시간의 중복 개발
- 기존 코드 이해 → 확장/수정 → 최고 효율!

