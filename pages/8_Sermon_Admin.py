"""
믿음루프(FaithLoop) - 설교 관리 (관리자 전용)
URL 직접 접근: /_Sermon_Admin
"""
import streamlit as st
from datetime import date

st.set_page_config(page_title="설교 관리 - 믿음루프", page_icon="⚙️", layout="wide")

# 로그인 체크
if "user" not in st.session_state or st.session_state.get("user") is None:
    st.warning("🔐 로그인이 필요합니다.")
    st.stop()

user_id = st.session_state["user"].id

# 관리자 체크 (파일럿에서는 모든 로그인 사용자 허용)
# 나중에 관리자 제한 필요시 아래 주석 해제
# from lib.supabase_db import is_admin
# if not is_admin(user_id):
#     st.error("🚫 관리자만 접근할 수 있습니다.")
#     st.stop()

st.title("⚙️ 설교 관리")
st.caption("설교 요약과 적용 질문을 등록하고 교인들에게 배포합니다")

# === 탭 구성 ===
tab1, tab2 = st.tabs(["📝 새 설교 등록", "📋 설교 목록"])

# === 탭1: 새 설교 등록 ===
with tab1:
    st.subheader("새 설교 등록")
    
    with st.form("sermon_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("설교 제목 *", placeholder="예: 믿음의 본질")
            sermon_date = st.date_input("설교 날짜 *", value=date.today())
        
        with col2:
            scripture = st.text_input("성경 본문", placeholder="예: 히브리서 11:1-6")
            preacher = st.text_input("설교자", placeholder="예: 김목사")
        
        st.divider()
        
        summary = st.text_area(
            "📌 설교 요약 *",
            height=200,
            placeholder="외부에서 작성한 설교 요약을 붙여넣으세요..."
        )
        
        application_question = st.text_area(
            "✍️ 적용 질문 *",
            height=100,
            placeholder="예: 이번 주 내 삶에서 믿음으로 나아갈 영역은 무엇입니까?"
        )
        
        st.divider()
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            save_draft = st.form_submit_button("💾 임시저장", use_container_width=True)
        with col2:
            publish = st.form_submit_button("✅ 배포하기", use_container_width=True, type="primary")
        
        # 폼 제출 처리 (폼 내부)
        if save_draft or publish:
            if not title or not summary or not application_question:
                st.error("필수 항목(*)을 모두 입력해주세요.")
            else:
                try:
                    from lib.supabase_db import create_sermon, publish_sermon
                    
                    sermon = create_sermon(
                        title=title,
                        sermon_date=str(sermon_date),
                        scripture=scripture,
                        preacher=preacher,
                        summary=summary,
                        application_question=application_question
                    )
                    
                    if sermon:
                        if publish:
                            publish_sermon(sermon["id"])
                            st.session_state["sermon_success"] = f"✅ '{title}' 설교가 교인들에게 배포되었습니다!"
                        else:
                            st.session_state["sermon_success"] = f"💾 '{title}' 설교가 임시저장되었습니다."
                    else:
                        st.session_state["sermon_error"] = "저장 중 오류가 발생했습니다."
                except Exception as e:
                    st.session_state["sermon_error"] = f"오류: {e}"
    
    # 성공/에러 메시지 표시 (폼 외부)
    if "sermon_success" in st.session_state:
        st.success(st.session_state["sermon_success"])
        del st.session_state["sermon_success"]
    
    if "sermon_error" in st.session_state:
        st.error(st.session_state["sermon_error"])
        del st.session_state["sermon_error"]


# === 탭2: 설교 목록 ===
with tab2:
    st.subheader("등록된 설교 목록")
    
    try:
        from lib.supabase_db import list_sermons_admin, publish_sermon, unpublish_sermon, delete_sermon
        
        sermons = list_sermons_admin()
        
        if sermons:
            for sermon in sermons:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        status_emoji = "✅" if sermon["status"] == "published" else "📝"
                        status_text = "배포됨" if sermon["status"] == "published" else "초안"
                        st.markdown(f"**{status_emoji} {sermon['title']}** `{status_text}`")
                        st.caption(f"{sermon['sermon_date']} | {sermon.get('scripture', '-')} | {sermon.get('preacher', '-')}")
                    
                    with col2:
                        if sermon["status"] == "published":
                            if st.button("배포취소", key=f"unpub_{sermon['id']}", use_container_width=True):
                                unpublish_sermon(sermon["id"])
                                st.rerun()
                        else:
                            if st.button("배포", key=f"pub_{sermon['id']}", use_container_width=True, type="primary"):
                                publish_sermon(sermon["id"])
                                st.rerun()
                    
                    with col3:
                        if st.button("🗑️", key=f"del_{sermon['id']}", use_container_width=True):
                            delete_sermon(sermon["id"])
                            st.rerun()
                    
                    with st.expander("요약 보기"):
                        st.markdown(sermon.get("summary", ""))
                        st.divider()
                        st.markdown(f"**적용 질문:** {sermon.get('application_question', '')}")
                    
                    st.divider()
        else:
            st.info("등록된 설교가 없습니다. 위에서 새 설교를 등록하세요.")
            
    except ImportError:
        st.warning("DB 연결을 확인해주세요.")
    except Exception as e:
        st.error(f"오류: {e}")
