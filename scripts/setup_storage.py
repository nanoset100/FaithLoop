"""
Supabase Storage Bucket 생성 스크립트
audio-files와 image-files bucket을 생성합니다.

사용법:
    python scripts/setup_storage.py

필수 설정 (.streamlit/secrets.toml 파일):
    SUPABASE_URL = "https://your-project.supabase.co"
    SUPABASE_SERVICE_KEY = "your-service-role-key"
"""
import sys
from pathlib import Path
from typing import Optional
import requests
import toml

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_supabase_config() -> tuple[Optional[str], Optional[str]]:
    """
    .streamlit/secrets.toml 파일에서 Supabase 설정 가져오기
    
    Returns:
        (url, service_key) 튜플
    """
    secrets_path = project_root / ".streamlit" / "secrets.toml"
    
    if not secrets_path.exists():
        print(f"❌ 오류: {secrets_path} 파일이 존재하지 않습니다.")
        return None, None
    
    try:
        secrets = toml.load(secrets_path)
        
        url = secrets.get("SUPABASE_URL")
        service_key = secrets.get("SUPABASE_SERVICE_KEY")
        
        if not url:
            print("❌ 오류: SUPABASE_URL이 .streamlit/secrets.toml 파일에 설정되지 않았습니다.")
            return None, None
        
        if not service_key:
            print("❌ 오류: SUPABASE_SERVICE_KEY가 .streamlit/secrets.toml 파일에 설정되지 않았습니다.")
            return None, None
        
        return url, service_key
        
    except Exception as e:
        print(f"❌ 오류: secrets.toml 파일 읽기 실패: {e}")
        return None, None


def create_bucket(
    url: str,
    service_key: str,
    bucket_name: str,
    public: bool = False,
    file_size_limit: Optional[int] = None,
    allowed_mime_types: Optional[list[str]] = None
) -> bool:
    """
    Supabase Storage bucket 생성
    
    Args:
        url: Supabase 프로젝트 URL
        service_key: Supabase Service Role Key
        bucket_name: 생성할 bucket 이름
        public: Public 접근 허용 여부
        file_size_limit: 파일 크기 제한 (bytes) - 참고용 (API에서 직접 설정 불가)
        allowed_mime_types: 허용할 MIME 타입 리스트 - 참고용 (API에서 직접 설정 불가)
    
    Returns:
        생성 성공 여부
    """
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }
    
    # Storage API endpoint
    storage_url = f"{url}/storage/v1/bucket"
    
    # Supabase Storage API는 기본적으로 name과 public만 지원
    # file_size_limit과 allowed_mime_types는 Supabase 대시보드에서 설정해야 함
    payload = {
        "name": bucket_name,
        "public": public
    }
    
    try:
        response = requests.post(storage_url, headers=headers, json=payload)
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ '{bucket_name}' bucket이 성공적으로 생성되었습니다.")
            
            # 파일 크기 제한 및 MIME 타입 정보 출력 (참고용)
            if file_size_limit:
                limit_mb = file_size_limit // (1024 * 1024)
                print(f"   💡 파일 크기 제한 ({limit_mb}MB)은 Supabase 대시보드에서 설정하세요.")
            if allowed_mime_types:
                print(f"   💡 MIME 타입 제한은 RLS 정책으로 관리하세요.")
            
            return True
        elif response.status_code == 409:
            # 이미 존재하는 경우
            print(f"⚠️  '{bucket_name}' bucket이 이미 존재합니다. 건너뜁니다.")
            return True
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get("message", error_data.get("error", "알 수 없는 오류"))
            except:
                error_msg = response.text or "알 수 없는 오류"
            
            print(f"❌ '{bucket_name}' bucket 생성 실패: {error_msg}")
            print(f"   응답 코드: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ '{bucket_name}' bucket 생성 중 오류 발생: {e}")
        return False


def main():
    """메인 함수"""
    print("=" * 60)
    print("Supabase Storage Bucket 생성 스크립트")
    print("=" * 60)
    print()
    
    # Supabase 설정 가져오기
    url, service_key = get_supabase_config()
    if not url or not service_key:
        sys.exit(1)
    
    print(f"📍 Supabase URL: {url}")
    print()
    
    # Bucket 설정
    buckets = [
        {
            "name": "audio-files",
            "public": True,
            "file_size_limit": 50 * 1024 * 1024,  # 50MB
            "allowed_mime_types": [
                "audio/mpeg",
                "audio/mp3",
                "audio/wav",
                "audio/x-wav",
                "audio/m4a",
                "audio/x-m4a",
                "audio/ogg",
                "audio/webm",
                "audio/flac",
                "audio/x-flac"
            ],
            "description": "음성 파일 저장용 (50MB 제한)"
        },
        {
            "name": "image-files",
            "public": True,
            "file_size_limit": 10 * 1024 * 1024,  # 10MB
            "allowed_mime_types": [
                "image/png",
                "image/jpeg",
                "image/jpg",
                "image/webp",
                "image/gif"
            ],
            "description": "이미지 파일 저장용 (10MB 제한)"
        }
    ]
    
    # Bucket 생성
    success_count = 0
    for bucket_config in buckets:
        print(f"📦 {bucket_config['description']}")
        print(f"   Bucket 이름: {bucket_config['name']}")
        print(f"   Public: {bucket_config['public']}")
        print(f"   파일 크기 제한: {bucket_config['file_size_limit'] // (1024 * 1024)}MB")
        print(f"   허용 MIME 타입: {', '.join(bucket_config['allowed_mime_types'][:3])}...")
        
        success = create_bucket(
            url=url,
            service_key=service_key,
            bucket_name=bucket_config["name"],
            public=bucket_config["public"],
            file_size_limit=bucket_config["file_size_limit"],
            allowed_mime_types=bucket_config["allowed_mime_types"]
        )
        
        if success:
            success_count += 1
        
        print()
    
    # 결과 요약
    print("=" * 60)
    if success_count == len(buckets):
        print(f"✅ 모든 bucket 생성 완료 ({success_count}/{len(buckets)})")
        print()
        print("💡 다음 단계:")
        print("   1. Supabase 대시보드에서 Storage > Policies를 확인하세요")
        print("   2. 필요시 RLS 정책을 추가하세요")
    else:
        print(f"⚠️  일부 bucket 생성 실패 ({success_count}/{len(buckets)})")
        print("   Supabase 대시보드에서 수동으로 확인해주세요")
    print("=" * 60)


if __name__ == "__main__":
    main()
