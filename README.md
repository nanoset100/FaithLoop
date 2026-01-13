# 믿음루프(FaithLoop) ✝️

> AI+RAG 신앙일기 - 결단·기도·적용을 누적하고, 근거 기반으로 나를 보며 작은 실천을 지속합니다.

**믿음루프(FaithLoop)**는 감사/기도/말씀/적용/방해요인을 매일 기록하고, AI가 과거 기록을 참조하여 신앙 성장을 돕는 웹 애플리케이션입니다.

> ⚠️ **면책 조항**: 이 앱은 목회상담/의료를 대체하지 않으며, 기록 기반 성찰과 루틴 형성을 돕는 도구입니다.

---

## 📋 목차

- [핵심 기능](#핵심-기능)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [설치 및 실행](#설치-및-실행)
- [환경 설정](#환경-설정)
- [주요 기능 상세](#주요-기능-상세)
- [데이터베이스](#데이터베이스)
- [개발 로드맵](#개발-로드맵)
- [문제 해결](#문제-해결)

---

## 🎯 핵심 기능

### 1. 📝 멀티모달 신앙 기록
- **텍스트 입력**: 감사/말씀/적용/방해요인을 자유롭게 기록
- **음성 입력**: 음성 파일 업로드 시 OpenAI Whisper로 자동 전사
- **이미지 입력**: 이미지 업로드 시 OpenAI Vision API로 내용 분석
- **AI 구조화**: LLM 기반으로 기록 내용을 구조화된 데이터로 추출 (tasks, obstacles, insights 등)

### 2. 🧠 RAG 기반 기억검색
- **벡터 검색**: pgvector를 활용한 의미 기반 검색
- **근거 기반 답변**: 과거 기록을 참조하여 정확한 답변 제공
- **컨텍스트 표시**: AI가 참조한 원본 기록 표시

### 3. 📊 주간 성장 리포트
- **AI 분석**: 주간 신앙 기록을 분석하여 성장 패턴 파악
- **감사 하이라이트**: 이번 주 감사한 내용 요약
- **방해요인 패턴**: 반복되는 방해요인 식별
- **결단/적용 추적**: 설교 적용 및 실천 내용 분석

### 4. 📖 설교노트
- **설교 요약**: 주일 설교 요약 및 본문 확인
- **나의 적용**: 설교를 바탕으로 한 개인 적용 작성 및 저장
- **관리자 기능**: 설교 등록 및 발행 (관리자 전용)

### 5. 🙏 기도노트
- **기도제목 등록**: 가족, 건강, 사역, 직장 등 카테고리별 기도제목 관리
- **응답 추적**: 기도 응답 기록 및 통계 확인
- **상태 관리**: 기도 중 / 응답됨 / 진행 중 상태 관리

### 6. 📅 Google Calendar 연동
- **일정 동기화**: 오늘 일정을 Home 대시보드에서 확인
- **OAuth2 인증**: 안전한 Google 계정 연동

### 7. 🔐 사용자 인증
- **Supabase Auth**: 이메일/비밀번호 기반 회원가입 및 로그인
- **초대코드 시스템**: 파일럿 100명용 초대코드 관리
- **프로필 관리**: 사용자 프로필 및 설정 관리

---

## 🛠 기술 스택

| 영역 | 기술 | 버전 |
|------|------|------|
| **Frontend** | Streamlit | ≥1.31.0 |
| **Database** | Supabase PostgreSQL + pgvector | - |
| **Storage** | Supabase Storage | - |
| **Authentication** | Supabase Auth | - |
| **AI/ML** | OpenAI (GPT-4, Embeddings, Whisper, Vision) | ≥1.12.0 |
| **Calendar** | Google Calendar API (OAuth2) | ≥2.100.0 |
| **Language** | Python | 3.10+ |

### 주요 라이브러리
- `supabase`: Supabase 클라이언트
- `openai`: OpenAI API 클라이언트
- `google-api-python-client`: Google Calendar API
- `pandas`, `numpy`: 데이터 처리
- `pydub`: 오디오 처리
- `Pillow`: 이미지 처리

---

## 📁 프로젝트 구조

```
FaithLoop/
├── app.py                      # 메인 엔트리 포인트 (로그인/회원가입)
├── requirements.txt            # Python 의존성 패키지
├── README.md                   # 프로젝트 문서
├── 사용설명서.md              # 사용자 가이드
│
├── pages/                      # Streamlit 멀티페이지
│   ├── 1_Home.py              # 홈 대시보드
│   ├── 2_Sermon.py            # 설교노트
│   ├── 3_Checkin.py           # 오늘의 기록 (멀티모달)
│   ├── 4_Prayer.py            # 기도노트
│   ├── 5_Report.py            # 주간 성장 리포트
│   ├── 6_Memory.py            # 기억검색 (RAG)
│   ├── 7_Settings.py          # 설정
│   └── 8_Sermon_Admin.py      # 설교 관리자 (관리자 전용)
│
├── lib/                        # 핵심 모듈
│   ├── config.py              # 설정 관리 (secrets 로드)
│   ├── supabase_db.py         # Supabase DB CRUD 헬퍼
│   ├── supabase_storage.py    # Supabase Storage 업로드
│   ├── openai_client.py       # OpenAI API 클라이언트
│   ├── rag.py                 # RAG 검색 및 인덱싱
│   ├── calendar_google.py     # Google Calendar 연동
│   ├── prompts.py             # AI 프롬프트 템플릿
│   ├── utils.py               # 유틸리티 함수
│   └── demo_data.py           # 데모 데이터 생성
│
├── sql/                        # 데이터베이스 스키마
│   └── schema.sql             # PostgreSQL 스키마 (테이블, RLS, 함수)
│
├── scripts/                    # 유틸리티 스크립트
│   └── setup_storage.py       # Storage 버킷 설정
│
└── .streamlit/                 # Streamlit 설정
    └── secrets.toml            # 환경 변수 (gitignore)
```

---

## 🚀 설치 및 실행

### 1. 사전 요구사항

- Python 3.10 이상
- Supabase 프로젝트 (PostgreSQL + Storage + Auth)
- OpenAI API 키
- Google Cloud 프로젝트 (Calendar API 사용 시, 선택사항)

### 2. 저장소 클론

```bash
git clone <repository-url>
cd FaithLoop
```

### 3. 가상환경 생성 및 활성화

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. 의존성 설치

```bash
pip install -r requirements.txt
```

### 5. 환경 변수 설정

`.streamlit/secrets.toml` 파일을 생성하고 다음 내용을 입력하세요:

```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"

[openai]
api_key = "sk-..."

[google]
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "your-client-secret"
redirect_uri = "http://localhost:8501"

[app]
debug = false
default_timezone = "Asia/Seoul"
```

> ⚠️ **보안 주의**: `secrets.toml` 파일은 절대 Git에 커밋하지 마세요!

### 6. 데이터베이스 스키마 적용

Supabase 대시보드의 **SQL Editor**에서 `sql/schema.sql` 파일의 내용을 실행하세요.

주요 작업:
- pgvector 확장 활성화 (Supabase Extensions에서)
- 테이블 생성 (profiles, checkins, sermons, prayers, artifacts, extractions, memory_chunks, memory_embeddings 등)
- RLS (Row Level Security) 정책 설정
- RAG 검색 함수 생성

### 7. Storage 버킷 설정 (선택사항)

멀티모달 기능(음성/이미지)을 사용하려면:

```bash
python scripts/setup_storage.py
```

또는 Supabase 대시보드에서 수동으로 버킷 생성:
- `audio-files` (음성 파일용)
- `image-files` (이미지 파일용)

### 8. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

---

## ⚙️ 환경 설정

### Supabase 설정

1. **프로젝트 생성**: [Supabase](https://supabase.com)에서 새 프로젝트 생성
2. **API 키 확인**: Settings → API에서 URL과 anon key 복사
3. **pgvector 확장**: Database → Extensions에서 `vector` 확장 활성화
4. **스키마 적용**: SQL Editor에서 `sql/schema.sql` 실행

### OpenAI 설정

1. **API 키 발급**: [OpenAI Platform](https://platform.openai.com)에서 API 키 생성
2. **사용 모델**:
   - GPT-4: 구조화된 데이터 추출, 리포트 생성
   - text-embedding-3-small: 벡터 임베딩 (RAG)
   - whisper-1: 음성 전사
   - gpt-4-vision-preview: 이미지 분석

### Google Calendar 설정 (선택사항)

1. **Google Cloud 프로젝트 생성**
2. **Calendar API 활성화**
3. **OAuth 2.0 클라이언트 ID 생성** (웹 애플리케이션)
4. **승인된 리디렉션 URI**에 `http://localhost:8501` 추가
5. **클라이언트 ID/Secret**을 `secrets.toml`에 입력

---

## 📖 주요 기능 상세

### 1. 오늘의 기록 (Check-in)

**기능**:
- 영적 컨디션 선택 (great/good/neutral/bad/terrible)
- 영적 에너지 레벨 (1-10)
- 텍스트/음성/이미지 멀티모달 입력
- AI 기반 구조화 (tasks, obstacles, insights 추출)
- 자동 인덱싱 옵션 (RAG 검색용)

**사용 흐름**:
1. 영적 컨디션 및 에너지 선택
2. 텍스트 입력 또는 멀티모달 파일 업로드
3. AI 구조화 옵션 선택 (LLM 기반 또는 규칙 기반)
4. 저장 시 자동 인덱싱 (설정 ON 시)

### 2. 기억검색 (Memory)

**기능**:
- 자연어 질문으로 과거 기록 검색
- 벡터 유사도 기반 검색
- 검색 결과 소스 표시
- AI가 컨텍스트를 참조하여 답변 생성

**예시 질문**:
- "내가 자주 감사한 내용은?"
- "지난달 방해요인은 무엇이었나?"
- "설교 적용 관련 기록 찾아줘"

### 3. 주간 성장 리포트

**기능**:
- 주간 체크인 데이터 분석
- 감사/방해요인/결단/적용 패턴 분석
- 기분 트렌드 분석
- 다음 주 제안 생성

**생성 항목**:
- 한 줄 요약
- 이번 주 성취
- 어려웠던 점
- 발견된 패턴
- 다음 주 제안

### 4. 설교노트

**기능**:
- 주일 설교 요약 확인
- 설교 본문 및 설교자 정보
- 나의 적용 작성 및 저장
- 설교별 적용 이력 관리

### 5. 기도노트

**기능**:
- 기도제목 등록 (제목, 내용, 태그)
- 기도 상태 관리 (기도 중/응답됨/진행 중)
- 응답 기록 및 통계
- 카테고리별 필터링

---

## 🗄️ 데이터베이스

### 주요 테이블

| 테이블 | 설명 |
|--------|------|
| `profiles` | 사용자 프로필 및 설정 |
| `checkins` | 일일 신앙 기록 |
| `sermons` | 설교 정보 (관리자 등록) |
| `sermon_applications` | 교인별 설교 적용 |
| `prayers` | 기도제목 |
| `artifacts` | 멀티모달 첨부파일 (음성/이미지) |
| `extractions` | AI 추출 데이터 (구조화) |
| `memory_chunks` | RAG용 텍스트 청크 |
| `memory_embeddings` | 벡터 임베딩 (pgvector) |
| `ai_logs` | AI 호출 로그 |
| `feedback` | 피드백 수집 (파일럿) |

### RLS (Row Level Security)

모든 테이블에 RLS가 적용되어 사용자는 자신의 데이터만 접근할 수 있습니다.

### 벡터 검색

`memory_embeddings` 테이블의 `embedding` 컬럼에 pgvector를 사용하여 의미 기반 검색을 수행합니다.

---

## 🗺️ 개발 로드맵

### ✅ 완료된 기능

- [x] **Step 0**: 프로젝트 부팅 및 기본 구조
- [x] **Step 1**: Supabase 연결 + 스키마 설계
- [x] **Step 2**: 체크인 입력 (텍스트)
- [x] **Step 3**: 멀티모달 입력 (이미지/음성)
- [x] **Step 4**: RAG 기반 회고 (기억검색)
- [x] **Step 5**: 주간 리포트
- [x] **Step 6**: 설교노트 및 기도노트
- [x] **Step 7**: Google Calendar 연동
- [x] **Step 8**: 사용자 인증 시스템

### 🚧 진행 중 / 개선 예정

- [ ] **성능 최적화**: 벡터 검색 인덱스 튜닝
- [ ] **UI/UX 개선**: 모바일 반응형 디자인
- [ ] **알림 기능**: 기도 응답 알림, 주간 리포트 리마인더
- [ ] **데이터 내보내기**: PDF 리포트 생성, 데이터 백업
- [ ] **공동체 기능**: 기도제목 공유, 설교 토론

---

## 🔧 문제 해결

### 일반적인 오류

#### 1. Supabase 연결 실패

**증상**: "Supabase 연결 설정이 필요합니다" 오류

**해결**:
- `.streamlit/secrets.toml` 파일 확인
- Supabase URL과 anon key가 올바른지 확인
- Supabase 프로젝트가 활성 상태인지 확인

#### 2. OpenAI API 오류

**증상**: "OpenAI API 키가 설정되지 않았습니다" 오류

**해결**:
- `secrets.toml`에 `[openai]` 섹션 확인
- API 키가 유효한지 확인 (OpenAI Platform에서)
- 사용량 한도 확인

#### 3. 벡터 검색 실패

**증상**: "검색 결과가 없습니다" 또는 오류 발생

**해결**:
- pgvector 확장이 활성화되었는지 확인
- `memory_embeddings` 테이블에 데이터가 있는지 확인
- Memory 페이지에서 "체크인 동기화" 실행

#### 4. 음성 전사 실패

**증상**: 음성 파일 업로드 후 전사 실패

**해결**:
- 지원 형식 확인 (MP3, WAV, M4A 등)
- 파일 크기 확인 (25MB 이하 권장)
- OpenAI Whisper API 상태 확인

#### 5. 이미지 분석 실패

**증상**: 이미지 업로드 후 분석 실패

**해결**:
- 지원 형식 확인 (PNG, JPG, JPEG, WebP)
- 파일 크기 확인 (20MB 이하 권장)
- OpenAI Vision API 사용량 확인

### 디버깅 모드

`secrets.toml`에서 디버그 모드 활성화:

```toml
[app]
debug = true
```

터미널에서 상세한 오류 로그를 확인할 수 있습니다.

---

## 📝 라이선스

이 프로젝트는 개인/교회 내부 사용을 목적으로 합니다.

---

## 👥 기여

파일럿 100명 대상으로 테스트 중입니다. 피드백은 Settings 페이지의 피드백 기능을 통해 제출해주세요.

---

## 📞 문의

문제가 발생하거나 제안사항이 있으시면 이슈를 등록해주세요.

---

**Made with ❤️ using Streamlit**

*"하나님의 말씀을 묵상하며 작은 실천을 지속하는 신앙의 루프를 만들어가세요."* ✝️
