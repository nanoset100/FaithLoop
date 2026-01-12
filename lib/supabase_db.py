"""
ReflectOS - Supabase DB CRUD 헬퍼
각 테이블별 기본 CRUD 함수 제공
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
import streamlit as st
from lib.config import get_supabase_client, get_current_user_id
from lib.utils import has_demo_tag


# ============================================
# 공통 헬퍼
# ============================================

def _get_client():
    """Supabase 클라이언트 가져오기 (내부 헬퍼)"""
    client = get_supabase_client()
    if not client:
        raise Exception("Supabase 클라이언트가 초기화되지 않았습니다.")
    return client


def _get_user_id():
    """현재 사용자 ID (내부 헬퍼)"""
    return get_current_user_id()


# ============================================
# profiles 테이블
# ============================================

def get_profile(user_id: str = None) -> Optional[Dict]:
    """사용자 프로필 조회"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        response = client.table("profiles").select("*").eq("user_id", user_id).single().execute()
        return response.data
    except Exception as e:
        # 프로필이 없으면 None 반환
        return None


def upsert_profile(profile_data: Dict, user_id: str = None) -> Dict:
    """
    프로필 생성 또는 업데이트 (upsert)
    profile_data: {display_name, timezone, settings 등}
    """
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "updated_at": datetime.utcnow().isoformat(),
            **profile_data
        }
        
        response = client.table("profiles").upsert(data, on_conflict="user_id").execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"프로필 저장 실패: {e}")
        return None


# ============================================
# checkins 테이블
# ============================================

def insert_checkin(
    content: str,
    mood: str = "neutral",
    tags: List[str] = None,
    metadata: Dict = None,
    user_id: str = None,
    created_at: Optional[str] = None  # 데모 데이터용 옵션 인자
) -> Optional[Dict]:
    """
    새 체크인 저장
    
    Args:
        content: 체크인 내용 (텍스트)
        mood: 기분 (great/good/neutral/bad/terrible)
        tags: 태그 목록 (리스트)
        metadata: 추가 메타데이터 (energy 등)
        user_id: 사용자 ID (기본값: 현재 사용자)
        created_at: 생성 시간 (옵션, 없으면 현재 시간)
    
    Returns:
        저장된 체크인 레코드
    """
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "content": content,
            "mood": mood,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": created_at if created_at else datetime.utcnow().isoformat()
        }
        
        response = client.table("checkins").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"체크인 저장 실패: {e}")
        return None


def list_checkins(
    limit: int = 10,
    offset: int = 0,
    user_id: str = None,
    exclude_demo: bool = False
) -> List[Dict]:
    """
    체크인 목록 조회 (최신순)
    
    Args:
        limit: 가져올 개수
        offset: 건너뛸 개수 (페이지네이션)
        user_id: 사용자 ID
        exclude_demo: True면 데모 데이터 제외
    
    Returns:
        체크인 레코드 목록
    """
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        response = (
            client.table("checkins")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        
        rows = response.data or []
        if exclude_demo:
            rows = [c for c in rows if not has_demo_tag(c.get("tags", []))]
        return rows
    except Exception as e:
        st.error(f"체크인 목록 조회 실패: {e}")
        return []


def get_checkin(checkin_id: str) -> Optional[Dict]:
    """특정 체크인 조회"""
    try:
        client = _get_client()
        response = client.table("checkins").select("*").eq("id", checkin_id).single().execute()
        return response.data
    except Exception as e:
        return None


def delete_checkin(checkin_id: str) -> bool:
    """체크인 삭제"""
    try:
        client = _get_client()
        client.table("checkins").delete().eq("id", checkin_id).execute()
        return True
    except Exception as e:
        st.error(f"체크인 삭제 실패: {e}")
        return False


# ============================================
# extractions 테이블 (AI 추출 데이터)
# ============================================

def insert_extraction(
    source_type: str,
    source_id: str,
    extraction_type: str,
    data: Dict,
    user_id: str = None,
    created_at: Optional[str] = None  # 데모 데이터용 옵션 인자
) -> Optional[Dict]:
    """
    추출 데이터 저장 (규칙 기반 또는 LLM 기반)
    
    Args:
        source_type: 소스 타입 ('checkin', 'artifact', 'calendar')
        source_id: 소스 레코드 ID
        extraction_type: 추출 타입 ('rule_based', 'llm_extractor', 'keywords' 등)
        data: 추출된 데이터 (JSON)
        user_id: 사용자 ID
        created_at: 생성 시간 (옵션, 없으면 현재 시간)
    
    Returns:
        저장된 extraction 레코드
    """
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        record = {
            "user_id": user_id,
            "source_type": source_type,
            "source_id": source_id,
            "extraction_type": extraction_type,
            "data": data,
            "created_at": created_at if created_at else datetime.utcnow().isoformat()
        }
        
        response = client.table("extractions").insert(record).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Extraction 저장 실패: {e}")
        return None


def get_extractions_by_source(source_type: str, source_id: str) -> List[Dict]:
    """특정 소스의 모든 extraction 조회"""
    try:
        client = _get_client()
        response = (
            client.table("extractions")
            .select("*")
            .eq("source_type", source_type)
            .eq("source_id", source_id)
            .execute()
        )
        return response.data or []
    except Exception as e:
        return []


# ============================================
# artifacts 테이블 (멀티모달 첨부파일)
# ============================================

def insert_artifact(
    checkin_id: str,
    artifact_type: str,  # "image", "audio", "file"
    storage_path: str,
    metadata: Dict = None,
    original_name: str = None,
    file_size: int = None,
    user_id: str = None
) -> Optional[Dict]:
    """
    아티팩트(첨부파일) 저장
    
    Args:
        checkin_id: 연결된 체크인 ID
        artifact_type: 파일 타입 ("image", "audio", "file")
        storage_path: Supabase Storage 경로
        metadata: 추가 메타데이터 (전사 텍스트, 분석 결과 등)
        original_name: 원본 파일명
        file_size: 파일 크기 (bytes)
        user_id: 사용자 ID
    
    Returns:
        저장된 artifact 레코드
    """
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "checkin_id": checkin_id,
            "type": artifact_type,
            "storage_path": storage_path,
            "original_name": original_name,
            "file_size": file_size,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = client.table("artifacts").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"아티팩트 저장 실패: {e}")
        return None


def list_artifacts_by_checkin(checkin_id: str) -> List[Dict]:
    """특정 체크인의 아티팩트 목록"""
    try:
        client = _get_client()
        response = (
            client.table("artifacts")
            .select("*")
            .eq("checkin_id", checkin_id)
            .execute()
        )
        return response.data or []
    except Exception as e:
        return []


# ============================================
# plans 테이블 (일간 플랜)
# ============================================

def upsert_plan(
    plan_date: str,  # "YYYY-MM-DD"
    plan_data: Dict = None,
    user_id: str = None
) -> Optional[Dict]:
    """일간 플랜 생성/업데이트"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "plan_date": plan_date,
            "updated_at": datetime.utcnow().isoformat(),
            **(plan_data or {})
        }
        
        response = client.table("plans").upsert(
            data, 
            on_conflict="user_id,plan_date"
        ).execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"플랜 저장 실패: {e}")
        return None


def get_plan(plan_date: str, user_id: str = None) -> Optional[Dict]:
    """특정 날짜 플랜 조회"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        response = (
            client.table("plans")
            .select("*, plan_blocks(*)")
            .eq("user_id", user_id)
            .eq("plan_date", plan_date)
            .single()
            .execute()
        )
        return response.data
    except Exception as e:
        return None


# ============================================
# plan_blocks 테이블 (시간 블록)
# ============================================

def insert_plan_block(
    plan_id: str,
    start_time: str,  # "HH:MM"
    end_time: str,
    title: str,
    category: str = None,
    user_id: str = None
) -> Optional[Dict]:
    """시간 블록 추가"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "plan_id": plan_id,
            "start_time": start_time,
            "end_time": end_time,
            "title": title,
            "category": category,
            "is_completed": False
        }
        
        response = client.table("plan_blocks").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"블록 저장 실패: {e}")
        return None


# ============================================
# memory_chunks 테이블 (RAG용)
# ============================================

def insert_memory_chunk(
    source_type: str,  # "checkin", "note", "calendar"
    source_id: str,
    content: str,
    user_id: str = None
) -> Optional[Dict]:
    """메모리 청크 저장 (RAG 색인용)"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "source_type": source_type,
            "source_id": source_id,
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = client.table("memory_chunks").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"메모리 청크 저장 실패: {e}")
        return None


# ============================================
# 통계/집계 쿼리
# ============================================

def count_checkins_today(user_id: str = None) -> int:
    """오늘 체크인 횟수"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        today = datetime.utcnow().date().isoformat()
        
        response = (
            client.table("checkins")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .gte("created_at", f"{today}T00:00:00")
            .lte("created_at", f"{today}T23:59:59")
            .execute()
        )
        
        return response.count or 0
    except Exception as e:
        return 0


def get_checkins_date_range(
    start_date: str,
    end_date: str,
    user_id: str = None,
    exclude_demo: bool = False
) -> List[Dict]:
    """날짜 범위의 체크인 조회"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        response = (
            client.table("checkins")
            .select("*")
            .eq("user_id", user_id)
            .gte("created_at", f"{start_date}T00:00:00")
            .lte("created_at", f"{end_date}T23:59:59")
            .order("created_at", desc=True)
            .execute()
        )
        
        rows = response.data or []
        if exclude_demo:
            rows = [c for c in rows if not has_demo_tag(c.get("tags", []))]
        return rows
    except Exception as e:
        return []


# ============================================
# FaithLoop 파일럿 - 프로필 함수
# ============================================

def get_user_profile(user_id: str) -> dict | None:
    """사용자 프로필 조회"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        result = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[get_user_profile] Error: {e}")
        return None


def create_user_profile(user_id: str, email: str, display_name: str, role: str = "member", invite_code: str = None) -> dict | None:
    """사용자 프로필 생성"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        data = {
            "user_id": user_id,
            "email": email,
            "display_name": display_name,
            "role": role,
            "invite_code_used": invite_code
        }
        
        result = supabase.table("profiles").insert(data).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[create_user_profile] Error: {e}")
        return None


def is_admin(user_id: str) -> bool:
    """관리자 여부 확인"""
    profile = get_user_profile(user_id)
    if profile:
        return profile.get("role") == "admin"
    return False


def validate_invite_code(code: str) -> dict | None:
    """초대코드 유효성 검증"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        result = supabase.table("invite_codes").select("*").eq("code", code).eq("is_active", True).execute()
        
        if result.data and len(result.data) > 0:
            invite = result.data[0]
            if invite.get("max_uses") and invite.get("current_uses", 0) >= invite["max_uses"]:
                return None
            return invite
        return None
    except Exception as e:
        print(f"[validate_invite_code] Error: {e}")
        return None


# ============================================
# FaithLoop 파일럿 - 설교 함수
# ============================================

def create_sermon(title: str, sermon_date: str, scripture: str, preacher: str, 
                  summary: str, application_question: str, created_by: str = None) -> dict | None:
    """설교 생성 (관리자용)"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        data = {
            "title": title,
            "sermon_date": sermon_date,
            "scripture": scripture,
            "preacher": preacher,
            "summary": summary,
            "application_question": application_question,
            "status": "draft"
        }
        
        if created_by:
            data["created_by"] = created_by
        
        result = supabase.table("sermons").insert(data).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[create_sermon] Error: {e}")
        return None


def update_sermon(sermon_id: str, **kwargs) -> dict | None:
    """설교 수정 (관리자용)"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        result = supabase.table("sermons").update(kwargs).eq("id", sermon_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[update_sermon] Error: {e}")
        return None


def publish_sermon(sermon_id: str) -> dict | None:
    """설교 배포 (관리자용)"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        from datetime import datetime
        result = supabase.table("sermons").update({
            "status": "published",
            "published_at": datetime.now().isoformat()
        }).eq("id", sermon_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[publish_sermon] Error: {e}")
        return None


def unpublish_sermon(sermon_id: str) -> dict | None:
    """설교 배포 취소 (관리자용)"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        result = supabase.table("sermons").update({
            "status": "draft",
            "published_at": None
        }).eq("id", sermon_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[unpublish_sermon] Error: {e}")
        return None


def delete_sermon(sermon_id: str) -> bool:
    """설교 삭제 (관리자용)"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False
        
        supabase.table("sermons").delete().eq("id", sermon_id).execute()
        return True
    except Exception as e:
        print(f"[delete_sermon] Error: {e}")
        return False


def list_sermons_admin() -> list:
    """모든 설교 목록 (관리자용)"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return []
        
        result = supabase.table("sermons").select("*").order("sermon_date", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"[list_sermons_admin] Error: {e}")
        return []


def list_sermons_published() -> list:
    """배포된 설교 목록 (교인용)"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return []
        
        result = supabase.table("sermons").select("*").eq("status", "published").order("sermon_date", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"[list_sermons_published] Error: {e}")
        return []


def get_sermon(sermon_id: str) -> dict | None:
    """설교 상세 조회"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        result = supabase.table("sermons").select("*").eq("id", sermon_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[get_sermon] Error: {e}")
        return None


def get_latest_sermon() -> dict | None:
    """최신 배포 설교 조회"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        result = supabase.table("sermons").select("*").eq("status", "published").order("sermon_date", desc=True).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[get_latest_sermon] Error: {e}")
        return None


def save_sermon_application(sermon_id: str, user_id: str, my_application: str) -> dict | None:
    """교인 적용 저장"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        data = {
            "sermon_id": sermon_id,
            "user_id": user_id,
            "my_application": my_application
        }
        
        result = supabase.table("sermon_applications").upsert(data, on_conflict="sermon_id,user_id").execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[save_sermon_application] Error: {e}")
        return None


def get_sermon_application(sermon_id: str, user_id: str) -> dict | None:
    """교인 적용 조회"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        result = supabase.table("sermon_applications").select("*").eq("sermon_id", sermon_id).eq("user_id", user_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[get_sermon_application] Error: {e}")
        return None


# ============================================
# FaithLoop 파일럿 - 기도노트 함수
# ============================================

def create_prayer(user_id: str, title: str, content: str = None, tags: list = None) -> dict | None:
    """기도제목 생성"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        data = {
            "user_id": user_id,
            "title": title,
            "content": content,
            "tags": tags or [],
            "status": "praying"
        }
        
        result = supabase.table("prayers").insert(data).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[create_prayer] Error: {e}")
        return None


def update_prayer(prayer_id: str, **kwargs) -> dict | None:
    """기도제목 수정"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        result = supabase.table("prayers").update(kwargs).eq("id", prayer_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[update_prayer] Error: {e}")
        return None


def mark_prayer_answered(prayer_id: str, answer_note: str = None) -> dict | None:
    """기도 응답 처리"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        from datetime import datetime
        result = supabase.table("prayers").update({
            "status": "answered",
            "answer_note": answer_note,
            "answered_at": datetime.now().isoformat()
        }).eq("id", prayer_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[mark_prayer_answered] Error: {e}")
        return None


def delete_prayer(prayer_id: str) -> bool:
    """기도제목 삭제"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False
        
        supabase.table("prayers").delete().eq("id", prayer_id).execute()
        return True
    except Exception as e:
        print(f"[delete_prayer] Error: {e}")
        return False


def list_prayers(user_id: str, status: str = None, tag: str = None) -> list:
    """기도제목 목록 조회"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return []
        
        query = supabase.table("prayers").select("*").eq("user_id", user_id)
        
        if status:
            query = query.eq("status", status)
        
        if tag:
            query = query.contains("tags", [tag])
        
        result = query.order("created_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"[list_prayers] Error: {e}")
        return []


def get_prayer_stats(user_id: str) -> dict:
    """기도 통계"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return {"total": 0, "praying": 0, "answered": 0}
        
        result = supabase.table("prayers").select("status").eq("user_id", user_id).execute()
        
        if result.data:
            total = len(result.data)
            praying = len([p for p in result.data if p["status"] == "praying"])
            answered = len([p for p in result.data if p["status"] == "answered"])
            return {"total": total, "praying": praying, "answered": answered}
        
        return {"total": 0, "praying": 0, "answered": 0}
    except Exception as e:
        print(f"[get_prayer_stats] Error: {e}")
        return {"total": 0, "praying": 0, "answered": 0}


# ============================================
# Auth 함수
# ============================================

def sign_up(email: str, password: str, display_name: str = None):
    """회원가입"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None, "DB 연결 실패"
        
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "display_name": display_name or email.split("@")[0]
                }
            }
        })
        
        if response.user:
            return response.user, None
        return None, "회원가입 실패"
    except Exception as e:
        return None, str(e)


def sign_in(email: str, password: str):
    """로그인"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None, "DB 연결 실패"
        
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            return response.user, response.session
        return None, None
    except Exception as e:
        print(f"[sign_in] Error: {e}")
        return None, None


def sign_out():
    """로그아웃"""
    try:
        supabase = get_supabase_client()
        if supabase:
            supabase.auth.sign_out()
        return True
    except Exception as e:
        print(f"[sign_out] Error: {e}")
        return False


def get_current_user():
    """현재 로그인된 사용자 조회"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        response = supabase.auth.get_user()
        if response:
            return response.user
        return None
    except:
        return None