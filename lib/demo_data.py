"""
믿음루프(FaithLoop) - 데모 데이터 생성
Settings 페이지에서 테스트용 신앙 기록 데이터를 생성/삭제
"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import streamlit as st

# 데모 데이터 구분 태그
DEMO_TAG = "__demo__"


# ============================================
# (1) 규칙 기반 Extraction (Checkin.py 로직 복사)
# ============================================

def extract_by_rules(content: str) -> Dict[str, List[str]]:
    """
    규칙 기반으로 텍스트에서 구조화된 정보 추출
    (pages/2_Checkin.py의 로직과 동일)
    
    Args:
        content: 체크인 내용 텍스트
    
    Returns:
        추출된 정보 딕셔너리
    """
    lines = content.strip().split('\n')
    
    tasks = []
    obstacles = []
    projects = []
    insights = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # task: '-' 또는 '•'로 시작하는 줄
        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
            task_text = line.lstrip('-•* ').strip()
            if task_text:
                tasks.append(task_text)
        
        # obstacle: '!' 시작 또는 부정적 키워드 포함
        obstacle_keywords = ['문제', '어려움', '힘들', '막혀', '안됨', '실패', '오류', '버그']
        if line.startswith('!') or any(kw in line for kw in obstacle_keywords):
            obstacle_text = line.lstrip('! ').strip()
            if obstacle_text and obstacle_text not in obstacles:
                obstacles.append(obstacle_text)
        
        # project: '#프로젝트명' 형태
        project_matches = re.findall(r'#(\w+)', line)
        for proj in project_matches:
            if proj not in projects:
                projects.append(proj)
        
        # insight: 인사이트 키워드 포함
        insight_keywords = ['💡', '인사이트', '배움', '깨달음', '발견', '아이디어']
        if any(kw in line for kw in insight_keywords):
            insight_text = line.strip()
            if insight_text and insight_text not in insights:
                insights.append(insight_text)
    
    return {
        "tasks": tasks,
        "obstacles": obstacles,
        "projects": projects,
        "insights": insights,
        "people": [],
        "emotions": []
    }


# ============================================
# (2) 데모 데이터 항목 생성
# ============================================

def build_demo_items(days: int = 7) -> List[Dict]:
    """
    데모용 신앙 기록 항목 생성
    
    Args:
        days: 생성할 일수 (기본 7일)
    
    Returns:
        신앙 기록 항목 리스트 (과거→현재 순)
    """
    # 신앙 기록 맥락의 데모 콘텐츠 (감사/기도/말씀/적용/방해요인 포함)
    demo_contents = [
        # Day 0 (가장 오래된)
        """1) 오늘 감사:
- 아침에 일찍 일어나 조용히 기도할 수 있었음에 감사
- 가족이 건강한 것에 감사

2) 오늘 기도제목:
- 이번 주 중요한 회의에서 지혜를 달라
- 아내의 건강 회복

3) 말씀/적용:
"두려워하지 말라 내가 너와 함께 함이라" 이사야 41:10
→ 내일 발표에서 담대하게 나아가겠다

4) 방해요인:
- SNS에 시간을 너무 많이 보냄
- 저녁에 피곤해서 기도 시간을 건너뜀""",

        # Day 1
        """1) 오늘 감사:
- 새벽기도회에 참석할 수 있었음
- 동료가 커피를 사줌, 작은 친절에 감사

2) 기도제목:
- 부모님 건강
- 직장에서의 인간관계 지혜

3) 말씀묵상:
빌립보서 4:6-7 "아무 것도 염려하지 말고"
→ 걱정되는 일을 기도로 맡기기로 결단

4) 방해요인:
- 업무가 바빠서 점심 묵상 시간을 놓침
문제: 시간 관리가 잘 안됨""",

        # Day 2
        """1) 감사:
- 주일예배에서 큰 은혜를 받음
- 소그룹 모임에서 좋은 나눔이 있었음
- 날씨가 좋아서 산책하며 기도함

2) 기도:
- 교회 청년부 부흥을 위해
- 선교사님들을 위해

3) 말씀:
"너희는 먼저 그의 나라와 그의 의를 구하라" 마태복음 6:33
💡 인사이트: 우선순위를 바로잡아야겠다

4) 방해요인:
- 주일 오후에 피곤해서 낮잠을 오래 잠""",

        # Day 3
        """1) 감사 1가지:
- 어려운 프로젝트가 잘 마무리됨, 하나님의 도우심에 감사

2) 기도제목:
- 다음 주 시험을 앞둔 조카를 위해
- 교회 봉사 지혜

3) 말씀/적용:
시편 23편 묵상
"여호와는 나의 목자시니 내게 부족함이 없으리로다"
→ 부족함 대신 감사 연습하기로 결단

4) 방해요인:
- 유튜브 영상에 시간을 뺏김
어려움: 디지털 기기 사용 절제가 필요함""",

        # Day 4
        """1) 오늘 감사:
- 아침 말씀 묵상 3일 연속 성공!
- 동네 이웃과 좋은 대화를 나눔

2) 기도제목:
- 겸손한 마음을 달라
- 가정의 평화

3) 말씀묵상:
잠언 3:5-6 "너는 마음을 다하여 여호와를 신뢰하고"
💡 배움: 내 계획보다 하나님의 인도하심을 신뢰해야 함

4) 방해요인:
- 급한 업무로 저녁 기도 시간이 짧았음""",

        # Day 5
        """1) 감사:
- 오랜만에 친구와 좋은 시간을 보냄
- 봉사활동에 참여할 기회가 주어짐

2) 기도:
- 아픈 분들의 회복을 위해
- 나의 인내심을 키워달라

3) 말씀/적용:
"항상 기뻐하라 쉬지 말고 기도하라" 데살로니가전서 5:16-17
→ 짧은 기도라도 자주 하기로 결단

4) 방해요인:
- 부정적인 뉴스에 마음이 흔들림
실패: 걱정이 많아서 잠을 설침""",

        # Day 6 (오늘/어제)
        """1) 오늘 감사:
- 한 주를 건강하게 보낼 수 있었음에 감사
- 교회 소그룹 모임에서 따뜻한 교제
- 말씀 묵상이 꾸준히 이어지고 있음

2) 기도제목:
- 다음 주 계획들이 잘 진행되도록
- 가족의 건강

3) 말씀묵상:
로마서 8:28 "모든 것이 합력하여 선을 이루느니라"
💡 인사이트: 힘든 일도 결국 성장의 기회가 됨

4) 방해요인:
- 주중에 피곤해서 새벽기도 2번 빠짐
해결: 취침 시간을 앞당기기로 결단"""
    ]
    
    moods = ["good", "neutral", "great", "bad", "good", "neutral", "great"]
    
    items = []
    now = datetime.utcnow()
    
    # days개만큼 생성 (과거→현재 순)
    for i in range(min(days, len(demo_contents))):
        # 과거부터 시작 (days-1일 전 ~ 오늘)
        day_offset = days - 1 - i
        target_date = now - timedelta(days=day_offset)
        
        # 시간도 약간씩 다르게 (9시~18시 사이)
        target_date = target_date.replace(
            hour=9 + (i * 2) % 9,
            minute=(i * 13) % 60,
            second=0,
            microsecond=0
        )
        
        items.append({
            "content": demo_contents[i],
            "mood": moods[i % len(moods)],
            "tags": [DEMO_TAG, "감사", "기도", "말씀", "demo"],
            "metadata": {
                "is_demo": True,
                "seed_version": 2,  # FaithLoop 버전
                "day_index": i,
                "energy": 5 + (i % 4)  # 5~8 사이 (영적 에너지)
            },
            "created_at": target_date.isoformat() + "Z"
        })
    
    return items


# ============================================
# (3) 데모 데이터 삭제
# ============================================

def delete_demo_data() -> Dict[str, Any]:
    """
    데모 데이터만 삭제 (tags에 __demo__ 포함된 것)
    
    Returns:
        삭제 결과 딕셔너리
    """
    from lib.config import get_supabase_client, get_current_user_id
    
    result = {
        "deleted_checkins": 0,
        "deleted_extractions": 0,
        "deleted_embeddings": 0,
        "errors": []
    }
    
    try:
        client = get_supabase_client()
        if not client:
            result["errors"].append("Supabase 클라이언트 없음")
            return result
        
        user_id = get_current_user_id()
        
        # 1. 데모 체크인 ID 조회 (tags에 __demo__ 포함)
        demo_checkins = client.table("checkins").select("id").eq(
            "user_id", user_id
        ).contains("tags", [DEMO_TAG]).execute()
        
        demo_ids = [c["id"] for c in (demo_checkins.data or [])]
        
        if not demo_ids:
            return result
        
        # 2. 관련 extractions 삭제
        for checkin_id in demo_ids:
            try:
                client.table("extractions").delete().eq(
                    "source_type", "checkin"
                ).eq("source_id", checkin_id).execute()
                result["deleted_extractions"] += 1
            except Exception as e:
                result["errors"].append(f"extraction 삭제 오류: {e}")
        
        # 3. 관련 memory_embeddings 삭제
        for checkin_id in demo_ids:
            try:
                client.table("memory_embeddings").delete().eq(
                    "source_id", checkin_id
                ).execute()
                result["deleted_embeddings"] += 1
            except Exception as e:
                result["errors"].append(f"embedding 삭제 오류: {e}")
        
        # 4. 관련 memory_chunks 삭제
        for checkin_id in demo_ids:
            try:
                client.table("memory_chunks").delete().eq(
                    "source_id", checkin_id
                ).execute()
            except Exception:
                pass  # memory_chunks는 선택적
        
        # 5. 데모 체크인 삭제
        client.table("checkins").delete().eq(
            "user_id", user_id
        ).contains("tags", [DEMO_TAG]).execute()
        
        result["deleted_checkins"] = len(demo_ids)
        
    except Exception as e:
        result["errors"].append(f"삭제 중 오류: {e}")
    
    return result


# ============================================
# (3) 데모 데이터 시드 (통합 함수)
# ============================================

def seed_demo_data(
    days: int = 7,
    overwrite: bool = False,
    also_index: bool = True
) -> Dict[str, Any]:
    """
    데모 데이터 생성 및 저장
    
    Args:
        days: 생성할 일수
        overwrite: 기존 데모 데이터 삭제 후 재생성
        also_index: RAG 임베딩도 함께 생성
    
    Returns:
        결과 딕셔너리 {deleted_demo_checkins, inserted_checkins, inserted_extractions, indexed, errors}
    """
    from lib.config import get_supabase_client, get_current_user_id
    from lib.supabase_db import insert_checkin, insert_extraction
    from lib.rag import index_checkin, index_extraction
    
    result = {
        "deleted_demo_checkins": 0,
        "inserted_checkins": 0,
        "inserted_extractions": 0,
        "indexed": 0,
        "errors": []
    }
    
    try:
        client = get_supabase_client()
        if not client:
            result["errors"].append("Supabase 클라이언트가 없습니다.")
            return result
        
        user_id = get_current_user_id()
        
        # A) overwrite=True면 기존 데모 데이터 삭제
        if overwrite:
            delete_result = delete_demo_data()
            result["deleted_demo_checkins"] = delete_result.get("deleted_checkins", 0)
            result["errors"].extend(delete_result.get("errors", []))
        
        # B) 데모 항목 생성
        items = build_demo_items(days)
        
        # C) 각 항목 저장
        for item in items:
            try:
                # 1) 체크인 저장
                checkin_data = insert_checkin(
                    content=item["content"],
                    mood=item["mood"],
                    tags=item["tags"],
                    metadata=item["metadata"],
                    created_at=item["created_at"]  # 확장된 인자 사용
                )
                
                if not checkin_data:
                    result["errors"].append(f"체크인 저장 실패: day_index={item['metadata']['day_index']}")
                    continue
                
                result["inserted_checkins"] += 1
                checkin_id = checkin_data.get("id")
                
                # 2) 규칙 기반 추출
                extractions = extract_by_rules(item["content"])
                
                # 3) extraction 저장
                extraction_result = insert_extraction(
                    source_type="checkin",
                    source_id=checkin_id,
                    extraction_type="demo_rule",
                    data=extractions,
                    created_at=item["created_at"]  # 확장된 인자 사용
                )
                
                if extraction_result:
                    result["inserted_extractions"] += 1
                
                # 4) RAG 인덱싱 (also_index=True인 경우)
                if also_index:
                    try:
                        # 체크인 인덱싱
                        if index_checkin(checkin_id, item["content"], extractions):
                            result["indexed"] += 1
                        
                        # extraction 인덱싱
                        index_extraction(checkin_id, "demo_rule", extractions)
                        
                    except Exception as e:
                        result["errors"].append(f"인덱싱 오류: {e}")
                        
            except Exception as e:
                result["errors"].append(f"항목 처리 오류: {e}")
        
    except Exception as e:
        result["errors"].append(f"seed_demo_data 오류: {e}")
    
    return result

