"""
믿음루프(FaithLoop) - 설교노트
주일 설교 요약 확인 및 나의 적용 작성
"""
import streamlit as st

st.set_page_config(page_title="설교노트 - 믿음루프", page_icon="📖", layout="wide")

# 로그인 체크
if "user" not in st.session_state or st.session_state.get("user") is None:
    st.warning("🔐 로그인이 필요합니다. 메인 페이지에서 로그인하세요.")
    st.stop()

user_id = st.session_state["user"].id

# 텍스트 영역 가독성 개선 CSS (로그인 체크 이후에 추가)
st.markdown("""
<style>
    /* Streamlit textarea 모든 가능한 셀렉터로 강제 스타일링 */
    textarea,
    .stTextArea textarea,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="textarea"] textarea,
    .stTextArea > div > div > textarea,
    div[data-testid="stTextArea"] > div > div > textarea,
    textarea[aria-label],
    textarea[data-baseweb="textarea-input"] {
        color: #1E1E1E !important;
        background-color: #F8F9FA !important;
        border: 1px solid #DEE2E6 !important;
        font-size: 16px !important;
    }
    
    /* placeholder 색상 */
    textarea::placeholder,
    .stTextArea textarea::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #999999 !important;
        opacity: 1 !important;
    }
    
    /* focus 상태 */
    textarea:focus,
    .stTextArea textarea:focus,
    div[data-testid="stTextArea"] textarea:focus {
        color: #FFFFFF !important;
        background-color: #1E1E1E !important;
        border-color: #666666 !important;
        outline: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📖 설교노트")
st.caption("주일 설교를 묵상하고 삶에 적용해보세요")

try:
    from lib.supabase_db import list_sermons_published, get_sermon, get_latest_sermon, get_sermon_application, save_sermon_application
    
    sermons = list_sermons_published()
    
    if sermons:
        # 설교 선택 (기본: 최신 설교)
        sermon_options = {f"{s['sermon_date']} - {s['title']}": s['id'] for s in sermons}
        selected = st.selectbox(
            "설교 선택",
            options=list(sermon_options.keys()),
            index=0  # 최신 설교 기본 선택
        )
        
        if selected:
            sermon_id = sermon_options[selected]
            sermon = get_sermon(sermon_id)
            
            if sermon:
                st.divider()
                
                # === 설교 정보 ===
                st.markdown(f"## ✝️ {sermon['title']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"📅 {sermon['sermon_date']}")
                with col2:
                    st.caption(f"📜 {sermon.get('scripture', '-')}")
                with col3:
                    st.caption(f"🎤 {sermon.get('preacher', '-')}")
                
                st.divider()
                
                # === 설교 요약 ===
                st.markdown("### 📌 설교 요약")
                st.markdown(sermon.get("summary", ""))
                
                st.divider()
                
                # === 나의 적용 ===
                st.markdown("### ✍️ 나의 적용")
                
                # 적용 질문 표시
                if sermon.get("application_question"):
                    st.info(f"💬 {sermon['application_question']}")
                
                # 기존 적용 불러오기
                existing = get_sermon_application(sermon_id, user_id)
                
                my_application = st.text_area(
                    "이번 주 적용을 작성해보세요",
                    value=existing.get("my_application", "") if existing else "",
                    height=150,
                    placeholder="이번 주 구체적으로 실천할 내용을 적어보세요...",
                    label_visibility="collapsed"
                )
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("💾 저장", type="primary", use_container_width=True):
                        if my_application.strip():
                            result = save_sermon_application(sermon_id, user_id, my_application)
                            if result:
                                st.success("✅ 저장되었습니다!")
                                st.balloons()
                            else:
                                st.error("저장 중 오류가 발생했습니다.")
                        else:
                            st.warning("적용 내용을 입력해주세요.")
    else:
        st.info("📭 아직 등록된 설교가 없습니다.")
        st.caption("관리자가 설교를 등록하면 이곳에서 확인할 수 있습니다.")

except ImportError as e:
    st.warning("⚠️ DB 연결을 확인해주세요.")
    st.code(str(e))
except Exception as e:
    st.error(f"오류: {e}")

# === 푸터 ===
st.divider()
st.caption("말씀을 삶에 적용하며 믿음으로 성장해가요 🌱")
