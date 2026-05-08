"""
=====================================================
 backend/utils/helpers.py
 촬영 / 움직임 감지 / 자세 분류 / 오버레이 공통 함수
 CSV 저장 제거 → Supabase DB로 통일
=====================================================
"""

import cv2
import numpy as np
import time
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import (
    LATERAL_ANGLE_THRESHOLD,
    POSTURE_SUPINE, POSTURE_PRONE,
    POSTURE_LATERAL_L, POSTURE_LATERAL_R, POSTURE_UNKNOWN,
    POSTURE_COLOR_BGR, JOINT_INDEX,
)


# ── 이미지 저장 ────────────────────────────────────
def save_images(save_dir: Path, color_image,
                depth_image, label: str) -> str:
    """
    RGB + 뎁스 이미지 저장
    label: 'regular' or 'motion'
    반환: color 이미지 경로 (str)
    """
    ts         = int(time.time())
    color_path = save_dir / f"{ts}_{label}_color.png"
    depth_path = save_dir / f"{ts}_{label}_depth.png"
    cv2.imwrite(str(color_path), color_image)
    cv2.imwrite(str(depth_path), depth_image)
    return str(color_path)


# ── 뎁스 시각화 ───────────────────────────────────
def depth_to_colormap(depth_image) -> np.ndarray:
    depth_norm = cv2.normalize(
        depth_image, None, 0, 255, cv2.NORM_MINMAX
    ).astype(np.uint8)
    return cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)


# ── 움직임 감지 ───────────────────────────────────
def to_gray(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (21, 21), 0)


def detect_motion(prev_gray: np.ndarray,
                  curr_gray: np.ndarray,
                  threshold: float) -> tuple[bool, float]:
    diff  = cv2.absdiff(prev_gray, curr_gray)
    score = float(np.mean(diff))
    return score > threshold, score


# ── 자세 분류 (룰 기반) ───────────────────────────
def classify_posture(joints: dict) -> tuple[str, float]:
    required = ['SHOULDER_LEFT', 'SHOULDER_RIGHT',
                'HIP_LEFT', 'HIP_RIGHT']
    if not all(k in joints for k in required):
        return POSTURE_UNKNOWN, 0.0

    sl = np.array(joints['SHOULDER_LEFT'])
    sr = np.array(joints['SHOULDER_RIGHT'])
    hl = np.array(joints['HIP_LEFT'])
    hr = np.array(joints['HIP_RIGHT'])

    shoulder_mid = (sl + sr) / 2
    hip_mid      = (hl + hr) / 2
    body_vec     = shoulder_mid - hip_mid

    angle = np.degrees(
        np.arctan2(abs(body_vec[0]), abs(body_vec[1]))
    )

    if angle < LATERAL_ANGLE_THRESHOLD:
        return (POSTURE_LATERAL_L if sl[1] < sr[1]
                else POSTURE_LATERAL_R), angle

    if 'NOSE' in joints:
        face_forward = joints['NOSE'][2] < (sl[2] + sr[2]) / 2
    else:
        face_forward = (sl[2] + sr[2]) / 2 < (hl[2] + hr[2]) / 2

    return (POSTURE_SUPINE if face_forward else POSTURE_PRONE), angle


def extract_joints_from_body(body) -> dict:
    """Kinect body 객체 → 관절 딕셔너리"""
    skel   = body.numpy_joints
    joints = {}
    for name, idx in JOINT_INDEX.items():
        joints[name] = tuple(skel[idx, :3])
    return joints


# ── 미리보기 오버레이 ──────────────────────────────
def draw_overlay(image: np.ndarray, posture: str,
                 next_in: float, regular: int,
                 motion: int, score: float) -> np.ndarray:
    out  = image.copy()
    h, w = out.shape[:2]

    bar = out.copy()
    cv2.rectangle(bar, (0, 0), (w, 75), (0, 0, 0), -1)
    cv2.addWeighted(bar, 0.45, out, 0.55, 0, out)

    col = POSTURE_COLOR_BGR.get(posture, (255, 255, 255))
    cv2.putText(out, f"자세: {posture}",
                (12, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.85, col, 2)
    cv2.putText(out,
                f"다음 정기까지: {int(next_in)}s  "
                f"정기: {regular}  움직임: {motion}",
                (12, 58), cv2.FONT_HERSHEY_SIMPLEX,
                0.58, (200, 200, 200), 1)

    bar_w   = min(int((score / 80) * (w - 20)), w - 20)
    bar_col = (0, 200, 80) if score <= 30 else (0, 80, 255)
    cv2.rectangle(out, (0, h - 10), (bar_w, h), bar_col, -1)
    return out
