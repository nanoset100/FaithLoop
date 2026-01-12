import streamlit as st

st.set_page_config(
    page_title="믿음루프(FaithLoop)",
    page_icon="✝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 로그인 상태 체크
# ============================================

def show_login_page():
    """로그인/회원가입 페이지"""
    st.title("✝️ 믿음루프(FaithLoop)")
    st.caption("AI+RAG 신앙일기로 결단·기도·적용을 누적하고, 근거 기반으로 나를 돌아보며 작은 실천을 지속합니다.")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    # === 로그인 ===
    with col1:
        st.subheader("🔐 로그인")
        with st.form("login_form"):
            email = st.text_input("이메일", placeholder="example@email.com")
            password = st.text_input("비밀번호", type="password")
            
            if st.form_submit_button("로그인", type="primary", use_container_width=True):
                if email and password:
                    from lib.supabase_db import sign_in
                    user, session = sign_in(email, password)
                    if user:
                        st.session_state["user"] = user
                        st.session_state["user_id"] = user.id
                        st.success("✅ 로그인 성공!")
                        st.rerun()
                    else:
                        st.error("❌ 이메일 또는 비밀번호가 올바르지 않습니다.")
                else:
                    st.warning("이메일과 비밀번호를 입력하세요.")
    
    # === 회원가입 ===
    with col2:
        st.subheader("📝 회원가입")
        with st.form("signup_form"):
            new_email = st.text_input("이메일", placeholder="example@email.com", key="signup_email")
            new_password = st.text_input("비밀번호 (6자 이상)", type="password", key="signup_pw")
            new_password2 = st.text_input("비밀번호 확인", type="password", key="signup_pw2")
            display_name = st.text_input("이름 (선택)", placeholder="홍길동")
            
            if st.form_submit_button("회원가입", type="primary", use_container_width=True):
                if not new_email or not new_password:
                    st.warning("이메일과 비밀번호를 입력하세요.")
                elif new_password != new_password2:
                    st.error("비밀번호가 일치하지 않습니다.")
                elif len(new_password) < 6:
                    st.error("비밀번호는 6자 이상이어야 합니다.")
                else:
                    from lib.supabase_db import sign_up
                    user, error = sign_up(new_email, new_password, display_name)
                    if user:
                        st.success("✅ 회원가입 성공! 왼쪽에서 로그인하세요.")
                    else:
                        st.error(f"❌ 회원가입 실패: {error}")
    
    st.divider()
    st.caption("처음 오셨나요? 오른쪽에서 회원가입 후, 왼쪽에서 로그인하세요.")


def show_main_app():
    """메인 앱 (로그인 후)"""
    user = st.session_state.get("user")
    
    # 사이드바에 사용자 정보 표시
    with st.sidebar:
        st.markdown("---")
        st.caption(f"👤 {user.email}")
        if st.button("🚪 로그아웃", use_container_width=True):
            from lib.supabase_db import sign_out
            sign_out()
            st.session_state.clear()
            st.rerun()
    
    # 메인 콘텐츠
    st.title("✝️ 믿음루프(FaithLoop)에 오신 것을 환영합니다")
    st.caption("AI+RAG 신앙일기로 결단·기도·적용을 누적하고, 근거 기반으로 나를 돌아보며 작은 실천을 지속합니다.")
    
    st.divider()
    
    st.subheader("🚀 시작하기")
    st.write("왼쪽 사이드바에서 원하는 기능을 선택하세요:")
    
    st.markdown("""
| 페이지 | 설명 |
|--------|------|
| 🏠 Home | 대시보드 - 최근 신앙 기록 확인 |
| 📖 설교노트 | 주일 설교 요약 확인 및 적용 작성 |
| ✍️ 오늘의 기록 | 감사/말씀/적용 체크인 |
| 🙏 기도노트 | 기도제목 등록 및 응답 추적 |
| 📊 주간 성장 리포트 | AI 기반 주간 신앙 성장 분석 |
| 🧠 기억검색 | 내 기록 기반 RAG 검색 |
| ⚙️ Settings | 연동 및 설정 |
""")
    
    st.divider()
    st.info("💡 **Tip:** 매일 짧은 감사/말씀 체크인으로 시작하세요!")
    
    st.divider()
    st.caption("이 앱은 목회상담/의료를 대체하지 않으며, 기록 기반 성찰과 루틴 형성을 돕습니다.")
    st.caption("Made with ❤️ using Streamlit")


# ============================================
# 메인 로직
# ============================================

if "user" not in st.session_state or st.session_state.get("user") is None:
    show_login_page()
else:
    show_main_app()
