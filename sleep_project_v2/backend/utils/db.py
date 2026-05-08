"""
=====================================================
 backend/utils/db.py
 Supabase 연동 모듈
 - posture_log 저장 / 조회
 - condition_log 저장 / 조회
 
 사용법:
     from utils.db import insert_posture, fetch_posture_by_date
=====================================================
"""

import os
import sys
from pathlib import Path
from datetime import datetime, date

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


# ── posture_log ────────────────────────────────────
def insert_posture(timestamp: int, posture: str, angle: float,
                   capture_type: str, image_path: str) -> dict:
    """
    자세 분류 결과를 Supabase posture_log 테이블에 저장

    반환: 저장된 row (dict)
    """
    supabase = get_client()
    dt_str   = datetime.fromtimestamp(timestamp).isoformat()

    row = {
        "timestamp":    timestamp,
        "datetime":     dt_str,
        "posture":      posture,
        "angle":        round(float(angle), 2),
        "capture_type": capture_type,
        "image_path":   image_path,
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
    기상 후 컨디션을 Supabase condition_log 테이블에 저장
    log_date: "YYYY-MM-DD" 형식
    refresh_level: 1(최악) ~ 5(최고)
    """
    supabase = get_client()
    row = {
        "log_date":      log_date,
        "refresh_level": refresh_level,
        "pain_neck":     pain_neck,
        "pain_shoulder": pain_shoulder,
        "pain_back":     pain_back,
        "memo":          memo,
    }
    # upsert: 같은 날짜면 덮어쓰기
    result = (
        supabase.table(TABLE_CONDITION)
        .upsert(row, on_conflict="log_date")
        .execute()
    )
    return result.data[0] if result.data else {}


def fetch_condition_by_date(log_date: str) -> dict:
    """특정 날짜 컨디션 조회"""
    supabase = get_client()
    result   = (
        supabase.table(TABLE_CONDITION)
        .select("*")
        .eq("log_date", log_date)
        .execute()
    )
    return result.data[0] if result.data else {}


def fetch_condition_all() -> list[dict]:
    """전체 컨디션 로그 조회 (최신순)"""
    supabase = get_client()
    result   = (
        supabase.table(TABLE_CONDITION)
        .select("*")
        .order("log_date", desc=True)
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
