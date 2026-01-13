import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="개인정보처리방침 - FaithLoop",
    page_icon="🔒",
    layout="wide"
)

# 스타일 추가
st.markdown("""
<style>
    .main {
        max-width: 800px;
        margin: 0 auto;
    }
    .highlight-box {
        background-color: #ecf0f1;
        padding: 15px;
        border-left: 4px solid #3498db;
        margin: 20px 0;
        border-radius: 4px;
    }
    .section-title {
        color: #34495e;
        margin-top: 30px;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    th {
        background-color: #ecf0f1;
        padding: 10px;
        border: 1px solid #ddd;
        text-align: left;
    }
    td {
        padding: 10px;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.title("🔒 FaithLoop 개인정보처리방침")

# 시행일자
st.markdown("""
<div class="highlight-box">
    <strong>시행일자:</strong> 2025년 1월 14일<br>
    <strong>최종 수정일:</strong> 2025년 1월 14일
</div>
""", unsafe_allow_html=True)

# 서론
st.markdown("""
FaithLoop("믿음루프", 이하 "서비스")는 사용자의 개인정보를 매우 중요하게 생각하며, 
「개인정보 보호법」을 준수하고 있습니다. 본 개인정보처리방침은 서비스 이용 과정에서 
수집되는 개인정보의 항목, 이용 목적, 보유 및 이용 기간, 파기 절차 등을 안내합니다.
""")

# 1. 수집하는 개인정보 항목
st.markdown('<h2 class="section-title">📋 1. 수집하는 개인정보 항목</h2>', unsafe_allow_html=True)

st.markdown("### 1.1 필수 수집 정보")
st.markdown("""
- **회원가입 시:** 이메일 주소, 비밀번호(암호화 저장)
- **서비스 이용 시:** 사용자가 작성한 신앙 기록, 설교노트, 기도노트, 리포트 등
""")

st.markdown("### 1.2 선택적 수집 정보")
st.markdown("""
- **멀티모달 입력:** 음성 파일, 이미지 파일 (사용자가 업로드한 경우)
- **Google 연동:** Google Calendar 일정 정보 (사용자가 연동한 경우)
""")

st.markdown("### 1.3 자동 수집 정보")
st.markdown("""
- 서비스 이용 기록 (로그인 시간, 작성 일시 등)
- 기기 정보 (브라우저 종류, OS 버전)
""")

# 2. 개인정보의 수집 및 이용 목적
st.markdown('<h2 class="section-title">🎯 2. 개인정보의 수집 및 이용 목적</h2>', unsafe_allow_html=True)

st.markdown("""
- **회원 관리:** 회원제 서비스 제공, 본인 인증, 회원 식별
- **서비스 제공:** 신앙 기록 저장, AI 분석 및 리포트 생성, 기억검색(RAG) 기능
- **서비스 개선:** 신규 서비스 개발, 통계 분석, 사용자 피드백 반영
- **고객 지원:** 문의사항 응대, 공지사항 전달
""")

# 3. 개인정보의 보유 및 이용 기간
st.markdown('<h2 class="section-title">🔒 3. 개인정보의 보유 및 이용 기간</h2>', unsafe_allow_html=True)

st.markdown("""
- **회원 탈퇴 시:** 즉시 파기 (단, 관련 법령에 따라 보존 의무가 있는 정보는 예외)
- **서비스 이용 기록:** 회원 탈퇴 시까지 보관
- **법령에 따른 보존:**
  - 소비자 불만 또는 분쟁처리 기록: 3년 (전자상거래법)
  - 로그인 기록: 3개월 (통신비밀보호법)
""")

# 4. 개인정보의 제3자 제공 및 처리 위탁
st.markdown('<h2 class="section-title">🤝 4. 개인정보의 제3자 제공 및 처리 위탁</h2>', unsafe_allow_html=True)

st.markdown("### 4.1 제3자 제공")
st.markdown("FaithLoop는 사용자의 개인정보를 외부에 판매하거나 제공하지 않습니다.")

st.markdown("### 4.2 처리 위탁")
st.markdown("서비스 제공을 위해 다음의 제3자 서비스를 이용합니다:")

st.markdown("""
| 수탁업체 | 위탁 업무 내용 | 개인정보 보유기간 |
|---------|--------------|----------------|
| Supabase | 데이터베이스 호스팅, 인증, 파일 저장 | 회원 탈퇴 시까지 |
| OpenAI | AI 분석, 음성 전사, 이미지 분석 | 처리 즉시 삭제 |
| Google | Calendar 연동 (사용자 동의 시) | 연동 해제 시까지 |
""")

st.markdown("""
<div class="highlight-box">
<strong>⚠️ 중요:</strong> OpenAI API를 통해 전송되는 데이터는 분석 목적으로만 사용되며, 
OpenAI의 정책에 따라 모델 학습에 사용되지 않습니다. 
자세한 내용은 <a href="https://openai.com/policies/privacy-policy" target="_blank">OpenAI 개인정보처리방침</a>을 참조하세요.
</div>
""", unsafe_allow_html=True)

# 5. 개인정보의 파기 절차 및 방법
st.markdown('<h2 class="section-title">🛡️ 5. 개인정보의 파기 절차 및 방법</h2>', unsafe_allow_html=True)

st.markdown("""
- **파기 절차:** 회원 탈퇴 요청 시 즉시 파기 (법령 보존 의무 제외)
- **파기 방법:**
  - 전자 파일: 복구 불가능한 방법으로 영구 삭제
  - 종이 문서: 파쇄 또는 소각
""")

# 6. 정보주체의 권리 및 행사 방법
st.markdown('<h2 class="section-title">👤 6. 정보주체의 권리 및 행사 방법</h2>', unsafe_allow_html=True)

st.markdown("""
사용자는 언제든지 다음의 권리를 행사할 수 있습니다:

- **열람 요구:** 서비스 내 Settings 페이지에서 본인 정보 확인
- **정정 요구:** Settings 페이지에서 정보 수정
- **삭제 요구:** 회원 탈퇴를 통한 정보 삭제
- **처리 정지 요구:** 서비스 이용 중지 또는 회원 탈퇴
""")

# 7. 개인정보 보호를 위한 기술적/관리적 대책
st.markdown('<h2 class="section-title">🔐 7. 개인정보 보호를 위한 기술적/관리적 대책</h2>', unsafe_allow_html=True)

st.markdown("### 7.1 기술적 대책")
st.markdown("""
- 비밀번호 암호화 저장 (해시 처리)
- HTTPS 암호화 통신
- Supabase Row Level Security (RLS) 적용
- 정기적인 보안 업데이트
""")

st.markdown("### 7.2 관리적 대책")
st.markdown("""
- 개인정보 접근 권한 최소화
- 개인정보 처리 직원 교육
- 개인정보 보호 책임자 지정
""")

# 8. 개인정보 보호 책임자
st.markdown('<h2 class="section-title">📞 8. 개인정보 보호 책임자</h2>', unsafe_allow_html=True)

st.markdown("""
개인정보 처리에 관한 문의사항이 있으시면 아래로 연락해주세요:

- **책임자:** FaithLoop 운영팀
- **문의:** 서비스 내 Settings > 피드백 기능 이용
""")

# 9. 개인정보처리방침의 변경
st.markdown('<h2 class="section-title">🔄 9. 개인정보처리방침의 변경</h2>', unsafe_allow_html=True)

st.markdown("""
본 개인정보처리방침은 법령 및 서비스 정책 변경에 따라 수정될 수 있으며, 
변경 시 앱 내 공지사항을 통해 최소 7일 전에 안내합니다.
""")

# 10. 분쟁 해결
st.markdown('<h2 class="section-title">⚖️ 10. 분쟁 해결</h2>', unsafe_allow_html=True)

st.markdown("""
개인정보 침해에 대한 신고나 상담이 필요하신 경우:

- **개인정보침해 신고센터:** (국번없이) 118 / privacy.kisa.or.kr
- **대검찰청 사이버수사과:** (국번없이) 1301 / www.spo.go.kr
- **경찰청 사이버안전국:** (국번없이) 182 / cyberbureau.police.go.kr
""")

# 면책 조항
st.markdown("""
<div class="highlight-box">
<strong>⚠️ 면책 조항:</strong> 
FaithLoop는 신앙 성찰 및 기록을 돕는 도구이며, 전문적인 목회상담이나 의료 서비스를 대체하지 않습니다. 
심각한 정신 건강 문제가 있는 경우 전문가의 도움을 받으시기 바랍니다.
</div>
""", unsafe_allow_html=True)

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.9em;">
    <p><strong>시행일자:</strong> 2025년 1월 14일</p>
    <p>© 2025 FaithLoop. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)