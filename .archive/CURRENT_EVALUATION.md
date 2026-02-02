# 🧠 Shawn Brain (v5.1.0) 상세 평가 및 개선 제안서

## 1. 📊 종합 평가 요약

**"강력한 DDC 코어, 그러나 혼란스러운 외피 (Dual Structural State)"**

현재 Shawn Brain은 `ddc/` 디렉토리를 중심으로 한 신규 아키텍처(v5.1.0)와, 루트 디렉토리에 산재한 레거시 파일/폴더가 공존하는 **과도기적 상태**입니다. 기능적으로는 "Production Ready"에 도달했으나, 프로젝트 구조 측면에서는 정리가 시급합니다.

| 평가 항목 | 점수 | 상태 | 비고 |
| :--- | :--- | :--- | :--- |
| **핵심 아키텍처 (DDC)** | **9.6/10** | 🟢 우수 | 4계층 신경망, 5개 카트리지 구조 명확함 |
| **디렉토리 구조** | **4.2/10** | 🔴 위험 | 루트에 156개 파일 방치, 레거시 폴더 중복 |
| **문서화** | **6.5/10** | 🟡 보통 | 내용은 풍부하나, 30여 개 파일이 루트에 난립 |
| **실행 명확성** | **5.0/10** | 🟡 혼란 | `run_telegram_bot.py` vs `ddc/main.py` 혼재 |

---

## 2. 🚨 주요 문제점 분석 (What & Why)

### A. 이중 아키텍처 (Structural Duplication)
- **현상**: `ddc/brain` (신규)과 루트의 `brain_core`, `neocortex` (구형)가 동시에 존재.
- **Why it matters**: 
  - 개발 시 어느 파일을 수정해야 할지 혼란 초래.
  - 구형 스크립트 실행 시 구형 로직이 작동하여 데이터 불일치 발생 가능성.
  - `Import` 경로 꼬임의 원인.

### B. 루트 디렉토리 오염 (Root Pollution)
- **현상**: 루트에 156개의 파일 및 디렉토리 존재.
  - **문서**: `MASTER_PLAN_2026.md`, `PHASE_*.md` 등 각종 보고서 산재.
  - **스크립트**: `daily_*.py`, `task_*.py` 등 50여 개 Python 스크립트가 정리되지 않음.
  - **로그**: `shawn-bot.log`, `bot.log` 등 대용량 로그 파일이 루트에 방치.
- **Why it matters**: 프로젝트 진입 장벽을 높이고, Git 관리를 어렵게 함.

### C. 실행 진입점 모호성
- **현상**: `docker-compose.yml`은 존재하나, 로컬 실행 시 `python run_telegram_bot.py`를 써야 하는지, `uvicorn ddc.web.app:app`을 써야 하는지 불분명.
- **Why it matters**: 배포 및 유지보수 일관성 저하.

---

## 3. 🛠️ 개선 로드맵 (Action Plan)

### Step 1: 과감한 격리 (The Great Purge)
루트 디렉토리의 레거시 요소들을 `.archive` 또는 적절한 하위 폴더로 즉시 이동시켜야 합니다.

**[파일 이동 계획]**
- `brain_core/`, `neocortex/`, `engines/`, `tools/` (Root) → `.archive/legacy_v4_root/`
- `*.md` (README 제외) → `docs/reports/` 또는 `docs/archive/`
- `*.log`, `*.pid` → `logs/` (폴더 생성 및 .gitignore 확인)
- `daily_*.py`, `task_*.py` → `scripts/maintenance/`

### Step 2: DDC 체제 확립 (Single Source of Truth)
- 모든 실행 스크립트가 `ddc` 패키지를 참조하도록 강제.
- 루트의 `requirements.txt`가 `ddc` 의존성을 정확히 반영하는지 확인.

### Step 3: 진입점 통일 (Unified Entry Point)
- `manage.py` 또는 `run.py` 하나만 루트에 남기고, 내부에서 `ddc.bot` 또는 `ddc.web`을 호출하도록 구조화.
- 사용하지 않는 `run_telegram_bot.py` 등은 삭제 또는 아카이브.

---

## 4. 🚀 결론
Shawn Brain은 **"이사 짐은 다 쌌지만, 옛날 가구를 아직 버리지 않은 새 집"**과 같습니다. 
`ddc`라는 훌륭한 코어가 준비되어 있으므로, **"청소(Cleanup)"**만 수행하면 시스템의 가치는 즉시 100%로 상승할 것입니다.
