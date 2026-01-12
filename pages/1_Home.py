"""
믿음루프(FaithLoop) - Home (대시보드)
최근 신앙 기록 목록 및 요약 표시
Step 9: Google Calendar 일정 표시
"""
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Home - 믿음루프", page_icon="🏠", layout="wide")

# 로그인 체크
if "user" not in st.session_state or st.session_state.get("user") is None:
    st.warning("🔐 로그인이 필요합니다. 메인 페이지에서 로그인하세요.")
    st.stop()

user_id = st.session_state["user"].id

st.title("🏠 Home")
st.caption("최근 신앙 기록과 오늘의 은혜를 확인하세요")

# === 사이드바: 데모 데이터 제외 토글 ===
with st.sidebar:
    exclude_demo = st.checkbox(
        "🧪 데모 데이터 제외",
        value=st.session_state.get("exclude_demo", True)
    )
    st.session_state["exclude_demo"] = exclude_demo

# === 오늘의 캘린더 일정 (Step 9) ===
try:
    from lib.calendar_google import is_authenticated, get_today_events
    
    if is_authenticated():
        with st.container():
            st.subheader("📅 오늘 일정")
            
            events = get_today_events()
            if events:
                for event in events[:5]:
                    start = event.get("start_time", "")
                    if "T" in start:
                        start_time = start.split("T")[1][:5]
                    else:
                        start_time = "종일"
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"**{start_time}**")
                    with col2:
                        st.markdown(event.get("title", ""))
                
                if len(events) > 5:
                    st.caption(f"외 {len(events) - 5}개 일정...")
            else:
                st.info("오늘 일정이 없습니다 📭")
        
        st.divider()
except:
    pass  # Google Calendar 미연결 시 무시

# === Supabase 연결 상태 체크 ===
try:
    from lib.config import get_supabase_client
    from lib.supabase_db import list_checkins
    
    supabase = get_supabase_client()
    
    if supabase:
        st.success("✅ Supabase 연결됨")
        
        # 최근 체크인 목록 가져오기
        st.subheader("📝 최근 신앙 기록")
        
        checkins = list_checkins(limit=10, exclude_demo=st.session_state.get("exclude_demo", True))
        
        if checkins:
            for checkin in checkins:
                with st.container():
                    # 날짜 포맷팅
                    created_at = checkin.get("created_at", "")
                    if created_at:
                        try:
                            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                            date_str = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            date_str = created_at[:16]
                    else:
                        date_str = "날짜 없음"
                    
                    # 영적 컨디션 이모지 매핑
                    mood_emoji = {
                        "great": "🙏",
                        "good": "✨", 
                        "neutral": "📖",
                        "bad": "🌧️",
                        "terrible": "😢"
                    }.get(checkin.get("mood", ""), "✝️")
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"### {mood_emoji}")
                        st.caption(date_str)
                    with col2:
                        st.markdown(checkin.get("content", "*내용 없음*"))
                        
                        # 태그가 있으면 표시
                        tags = checkin.get("tags", [])
                        if tags:
                            st.caption(" ".join([f"`{tag}`" for tag in tags]))
        else:
            st.info("아직 신앙 기록이 없습니다. **오늘의 기록** 페이지에서 감사/기도/말씀을 남겨보세요!")
            
    else:
        st.warning("⚠️ Supabase 연결 설정이 필요합니다")
        
except ImportError as e:
    st.warning("⚠️ Supabase 모듈 로드 중... (lib/config.py, lib/supabase_db.py 필요)")
    st.code(str(e))
    
    # 데모 데이터로 UI 미리보기
    st.subheader("📝 최근 신앙 기록 (데모)")
    
    demo_checkins = [
        {"mood": "great", "content": "오늘 예배에서 큰 은혜를 받았다. 하나님께 감사드린다.", "date": "2024-01-15 09:30"},
        {"mood": "good", "content": "새벽기도 참석. 말씀 묵상 중 '두려워하지 말라'는 구절이 마음에 와닿았다.", "date": "2024-01-14 08:00"},
        {"mood": "neutral", "content": "바쁜 하루였지만 잠시 기도하며 마음을 정돈했다.", "date": "2024-01-13 18:00"},
    ]
    
    for item in demo_checkins:
        with st.container():
            mood_emoji = {"great": "🙏", "good": "✨", "neutral": "📖"}.get(item["mood"], "✝️")
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"### {mood_emoji}")
                st.caption(item["date"])
            with col2:
                st.markdown(item["content"])

except Exception as e:
    st.error(f"오류 발생: {e}")

# === 오늘의 요약 섹션 ===
st.divider()
st.subheader("📊 오늘의 신앙 요약")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="감사/기도 기록", value="0회", delta="목표: 1회")
    
with col2:
    st.metric(label="말씀 묵상", value="0회", delta="오늘의 적용")
    
with col3:
    st.metric(label="연속 기록", value="0일", delta="꾸준히 성장 중")

# === 퀵 액션 ===
st.divider()
st.subheader("⚡ 빠른 시작")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📖 설교노트", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Sermon.py")

with col2:
    if st.button("✍️ 오늘의 기록", use_container_width=True):
        st.switch_page("pages/3_Checkin.py")
        
with col3:
    if st.button("🙏 기도노트", use_container_width=True):
        st.switch_page("pages/4_Prayer.py")
        
with col4:
    if st.button("🧠 기억검색", use_container_width=True):
        st.switch_page("pages/6_Memory.py")

# === 안전 문구 ===
st.divider()
st.caption("이 앱은 목회상담/의료를 대체하지 않으며, 기록 기반 성찰과 루틴 형성을 돕습니다.")