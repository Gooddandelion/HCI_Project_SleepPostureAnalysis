"""
=====================================================
 backend/utils/db.py
 Supabase 연동 모듈
 - Storage 이미지 업로드 / 공개 URL 반환
 - posture_log 저장 / 조회
 - condition_log 저장 / 조회

 사용법:
     from utils.db import insert_posture, fetch_posture_by_date
=====================================================
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 경로에 추가
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import TABLE_POSTURE_LOG, TABLE_CONDITION

# .env 로드
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / ".env")
except ImportError:
    pass  # python-dotenv 없으면 환경변수 직접 설정

from supabase import create_client, Client


# ── Supabase 클라이언트 초기화 ─────────────────────
def get_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise EnvironmentError(
            ".env 파일에 SUPABASE_URL과 SUPABASE_KEY를 설정해주세요\n"
            ".env.example 파일을 참고하세요"
        )
    return create_client(url, key)


# ── Storage: 이미지 업로드 ─────────────────────────
STORAGE_BUCKET = "sleep-images"   # Supabase Storage 버킷 이름


def upload_image(local_path: str) -> str:
    """
    로컬 이미지를 Supabase Storage에 업로드하고 공개 URL을 반환합니다.

    Storage 경로 구조:
        sleep-images/
          └── YYYYMMDD/
                └── {timestamp}_{type}_color.png

    반환:
        업로드 성공 → 공개 URL (str)
        업로드 실패 → 로컬 경로 (str) — DB에는 저장되지만 웹에서 이미지 불러오기 불가

    사전 준비 (최초 1회):
        Supabase 대시보드 → Storage → New bucket
        이름: sleep-images / Public: ON
    """
    supabase   = get_client()
    local_path = Path(local_path)

    if not local_path.exists():
        print(f"[Storage] 파일 없음: {local_path}")
        return str(local_path)

    # Storage 경로: YYYYMMDD/파일명
    date_folder   = local_path.parent.name   # ex) 20250510
    storage_path  = f"{date_folder}/{local_path.name}"

    try:
        with open(local_path, "rb") as f:
            supabase.storage.from_(STORAGE_BUCKET).upload(
                path=storage_path,
                file=f,
                file_options={
                    "content-type": "image/png",
                    "upsert": "true",   # 같은 파일명이면 덮어쓰기
                }
            )

        # 공개 URL 반환
        public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(
            storage_path
        )
        print(f"[Storage] ✅ 업로드 완료 → {public_url}")
        return public_url

    except Exception as e:
        print(f"[Storage] ❌ 업로드 실패 ({e}) → 로컬 경로로 저장")
        return str(local_path)


def upload_image_pair(color_path: str, depth_path: str) -> tuple[str, str]:
    """
    RGB + 뎁스 이미지를 동시에 업로드하고 각각의 공개 URL을 반환합니다.
    반환: (color_url, depth_url)
    """
    color_url = upload_image(color_path)
    depth_url = upload_image(depth_path)
    return color_url, depth_url


def get_image_url(storage_path: str) -> str:
    """
    Storage 경로로 공개 URL 조회 (업로드 없이 URL만 필요할 때)
    storage_path: ex) "20250510/1746000000_regular_color.png"
    """
    supabase = get_client()
    return supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)


# ── posture_log ────────────────────────────────────
def insert_posture(timestamp: int, posture: str, angle: float,
                   capture_type: str, image_path: str,
                   upload: bool = True) -> dict:
    """
    자세 분류 결과를 Supabase posture_log 테이블에 저장

    image_path: 로컬 이미지 경로
    upload:     True  → Storage에 자동 업로드 후 공개 URL을 DB에 저장
                False → 로컬 경로를 그대로 DB에 저장 (오프라인/테스트용)

    반환: 저장된 row (dict)
    """
    supabase = get_client()
    dt_str   = datetime.fromtimestamp(timestamp).isoformat()

    # 이미지 Storage 업로드
    if upload and image_path and Path(image_path).exists():
        stored_path = upload_image(image_path)
    else:
        stored_path = image_path   # 로컬 경로 그대로 저장

    row = {
        "timestamp":    timestamp,
        "datetime":     dt_str,
        "posture":      posture,
        "angle":        round(float(angle), 2),
        "capture_type": capture_type,
        "image_path":   stored_path,   # 공개 URL or 로컬 경로
    }
    result = supabase.table(TABLE_POSTURE_LOG).insert(row).execute()
    return result.data[0] if result.data else {}


def fetch_posture_by_date(target_date: str) -> list[dict]:
    """
    특정 날짜의 자세 로그 전체 조회
    target_date: "YYYY-MM-DD" 형식
    반환: [{id, timestamp, posture, ...}, ...]
    """
    supabase = get_client()
    start    = f"{target_date}T00:00:00"
    end      = f"{target_date}T23:59:59"

    result = (
        supabase.table(TABLE_POSTURE_LOG)
        .select("*")
        .gte("datetime", start)
        .lte("datetime", end)
        .order("datetime", desc=False)
        .execute()
    )
    return result.data or []


def fetch_posture_latest(limit: int = 100) -> list[dict]:
    """최근 N개 자세 로그 조회"""
    supabase = get_client()
    result   = (
        supabase.table(TABLE_POSTURE_LOG)
        .select("*")
        .order("datetime", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


# ── condition_log ──────────────────────────────────
def insert_condition(log_date: str, refresh_level: int,
                     pain_neck: bool, pain_shoulder: bool,
                     pain_back: bool, memo: str = "") -> dict:
    """
    기상 후 컨디션을 Supabase morning_conditions 테이블에 저장
    log_date: "YYYY-MM-DD" 형식
    refresh_level: 1(최악) ~ 5(최고)

    실제 DB 컬럼명:
        date / refreshment / pain_neck / pain_shoulder / pain_back
    """
    supabase = get_client()
    row = {
        "user_id":      "demo",          # 데모용 고정값 (추후 인증 연동 시 수정)
        "date":         log_date,        # log_date → date
        "refreshment":  refresh_level,   # refresh_level → refreshment
        "pain_neck":    pain_neck,
        "pain_shoulder":pain_shoulder,
        "pain_back":    pain_back,
    }
    # upsert: 같은 날짜면 덮어쓰기
    result = (
        supabase.table(TABLE_CONDITION)
        .upsert(row, on_conflict="date")
        .execute()
    )
    return result.data[0] if result.data else {}


def fetch_condition_by_date(log_date: str) -> dict:
    """특정 날짜 컨디션 조회"""
    supabase = get_client()
    result   = (
        supabase.table(TABLE_CONDITION)
        .select("*")
        .eq("date", log_date)        # log_date → date
        .execute()
    )
    return result.data[0] if result.data else {}


def fetch_condition_all() -> list[dict]:
    """전체 컨디션 로그 조회 (최신순)"""
    supabase = get_client()
    result   = (
        supabase.table(TABLE_CONDITION)
        .select("*")
        .order("date", desc=True)    # log_date → date
        .execute()
    )
    return result.data or []


# ── 연결 테스트 ────────────────────────────────────
def test_connection() -> bool:
    """Supabase 연결 확인용"""
    try:
        supabase = get_client()
        supabase.table(TABLE_POSTURE_LOG).select("id").limit(1).execute()
        print("[Supabase] ✅ 연결 성공")
        return True
    except Exception as e:
        print(f"[Supabase] ❌ 연결 실패: {e}")
        return False


if __name__ == "__main__":
    test_connection()