"""
믿음루프(FaithLoop) - 주간 성장 리포트
주간 신앙 성장 분석
Step 7: RAG 기반 주간 분석 + 감사/방해요인/결단/적용
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional

st.set_page_config(page_title="주간 성장 리포트 - 믿음루프", page_icon="📊", layout="wide")

# 로그인 체크
if "user" not in st.session_state or st.session_state.get("user") is None:
    st.warning("🔐 로그인이 필요합니다. 메인 페이지에서 로그인하세요.")
    st.stop()

user_id = st.session_state["user"].id

st.title("📊 주간 성장 리포트")
st.caption("AI가 생성하는 주간 신앙 성장 분석 (근거 기반)")

# === 사이드바: 데모 데이터 제외 토글 ===
with st.sidebar:
    exclude_demo = st.checkbox(
        "🧪 데모 데이터 제외",
        value=st.session_state.get("exclude_demo", True)
    )
    st.session_state["exclude_demo"] = exclude_demo


# === 주간 리포트 생성 함수 ===
def generate_weekly_report_json(checkins: List[Dict], extractions: List[Dict]) -> Optional[Dict]:
    """
    주간 데이터를 분석하여 구조화된 리포트 생성
    
    Returns:
        {
            "summary": "한 줄 요약",
            "wins": ["성취1", "성취2", ...],
            "issues": ["문제1", "문제2", ...],
            "patterns": ["패턴1", "패턴2", ...],
            "next_experiments": ["제안1", "제안2", ...],
            "mood_analysis": {"average": "good", "trend": "stable"},
            "stats": {"total_checkins": 7, "total_tasks": 12, ...}
        }
    """
    from lib.openai_client import chat_completion_json
    
    # 체크인 데이터 요약
    checkin_summaries = []
    mood_counts = {"great": 0, "good": 0, "neutral": 0, "bad": 0, "terrible": 0}
    all_tasks = []
    all_obstacles = []
    
    for c in checkins:
        date = c.get("created_at", "")[:10]
        mood = c.get("mood", "neutral")
        content = c.get("content", "")[:300]
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
        checkin_summaries.append(f"[{date}] 기분:{mood}\n{content}")
    
    for e in extractions:
        data = e.get("data", {})
        all_tasks.extend(data.get("tasks", []))
        all_obstacles.extend(data.get("obstacles", []))
    
    combined_text = "\n---\n".join(checkin_summaries)
    
    # JSON 스키마 정의 (FaithLoop 성장 리포트)
    report_schema = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "이번 주 핵심 주제"
            },
            "wins": {
                "type": "array",
                "items": {"type": "string"},
                "description": "감사 하이라이트 (최대 5개)"
            },
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "반복 방해요인(패턴) (최대 5개)"
            },
            "patterns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "결단/적용 진행 상황 (최대 3개)"
            },
            "next_experiments": {
                "type": "array",
                "items": {"type": "string"},
                "description": "다음 주 작은 실천 3가지"
            }
        },
        "required": ["summary", "wins", "issues", "patterns", "next_experiments"],
        "additionalProperties": False
    }
    
    system_prompt = """당신은 신앙 성장 코치입니다. 
한 주간의 신앙 기록(감사/기도/말씀/적용/방해요인)을 분석하여 의미 있는 성장 리포트를 생성합니다.

분석 원칙:
1. 감사 기록에서 하이라이트를 찾아 wins에 기록
2. 반복되는 방해요인(분주함/유혹/감정)을 issues에 기록
3. 결단/적용이 실제로 지켜졌는지를 patterns에 기록
4. 다음 주 작은 실천(말씀묵상/기도/공동체)을 next_experiments에 제안

말투: 따뜻하고 격려하며, 기록 근거를 제시"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""이번 주 체크인 기록을 분석해주세요:

{combined_text}

추출된 할 일: {', '.join(all_tasks[:10]) if all_tasks else '없음'}
추출된 어려움: {', '.join(all_obstacles[:5]) if all_obstacles else '없음'}
"""}
    ]
    
    result = chat_completion_json(messages, report_schema, temperature=0.7)
    
    if result:
        # 통계 추가
        result["stats"] = {
            "total_checkins": len(checkins),
            "total_tasks": len(all_tasks),
            "total_obstacles": len(all_obstacles),
            "mood_distribution": mood_counts
        }
        
        # 평균 무드 계산
        mood_scores = {"great": 5, "good": 4, "neutral": 3, "bad": 2, "terrible": 1}
        total_score = sum(mood_counts[m] * mood_scores[m] for m in mood_counts)
        total_count = sum(mood_counts.values())
        
        if total_count > 0:
            avg_score = total_score / total_count
            avg_mood = "great" if avg_score >= 4.5 else "good" if avg_score >= 3.5 else "neutral" if avg_score >= 2.5 else "bad" if avg_score >= 1.5 else "terrible"
            result["mood_analysis"] = {
                "average": avg_mood,
                "average_score": round(avg_score, 2)
            }
    
    return result


# === 주간 선택 ===
st.subheader("📅 기간 선택")

# 이번 주 월요일 계산
today = datetime.now().date()
this_monday = today - timedelta(days=today.weekday())
last_monday = this_monday - timedelta(days=7)

# 빠른 선택 버튼 (먼저 배치하여 session_state 수정)
st.caption("빠른 선택:")
bcol1, bcol2, bcol3 = st.columns(3)

# 버튼 상태 체크 (위젯 생성 전에 처리)
this_week_clicked = bcol1.button("이번 주", use_container_width=True, key="btn_this_week")
last_week_clicked = bcol2.button("지난 주", use_container_width=True, key="btn_last_week")
last_2weeks_clicked = bcol3.button("지난 2주", use_container_width=True, key="btn_last_2weeks")

# 버튼에 따라 기본값 결정
if this_week_clicked:
    default_start = this_monday
    default_end = this_monday + timedelta(days=6)
elif last_week_clicked:
    default_start = last_monday
    default_end = last_monday + timedelta(days=6)
elif last_2weeks_clicked:
    default_start = last_monday - timedelta(days=7)
    default_end = last_monday + timedelta(days=6)
else:
    # session_state 또는 기본값 사용
    default_start = st.session_state.get("rpt_start", this_monday)
    default_end = st.session_state.get("rpt_end", this_monday + timedelta(days=6))

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "시작일",
        value=default_start,
        help="주의 시작일 (보통 월요일)"
    )
with col2:
    end_date = st.date_input(
        "종료일",
        value=default_end,
        help="주의 종료일 (보통 일요일)"
    )

# 현재 선택된 날짜 저장
st.session_state.rpt_start = start_date
st.session_state.rpt_end = end_date


# === 리포트 생성 ===
if st.button("📝 리포트 생성", use_container_width=True, type="primary"):
    with st.spinner("📊 주간 데이터를 분석 중..."):
        try:
            from lib.supabase_db import get_checkins_date_range
            from lib.config import get_supabase_client, get_current_user_id
            
            client = get_supabase_client()
            user_id = get_current_user_id()
            
            # 체크인 조회
            checkins = get_checkins_date_range(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                exclude_demo=st.session_state.get("exclude_demo", True)
            )
            
            if not checkins:
                st.warning(f"⚠️ {start_date} ~ {end_date} 기간에 체크인 기록이 없습니다.")
            else:
                # extractions 조회
                checkin_ids = [c["id"] for c in checkins]
                extractions = []
                
                for cid in checkin_ids:
                    try:
                        ext_response = client.table("extractions").select("*").eq("source_id", cid).execute()
                        if ext_response.data:
                            extractions.extend(ext_response.data)
                    except:
                        pass
                
                # 리포트 생성
                report = generate_weekly_report_json(checkins, extractions)
                
                if report:
                    st.session_state.weekly_report = report
                    st.session_state.report_checkins = checkins
                    st.success("✅ 리포트 생성 완료!")
                else:
                    st.error("리포트 생성에 실패했습니다.")
                    
        except ImportError as e:
            st.error(f"모듈 로드 실패: {e}")
        except Exception as e:
            st.error(f"오류 발생: {e}")


st.divider()

# === 리포트 표시 ===
if st.session_state.get("weekly_report"):
    report = st.session_state.weekly_report
    checkins = st.session_state.get("report_checkins", [])
    
    st.subheader(f"📋 주간 성장 리포트")
    st.caption(f"{start_date} ~ {end_date}")
    
    # 요약
    st.markdown(f"### 💬 이번 주 핵심 주제")
    st.info(report.get("summary", ""))
    
    # 통계 카드
    stats = report.get("stats", {})
    mood_analysis = report.get("mood_analysis", {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 체크인", f"{stats.get('total_checkins', 0)}회")
    with col2:
        st.metric("완료한 일", f"{stats.get('total_tasks', 0)}개")
    with col3:
        mood_emoji = {"great": "😊", "good": "🙂", "neutral": "😐", "bad": "😔", "terrible": "😢"}
        avg_mood = mood_analysis.get("average", "neutral")
        st.metric("평균 기분", mood_emoji.get(avg_mood, "😐"))
    with col4:
        st.metric("어려움", f"{stats.get('total_obstacles', 0)}개")
    
    st.divider()
    
    # 4분면 표시
    col1, col2 = st.columns(2)
    
    with col1:
        # Wins (감사 하이라이트)
        with st.container():
            st.markdown("### 🙏 감사 하이라이트")
            wins = report.get("wins", [])
            if wins:
                for i, win in enumerate(wins, 1):
                    st.markdown(f"{i}. {win}")
            else:
                st.caption("기록된 감사가 없습니다")
        
        # Patterns (결단/적용 진행 상황)
        with st.container():
            st.markdown("### ✅ 결단/적용 진행 상황")
            patterns = report.get("patterns", [])
            if patterns:
                for pattern in patterns:
                    st.markdown(f"• {pattern}")
            else:
                st.caption("결단/적용 기록이 없습니다")
    
    with col2:
        # Issues (반복 방해요인)
        with st.container():
            st.markdown("### ⚠️ 반복 방해요인(패턴)")
            issues = report.get("issues", [])
            if issues:
                for i, issue in enumerate(issues, 1):
                    st.markdown(f"{i}. {issue}")
            else:
                st.caption("기록된 방해요인이 없습니다")
        
        # Next Experiments (다음 주 작은 실천)
        with st.container():
            st.markdown("### 🚀 다음 주 작은 실천 3가지")
            experiments = report.get("next_experiments", [])
            if experiments:
                for exp in experiments:
                    st.checkbox(exp, key=f"exp_{exp[:20]}")
            else:
                st.caption("제안 사항이 없습니다")
    
    # 영적 컨디션 분포 차트
    st.divider()
    st.markdown("### 📊 영적 컨디션 분포")
    
    mood_dist = stats.get("mood_distribution", {})
    if any(mood_dist.values()):
        import pandas as pd
        
        mood_data = {
            "컨디션": ["🙏 평안/감사", "✨ 은혜로움", "📖 보통", "🌧️ 분주/낙심", "😢 힘든 하루"],
            "횟수": [
                mood_dist.get("great", 0),
                mood_dist.get("good", 0),
                mood_dist.get("neutral", 0),
                mood_dist.get("bad", 0),
                mood_dist.get("terrible", 0)
            ]
        }
        df = pd.DataFrame(mood_data)
        st.bar_chart(df.set_index("컨디션"))
    
    # 원문 보기 (소스 링크) - 근거 표시
    st.divider()
    with st.expander("📖 원문 신앙 기록 보기 (근거)"):
        for checkin in checkins:
            with st.container():
                date = checkin.get("created_at", "")[:10]
                mood = checkin.get("mood", "neutral")
                mood_emoji = {"great": "🙏", "good": "✨", "neutral": "📖", "bad": "🌧️", "terrible": "😢"}
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown(f"### {mood_emoji.get(mood, '📝')}")
                    st.caption(date)
                with col2:
                    st.markdown(checkin.get("content", "")[:200] + "...")
                    tags = checkin.get("tags", [])
                    if tags:
                        st.caption(" ".join([f"`{t}`" for t in tags]))

else:
    # 리포트가 없을 때 템플릿 표시
    st.subheader("📋 리포트 미리보기")
    st.caption("위에서 기간을 선택하고 '리포트 생성' 버튼을 클릭하세요")
    
    with st.container():
        st.markdown("""
        ## 주간 성장 리포트 예시
        
        ---
        
        ### 💬 이번 주 핵심 주제
        > 감사와 기도를 통해 평안을 회복해가는 한 주였습니다.
        
        ---
        
        ### 🙏 감사 하이라이트
        1. 가족과 함께한 주일 예배
        2. 어려운 일에서 지혜를 얻음
        3. 새벽기도 3일 연속 참석
        
        ### ⚠️ 반복 방해요인(패턴)
        1. SNS에 시간을 많이 뺏김
        2. 바쁜 일정으로 기도 시간 부족
        
        ### ✅ 결단/적용 진행 상황
        • "두려워하지 말라" 말씀 적용 → 면접에서 담대히 말함
        • 저녁 묵상 습관 시작
        
        ### 🚀 다음 주 작은 실천 3가지
        - [ ] 매일 감사 1가지 기록
        - [ ] 새벽기도 2회 참석
        - [ ] 공동체 모임 참여
        """)
