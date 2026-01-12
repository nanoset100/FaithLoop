"""
믿음루프(FaithLoop) - 기도노트
기도제목 등록, 관리, 응답 기록
"""
import streamlit as st

st.set_page_config(page_title="기도노트 - 믿음루프", page_icon="🙏", layout="wide")

# 로그인 체크
if "user" not in st.session_state or st.session_state.get("user") is None:
    st.warning("🔐 로그인이 필요합니다. 메인 페이지에서 로그인하세요.")
    st.stop()

user_id = st.session_state["user"].id

st.title("🙏 기도노트")
st.caption("기도제목을 기록하고 응답을 추적하세요")

# 태그 옵션
TAG_OPTIONS = ["가족", "건강", "사역", "직장", "감사", "중보", "회개", "기타"]

try:
    from lib.supabase_db import (
        create_prayer, list_prayers, update_prayer, 
        mark_prayer_answered, delete_prayer, get_prayer_stats
    )
    
    # === 통계 ===
    stats = get_prayer_stats(user_id)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("전체 기도", stats["total"])
    with col2:
        st.metric("기도 중", stats["praying"])
    with col3:
        st.metric("응답됨", stats["answered"])
    
    st.divider()
    
    # === 탭 구성 ===
    tab1, tab2, tab3 = st.tabs(["✍️ 새 기도", "🙏 기도 중", "✅ 응답된 기도"])
    
    # === 탭1: 새 기도 등록 ===
    with tab1:
        with st.form("prayer_form", clear_on_submit=True):
            title = st.text_input("기도제목 *", placeholder="예: 가족의 건강을 위해")
            content = st.text_area(
                "상세 내용",
                height=100,
                placeholder="구체적인 기도 내용을 적어보세요..."
            )
            tags = st.multiselect("태그", TAG_OPTIONS)
            
            if st.form_submit_button("🙏 기도 등록", type="primary", use_container_width=True):
                if title.strip():
                    result = create_prayer(user_id, title, content, tags)
                    if result:
                        st.success("✅ 기도제목이 등록되었습니다!")
                        st.rerun()
                    else:
                        st.error("등록 중 오류가 발생했습니다.")
                else:
                    st.warning("기도제목을 입력해주세요.")
    
    # === 탭2: 기도 중 ===
    with tab2:
        prayers = list_prayers(user_id, status="praying")
        
        if prayers:
            for prayer in prayers:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**{prayer['title']}**")
                        if prayer.get("content"):
                            st.caption(prayer["content"][:100] + "..." if len(prayer.get("content", "")) > 100 else prayer.get("content", ""))
                        if prayer.get("tags"):
                            st.caption(" ".join([f"`{tag}`" for tag in prayer["tags"]]))
                        st.caption(f"📅 {prayer['created_at'][:10]}")
                    
                    with col2:
                        if st.button("✅ 응답", key=f"ans_{prayer['id']}", use_container_width=True):
                            st.session_state[f"answering_{prayer['id']}"] = True
                            st.rerun()
                    
                    # 응답 기록 폼
                    if st.session_state.get(f"answering_{prayer['id']}"):
                        with st.form(f"answer_form_{prayer['id']}"):
                            answer_note = st.text_area("응답 내용", placeholder="하나님께서 어떻게 응답하셨나요?")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("저장", type="primary"):
                                    mark_prayer_answered(prayer["id"], answer_note)
                                    del st.session_state[f"answering_{prayer['id']}"]
                                    st.rerun()
                            with col2:
                                if st.form_submit_button("취소"):
                                    del st.session_state[f"answering_{prayer['id']}"]
                                    st.rerun()
                    
                    st.divider()
        else:
            st.info("기도 중인 제목이 없습니다. 새 기도를 등록해보세요!")
    
    # === 탭3: 응답된 기도 ===
    with tab3:
        answered = list_prayers(user_id, status="answered")
        
        if answered:
            for prayer in answered:
                with st.container():
                    st.markdown(f"**✅ {prayer['title']}**")
                    if prayer.get("answer_note"):
                        st.success(f"💬 {prayer['answer_note']}")
                    st.caption(f"기도 시작: {prayer['created_at'][:10]} → 응답: {prayer.get('answered_at', '')[:10] if prayer.get('answered_at') else '-'}")
                    st.divider()
        else:
            st.info("아직 응답된 기도가 없습니다. 하나님의 응답을 기대하며 기도해보세요! 🙏")

except ImportError as e:
    st.warning("⚠️ DB 연결을 확인해주세요.")
    st.code(str(e))
except Exception as e:
    st.error(f"오류: {e}")

# === 푸터 ===
st.divider()
st.caption("쉬지 말고 기도하라 (데살로니가전서 5:17) 🙏")
