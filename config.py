"""
=====================================================
 sleep_project/config.py
 프로젝트 전체 공통 설정
 backend / frontend 모두 이 파일 기준으로 동작
=====================================================
"""

from pathlib import Path
from datetime import datetime

# ── 경로 ──────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
FRAMES_DIR    = BASE_DIR / "backend" / "sleep_frames"
TIMELAPSE_DIR = BASE_DIR / "backend" / "timelapse"

TODAY     = datetime.now().strftime("%Y%m%d")
TODAY_DIR = FRAMES_DIR / TODAY

# ── 촬영 설정 ──────────────────────────────────────
INTERVAL_SEC     = 60     # 정기 촬영 간격 (초) | 테스트: 5
MOTION_THRESHOLD = 30     # 움직임 감지 임계값  | 어두운 환경: 40~50
SHOW_PREVIEW     = True

# ── 타임랩스 설정 ──────────────────────────────────
TIMELAPSE_FPS    = 10
TIMELAPSE_WIDTH  = 1280
TIMELAPSE_HEIGHT = 720

# ── 자세 분류 설정 ─────────────────────────────────
LATERAL_ANGLE_THRESHOLD = 45

POSTURE_SUPINE    = "Supine"
POSTURE_PRONE     = "Prone"
POSTURE_LATERAL_L = "Lateral_L"
POSTURE_LATERAL_R = "Lateral_R"
POSTURE_UNKNOWN   = "Unknown"

POSTURE_LIST = [
    POSTURE_SUPINE,
    POSTURE_LATERAL_L,
    POSTURE_LATERAL_R,
    POSTURE_PRONE,
    POSTURE_UNKNOWN,
]

POSTURE_COLOR_BGR = {
    POSTURE_SUPINE:    (100, 220, 100),
    POSTURE_LATERAL_L: (50,  180, 255),
    POSTURE_LATERAL_R: (200, 120, 255),
    POSTURE_PRONE:     (80,   80, 255),
    POSTURE_UNKNOWN:   (160, 160, 160),
}

POSTURE_COLOR_HEX = {
    POSTURE_SUPINE:    "#5BBF72",
    POSTURE_LATERAL_L: "#F4A742",
    POSTURE_LATERAL_R: "#E07BB5",
    POSTURE_PRONE:     "#5B8EBF",
    POSTURE_UNKNOWN:   "#AAAAAA",
}

# ── Kinect 관절 인덱스 ─────────────────────────────
JOINT_INDEX = {
    "NOSE":           3,
    "HIP_RIGHT":      4,
    "SHOULDER_RIGHT": 12,
    "HIP_LEFT":       18,
    "SHOULDER_LEFT":  26,
}

# ── Supabase 테이블명 ──────────────────────────────
# shared/supabase_schema.sql 과 반드시 일치시킬 것
TABLE_POSTURE_LOG  = "posture_log"         # 자세 분류 결과
TABLE_CONDITION    = "morning_conditions"  # 기상 후 컨디션 입력


def init_dirs():
    """프로젝트 필수 폴더 자동 생성"""
    for d in [FRAMES_DIR, TIMELAPSE_DIR, TODAY_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    print(f"[config] 폴더 초기화 완료 → {TODAY_DIR.resolve()}")