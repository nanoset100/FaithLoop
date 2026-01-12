# 믿음루프(FaithLoop) ✝️

> AI+RAG 신앙일기 - 결단·기도·적용을 누적하고, 근거 기반으로 나를 보며 작은 실천을 지속합니다.

**믿음루프(FaithLoop)**는 감사/기도/말씀/적용/방해요인을 매일 기록하고, AI가 과거 기록을 참조하여 신앙 성장을 돕는 앱입니다.

> ⚠️ 이 앱은 목회상담/의료를 대체하지 않으며, 기록 기반 성찰과 루틴 형성을 돕습니다.

## 핵심 기능

- 📝 **멀티모달 입력**: 텍스트, 이미지, 음성으로 신앙 기록
- 🧠 **RAG 기반 기억검색**: AI가 과거 기록을 참조하여 근거 기반 인사이트 제공
- 📊 **주간 성장 리포트**: 감사 하이라이트, 방해요인 패턴, 결단/적용 진행 분석
- 📅 **다음 한 걸음**: 말씀묵상/기도/공동체 루틴 제안
- 🔗 **Google Calendar 연동**: 신앙 루틴 일정 동기화

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Streamlit (multipage) |
| Database | Supabase Postgres + pgvector |
| Storage | Supabase Storage |
| AI | OpenAI (GPT-4, Embeddings, Whisper) |
| Calendar | Google Calendar API (OAuth2) |

## 설치 및 실행

### 1. 가상환경 생성

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. Secrets 설정

`.streamlit/secrets.toml` 파일을 생성하고 필요한 키를 설정합니다:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# 이후 secrets.toml을 편집하여 실제 키 입력
```

### 4. Supabase 스키마 적용

Supabase 대시보드 SQL Editor에서 `sql/schema.sql` 실행

### 5. 앱 실행

```bash
streamlit run reflectos/app.py
```

## 폴더 구조

```
/reflectos
  app.py              # 메인 엔트리
  /pages              # Streamlit 멀티페이지
    1_Home.py
    2_Checkin.py
    3_Report.py
    4_Planner.py
    5_Memory.py
    6_Settings.py
  /lib                # 유틸리티 모듈
    config.py         # 설정 로드
    supabase_db.py    # DB CRUD 헬퍼
    supabase_storage.py
    openai_client.py
    rag.py
    calendar_google.py
    prompts.py
    utils.py
  /sql
    schema.sql        # DB 스키마
  requirements.txt
  .streamlit/
    secrets.toml.example
```

## 개발 로드맵

- [x] Step 0: 프로젝트 부팅
- [x] Step 1: Supabase 연결 + 스키마
- [ ] Step 2: 체크인 입력 (텍스트)
- [ ] Step 3: 멀티모달 입력 (이미지/음성)
- [ ] Step 4: RAG 기반 회고
- [ ] Step 5: 주간 리포트
- [ ] Step 6: 시간블록 플래너
- [ ] Step 7: Google Calendar 연동

